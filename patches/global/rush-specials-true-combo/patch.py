"""rush-specials-true-combo — SPEC-015.

Especiais de sequência com vários hits (Ryo, Robert, Takuma, Eiji): depois
que o 1º hit acerta, os outros conectam sem o oponente poder defender.

Esses golpes usam uma SEQUÊNCIA de animações (atributo +10 com bit 15 ->
tabela $233BE -> lista de ids; o bit 15 de cada id encadeia a próxima) e
têm hits extras no byte 7 (-> $247). Um trecho sem caixa de ataque longo
demais (18 frames no Ryo/Robert/Takuma, 16 no Eiji) deixava o oponente
sair da reação (~17 frames) e defender o resto (medido no Ryo com
tools/lua/frame_data.lua).

Correção: a sequência passa a usar uma CÓPIA da animação com o trecho
encurtado; a animação original (ex.: soco forte longe) não muda.

| Personagem | Golpe | Sequência              | Animação copiada | Encurtado              |
| Ryo        | $021  | $120 $122 $120 $121    | $122 -> $17D     | recuperação 8+8 -> 2+2 |
| Robert     | $046  | $1A0 $1A2 $1A0 $1A1    | $1A2 -> $177     | recuperação 8+8 -> 2+2 |
| Eiji       | $06B  | $238 $231              | $238 -> $178     | entre hits 4+3+3+3+3 -> 2+1+1+1+1 |
| Eiji       |       |                        | $231 -> $271     | antes do 3º hit 6+3+3+3 -> 1+1+1+1 |
| Takuma     | $163  | $5A0 $5A2 $5A0 $5A1    | $5A2 -> $179     | recuperação 8+8 -> 2+2 |
| Yuri       | $186  | $620 $631 $62B $63A    | $631/$62B/$63A -> $272/$273/$274 | buracos 15 e 14 -> ~7 |

Quadros de comando apontam para a lista de comandos com offset relativo de
16 bits ($4A6E). Ryo, Robert e Eiji ficam nas entradas vazias da tabela de
animações ($51F90+), ao alcance das listas originais. O Takuma não tem área
livre ao alcance: a lista de comandos dele (8 bytes) é copiada junto dos
quadros, num bloco de dados alocado pelo build.
"""
from patchlib import Data, DataBlock, Patch

ANIM_TABLE = 0x050000
PIECE, CMD = "piece", "cmd"


def frame_bytes(frames, org, cmd_override=None):
    """Monta a lista de quadros em `org`. CMD aponta para o endereço dado
    (ou para `cmd_override`, quando a lista de comandos é copiada)."""
    out = bytearray()
    for k, (dur, flags, kind, value) in enumerate(frames):
        f = org + k * 4
        if kind == PIECE:
            out += bytes([dur | 0x80, flags]) + value.to_bytes(2, "big")
        else:
            target = cmd_override if cmd_override is not None else value
            rel = target - (f + 2)
            if not -0x8000 <= rel <= 0x7FFF:
                raise ValueError(f"q{k}: lista de comandos fora do alcance de 16 bits")
            out += bytes([dur, flags]) + (rel & 0xFFFF).to_bytes(2, "big")
    return bytes(out)


def anim_entry(count, addr):
    return (count << 24 | addr).to_bytes(4, "big").hex()


