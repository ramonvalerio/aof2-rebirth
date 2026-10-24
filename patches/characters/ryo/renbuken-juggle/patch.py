"""renbuken-juggle (Ryo) — SPEC-017.

Kyokugen-ryu Renbuken (golpe $021, comando $45):
  - gasta 20% da barra de espírito;
  - recuperação curta depois do 4º hit, para emendar outro golpe
    (ex.: Kohou) no oponente;
  - (pendente) o 4º hit deixa o oponente em juggle, subindo reto: falta
    medir o estado de "acertado no ar" (ver SPEC-017). A v2 usava o efeito
    $0A, mas o estado $1F dele é uma "pegada" (o oponente fica preso ao
    atacante enquanto ele ataca, $1C96A), não um juggle.

O sistema de cancel (v1/v2: Kohou fraco +20% / Zanretsuken +40% no
hitstop do 4º hit) foi retirado a pedido.

Barra: $224(a6) word, byte alto = unidades (é ele que $1D7EC desconta);
máximo em $256(a6) (word, mesmo formato). 20% = máx * 51 / 256.
Custo: $1D7B2 copia o byte 4 do golpe para $241 (descontado em $1D7DE);
o hook troca pelos 20% quando é o Ryo ($62 = 1) e o golpe $10(a5) = $021.

Recuperação: o 4º hit é a animação $121 (último item da sequência em
$2385E), que também é o uppercut. A sequência passa a usar a cópia $11D
(id livre) com a recuperação 5+5+4 -> 2+2+2. As listas de comandos dos
quadros q0/q2/q4 ($52E8C, $52E94, $52E97) vão copiadas no bloco. Opcodes:
$C7 som (2 bytes), $DE (0: encerra os hits extras), $D0 (0); a lista
termina numa peça.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Data, DataBlock, Hook, Patch

RYO = 1
RENBUKEN = 0x021
PCT20 = 51                  # / 256
ANIM_TABLE = 0x050000
NEW_LAST_ANIM = 0x11D
SEQ_LAST = 0x02385E + 6     # 4º item da sequência: $0121

cost = [
    Ins("1d6800040241", "move.b $4(a0), $241(a6)"),   # original
    Ins(f"0c6e{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a6)"),
    Branch("bne", "out"),
    Ins(f"0c6d{RENBUKEN:04x}0010", f"cmpi.w #${RENBUKEN:x}, $10(a5)"),
    Branch("bne", "out"),
    Ins("3f03", "move.w d3, -(a7)"),
    Ins(f"76{PCT20:02x}", f"moveq #${PCT20:x}, d3"),
    Ins("302e0256", "move.w $256(a6), d0"),
    Ins("e048", "lsr.w #$8, d0"),
    Ins("c0c3", "mulu.w d3, d0"),
    Ins("e048", "lsr.w #$8, d0"),
    Ins("361f", "move.w (a7)+, d3"),
    Ins("1d400241", "move.b d0, $241(a6)"),
    Label("out"),
    JmpAbs(0x1D7B8),
]

# Cópia da $121: (duração, flags, peça ou lista de comandos em bytes)
LAST_FRAMES = [
    (2, 0x10, bytes.fromhex("c70044c701720622")),   # q0: som, som, peça
    (2, 0x18, 0x0623),
    (2, 0x18, bytes.fromhex("de0624")),             # q2: fim dos hits extras
    (9, 0x18, 0x0625),                              # q3: 4º hit
    (2, 0x00, bytes.fromhex("d00624")),             # q4: era 5
    (2, 0x00, 0x0623),                              # q5: era 5
    (2, 0x00, 0x0622),                              # q6: era 4
    (0, 0x80, 0x0622),
]


def last_anim_block(org):
    out, streams = bytearray(), bytearray()
    cmd_base = org + len(LAST_FRAMES) * 4
    for k, (dur, flags, value) in enumerate(LAST_FRAMES):
        if isinstance(value, bytes):
            target = cmd_base + len(streams)
            streams += value + b"\x00" * (len(value) & 1)
            out += bytes([dur, flags]) + (target - (org + k * 4 + 2)).to_bytes(2, "big")
        else:
            out += bytes([dur | 0x80, flags]) + value.to_bytes(2, "big")
    return bytes(out + streams)


PATCH = Patch(
    id="renbuken-juggle",
    title="Ryo: Renbuken gasta 20% e recupera rápido depois do 4º hit",
    spec="src/backend/specs/SPEC-017-ryo-renbuken-juggle.md",
    blocks=[
        Block("renbuken_cost", cost),
        DataBlock("renbuken_last", len(last_anim_block(0x100000)), last_anim_block),
    ],
    hooks=[
        # $1D7B2: move.b $4(a0),$241(a6)
        Hook(addr=0x1D7B2, expect="1d6800040241", to_block="renbuken_cost"),
    ],
    data=[
        Data(ANIM_TABLE + NEW_LAST_ANIM * 4, "00000000",
             lambda addrs: (len(LAST_FRAMES) << 24 | addrs["renbuken_last"]).to_bytes(4, "big").hex()),
        Data(SEQ_LAST, "0121", f"{NEW_LAST_ANIM:04x}"),
    ],
)
