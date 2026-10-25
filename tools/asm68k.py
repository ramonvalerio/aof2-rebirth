"""Mini-assembler 68000 para patches (ver ADR-0001).

Não é um assembler completo: cada instrução é escrita como o encoding em hex
junto do texto esperado na desmontagem. O build desmonta o resultado com o
capstone e falha se o texto não bater, o que garante que o código-fonte do
patch (o texto) e os bytes gravados na ROM sejam sempre a mesma coisa.

Só os desvios curtos (Bcc.s / BRA.s / BSR.s) e o salto absoluto JMP.l
são montados com resolução de rótulos.
"""
from dataclasses import dataclass

import capstone

_md = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_M68K_000)

# Opcode (byte alto) dos desvios curtos.
_BRANCH = {
    "bra": 0x60, "bsr": 0x61, "bhi": 0x62, "bls": 0x63, "bcc": 0x64, "bcs": 0x65,
    "bne": 0x66, "beq": 0x67, "bpl": 0x6A, "bmi": 0x6B, "bge": 0x6C, "blt": 0x6D,
    "bgt": 0x6E, "ble": 0x6F,
}


@dataclass
class Label:
    name: str


@dataclass
class Ins:
    hex: str   # encoding, ex.: "302e0068"
    text: str  # desmontagem esperada (formato capstone), ex.: "move.w $68(a6), d0"


@dataclass
class Raw:
    hex: str   # dados (ex.: registros de texto); não passam pela desmontagem


@dataclass
class Branch:
    cond: str   # chave de _BRANCH
    target: str  # nome do rótulo


@dataclass
class LeaPc:
    target: str  # rótulo
    reg: int     # registrador de endereço (a0-a7)


@dataclass
class JmpAbs:
    addr: int   # destino absoluto (jmp $xxxxxx.l)


@dataclass
class JmpNext:
    """Hook encadeado (patchlib.Hook com `chain`): segue para o próximo patch
    do mesmo endereço ou volta ao jogo. O build troca por JmpAbs."""
    hook: int   # endereço do hook


def _size(item):
    if isinstance(item, Label):
        return 0
    if isinstance(item, Ins):
        return len(bytes.fromhex(item.hex))
    if isinstance(item, Branch):
        return 2
    if isinstance(item, (JmpAbs, JmpNext)):
        return 6
    if isinstance(item, Raw):
        return len(bytes.fromhex(item.hex))
    if isinstance(item, LeaPc):
        return 4
    raise TypeError(item)


def size_of(program):
    return sum(_size(i) for i in program)


def assemble(program, origin):
    """Monta `program` no endereço `origin` e devolve os bytes (big-endian)."""
    labels, pc = {}, origin
    for item in program:
        if isinstance(item, Label):
            if item.name in labels:
                raise ValueError(f"rótulo duplicado: {item.name}")
            labels[item.name] = pc
        pc += _size(item)

    out, pc, expected = bytearray(), origin, []
    for item in program:
        if isinstance(item, Ins):
            b = bytes.fromhex(item.hex)
            expected.append((pc, item.text))
        elif isinstance(item, Branch):
            disp = labels[item.target] - (pc + 2)
            if not -128 <= disp <= 127 or disp == 0:
                raise ValueError(f"desvio curto fora de alcance: {item.cond} {item.target}")
            b = bytes([_BRANCH[item.cond], disp & 0xFF])
            expected.append((pc, f"{item.cond}.b ${labels[item.target]:x}"))
        elif isinstance(item, JmpAbs):
            b = bytes.fromhex("4ef9") + item.addr.to_bytes(4, "big")
            expected.append((pc, f"jmp ${item.addr:x}.l"))
        elif isinstance(item, Raw):
            b = bytes.fromhex(item.hex)
        elif isinstance(item, LeaPc):
            disp = labels[item.target] - (pc + 2)
            if not -0x8000 <= disp <= 0x7FFF:
                raise ValueError(f"lea fora de alcance: {item.target}")
            b = (0x41FA | item.reg << 9).to_bytes(2, "big") + (disp & 0xFFFF).to_bytes(2, "big")
            expected.append((pc, f"lea.l ${labels[item.target]:x}(pc), a{item.reg}"))
        else:
            continue
        out += b
        pc += len(b)

    verify(bytes(out), origin, expected)
    return bytes(out)


def label_addr(program, origin, name):
    """Endereço de um rótulo do programa montado em `origin`."""
    pc = origin
    for item in program:
        if isinstance(item, Label) and item.name == name:
            return pc
        pc += _size(item)
    raise KeyError(name)


def disasm(code, origin):
    return [(i.address, f"{i.mnemonic} {i.op_str}".strip(), i.size) for i in _md.disasm(code, origin)]


def verify(code, origin, expected):
    """Confere cada instrução isoladamente (dados `Raw` ficam de fora)."""
    norm = lambda s: " ".join(s.lower().split())
    for addr, text in expected:
        off = addr - origin
        got = next(_md.disasm(code[off:off + 10], addr), None)
        if got is None or norm(text) != norm(f"{got.mnemonic} {got.op_str}"):
            seen = f"{got.mnemonic} {got.op_str}" if got else "nada"
            raise ValueError(f"${addr:06x}: esperado '{text}', capstone leu '{seen}'")