# ---- Ryo: $122 (soco forte longe) -> $17D -------------------------------
RYO_FRAMES = [
    (2, 0x18, CMD, 0x052ECA), (2, 0x18, PIECE, 0x0626), (6, 0x18, PIECE, 0x0627),
    (2, 0x00, PIECE, 0x0626),   # era 8
    (2, 0x00, PIECE, 0x062A),   # era 8
    (0, 0x80, PIECE, 0x062A),
]
# ---- Robert: $1A2 -> $177 -----------------------------------------------
ROBERT_FRAMES = [
    (2, 0x10, CMD, 0x054000), (2, 0x18, PIECE, 0x0B7C), (6, 0x18, PIECE, 0x0B7D),
    (2, 0x00, PIECE, 0x0B7C),   # era 8
    (2, 0x00, PIECE, 0x0B7B),   # era 8
    (0, 0x80, PIECE, 0x0B7B),
]
# ---- Eiji: $238 -> $178 (trecho entre o 1º e o 2º hit) ------------------
EIJI_FRAMES = [
    (2, 0x10, CMD, 0x055256), (2, 0x10, PIECE, 0x03FB), (8, 0x10, PIECE, 0x03FC),
    (2, 0x10, PIECE, 0x03FB),   # era 4
    (1, 0x10, PIECE, 0x03FD),   # era 3
    (1, 0x10, PIECE, 0x03FE),   # era 3
    (1, 0x10, PIECE, 0x03FF),   # era 3
    (1, 0x10, PIECE, 0x0400),   # era 3
    (8, 0x10, PIECE, 0x0401),
    (1, 0x00, PIECE, 0x0402),   # era 6
    (0, 0x80, PIECE, 0x0402),
]
# ---- Eiji: $231 (golpe final) -> $271 (no bloco, comandos copiados) -------
EIJI_FINAL_FRAMES = [
    (1, 0x10, CMD, bytes.fromhex("c70046c702de03f3")),   # era 3
    (1, 0x10, PIECE, 0x03F4),   # era 3
    (1, 0x18, PIECE, 0x03F5),   # era 3
    (3, 0x18, CMD, bytes.fromhex("de03f6")),   # $DE + peça de ataque $3F6 (3º hit)
    (8, 0x00, PIECE, 0x03F7), (6, 0x00, PIECE, 0x03F8), (0, 0x80, PIECE, 0x03F8),
]
# ---- Takuma: $5A2 -> $179 (lista de comandos copiada) --------------------
TAKUMA_FRAMES = [
    (2, 0x18, CMD, 0x05BDC8), (6, 0x18, PIECE, 0x09DD),
    (2, 0x00, PIECE, 0x09DC),   # era 8
    (2, 0x00, PIECE, 0x09DA),   # era 8
    (0, 0x80, PIECE, 0x09DA),
]
TAKUMA_CMD = bytes.fromhex("c70044" "c70294" "09dc")   # som, som, peça (de $5BDC8)

# ---- Yuri: $186 (C para trás + chute) -----------------------------------
# Sequência $620 $631 $62B $63A. As listas de comandos ($5CDxx-$5CFxx) estão
# longe demais de qualquer área livre: vão copiadas no bloco (bytes, não
# endereço). Opcodes: $C7 som (2 bytes), $EC (1 byte), $DE (0: encerra os
# hits extras); a lista termina numa peça.
YURI_A = [   # $631 -> $272 (2º hit)
    (4, 0x10, CMD, bytes.fromhex("c70046c702b8011e")),
    (4, 0x18, PIECE, 0x011F), (3, 0x1A, PIECE, 0x0120), (3, 0x18, PIECE, 0x0121),
    (1, 0x00, PIECE, 0x0122),   # era 6
    (0, 0x80, PIECE, 0x0122),
]
YURI_B = [   # $62B -> $273 (3º hit)
    (1, 0x10, PIECE, 0x0113),   # era 3
    (2, 0x10, CMD, bytes.fromhex("c70044c702b80114")),
    (1, 0x10, PIECE, 0x0115),   # era 2
    (2, 0x10, CMD, bytes.fromhex("ec010116")),
    (2, 0x10, PIECE, 0x0117), (4, 0x10, PIECE, 0x0118),
    (1, 0x10, PIECE, 0x0119),   # era 4
    (1, 0x00, PIECE, 0x011A),   # era 4
    (0, 0x80, PIECE, 0x011A),
]
YURI_C = [   # $63A -> $274 (4º hit)
    (2, 0x10, CMD, bytes.fromhex("c70046c702b80123")),
    (1, 0x10, PIECE, 0x0124),   # era 2
    (1, 0x10, PIECE, 0x0125),   # era 2
    (2, 0x10, CMD, bytes.fromhex("ec010126")),
    (6, 0x10, CMD, bytes.fromhex("de0127")),
    (3, 0x10, PIECE, 0x0128), (3, 0x10, PIECE, 0x0129),
    (3, 0x00, PIECE, 0x0123), (0, 0x80, PIECE, 0x0123),
]
YURI = [(0x272, YURI_A), (0x273, YURI_B), (0x274, YURI_C)]

FIXED = [  # (id novo, endereço, quadros) nas entradas vazias da tabela ($7E4+)
    (0x17D, 0x051F90, RYO_FRAMES),
    (0x177, 0x051FA8, ROBERT_FRAMES),
    (0x178, 0x051FC0, EIJI_FRAMES),
]
SEQUENCES = [  # (endereço do item na lista, original, novo)
    (0x02385E + 2, 0x8122, 0x817D),   # Ryo
    (0x02386A + 2, 0x81A2, 0x8177),   # Robert
    (0x023710 + 0, 0x8238, 0x8178),   # Eiji
    (0x023710 + 2, 0x0231, 0x0271),
    (0x023876 + 2, 0x85A2, 0x8179),   # Takuma
    (0x0237E0 + 2, 0x8631, 0x8272),   # Yuri
    (0x0237E0 + 4, 0x862B, 0x8273),
    (0x0237E0 + 6, 0x063A, 0x0274),
]


def takuma_block(org):
    frames_len = len(TAKUMA_FRAMES) * 4
    return frame_bytes(TAKUMA_FRAMES, org, cmd_override=org + frames_len) + TAKUMA_CMD


def copied_block(anims, org):
    """Quadros das animações, depois as listas de comandos copiadas (pares)."""
    out, streams, cmd_at = bytearray(), bytearray(), {}
    frames_end = org + sum(len(f) for _, f in anims) * 4
    for _, frames in anims:
        for k, (dur, flags, kind, value) in enumerate(frames):
            if kind == CMD:
                cmd_at[(id(frames), k)] = frames_end + len(streams)
                streams += value + b"\x00" * (len(value) & 1)
    for _, frames in anims:
        base = org + len(out)
        fixed = [(du, fl, ki, cmd_at[(id(frames), k)] if ki == CMD else v)
                 for k, (du, fl, ki, v) in enumerate(frames)]
        out += frame_bytes(fixed, base)
    return bytes(out + streams)


def anim_offset(anims, anim_id):
    off = 0
    for aid, frames in anims:
        if aid == anim_id:
            return off
        off += len(frames) * 4


COPIED = {"eiji": [(0x271, EIJI_FINAL_FRAMES)], "yuri": YURI}

data = []
for anim_id, addr, frames in FIXED:
    fb = frame_bytes(frames, addr)
    data.append(Data(addr, "00" * len(fb), fb.hex()))
    data.append(Data(ANIM_TABLE + anim_id * 4, "00000000", anim_entry(len(frames), addr)))
data.append(Data(ANIM_TABLE + 0x179 * 4, "00000000",
                 lambda addrs: anim_entry(len(TAKUMA_FRAMES), addrs["takuma"])))
for key, anims in COPIED.items():
    for aid, frames in anims:
        data.append(Data(ANIM_TABLE + aid * 4, "00000000",
                         lambda addrs, key=key, anims=anims, aid=aid, n=len(frames):
                         anim_entry(n, addrs[key] + anim_offset(anims, aid))))
for addr, old, new in SEQUENCES:
    data.append(Data(addr, f"{old:04x}", f"{new:04x}"))

PATCH = Patch(
    id="rush-specials-true-combo",
    title="Especiais de sequência (Renbuken etc.) com todos os hits em combo",
    spec="src/backend/specs/SPEC-015-rush-specials-true-combo.md",
    blocks=[DataBlock("takuma", len(TAKUMA_FRAMES) * 4 + len(TAKUMA_CMD), takuma_block),
            *[DataBlock(key, len(copied_block(anims, 0x100000)),
                        lambda org, anims=anims: copied_block(anims, org))
              for key, anims in COPIED.items()]],
    data=data,
)
