"""kououken-weak-startup (Ryo) — SPEC-009.

Kou'ouken fraco (id $013, botão A) com startup de 11 frames (era 23), para
combar depois de normais cancelados (SPEC-008). O forte ($011) não muda.

As três versões do Kou'ouken usavam a mesma animação $0140 (SPEC-007).
O patch cria a animação $017F (id livre na tabela $050000) como cópia da
$0140 com os quadros de preparação q1-q4 encurtados, e aponta só o $013
para ela (atributo +10 em $23BA4 + id*16).

Quadros de comando (duração sem bit 7) usam offset RELATIVO de 16 bits
(adda.w em $4A6E), então a nova lista precisa ficar a até 32 KB das
listas de comando originais ($531D4/$531DB). Fica em $51F00, dentro da
tabela de animações, nas entradas zeradas (sem uso) dos ids $7C0-$7CB.
"""
from patchlib import Data, Patch

ANIM_TABLE = 0x050000
NEW_ANIM = 0x17F
FRAME_LIST = 0x051F00          # 12 quadros x 4 bytes, nas entradas livres $7C0-$7CB
WEAK_MOVE_ATTR_ANIM = 0x23BA4 + 0x013 * 16 + 10
ORIGINAL_ANIM = 0x0140

PIECE, CMD = "piece", "cmd"

# Animação $0140 original: (duração, flags, tipo, valor)
#   PIECE: valor = índice da peça de sprite (duração com bit 7)
#   CMD:   valor = endereço absoluto da lista de comandos
# q5 cria o projétil. Original: q0..q4 = 3+8+4+4+4 = 23 frames até o q5.
FRAMES = [
    (3, 0x10, CMD, 0x0531D4),    # q0
    (2, 0x10, PIECE, 0x068E),    # q1 (era 8)
    (2, 0x10, PIECE, 0x068F),    # q2 (era 4)
    (2, 0x10, PIECE, 0x0690),    # q3 (era 4)
    (2, 0x10, PIECE, 0x0691),    # q4 (era 4)  -> projétil no frame 11
    (2, 0x10, CMD, 0x0531DB),    # q5 cria o projétil
    (2, 0x10, PIECE, 0x0D15),    # q6
    (2, 0x10, PIECE, 0x0D16),    # q7
    (24, 0x10, PIECE, 0x0692),   # q8
    (4, 0x00, PIECE, 0x0626),    # q9  recuperação
    (4, 0x00, PIECE, 0x062A),    # q10 recuperação
    (0, 0x80, PIECE, 0x062A),    # q11 quadro final
]


def frame_bytes(org):
    out = bytearray()
    for k, (dur, flags, kind, value) in enumerate(FRAMES):
        f = org + k * 4
        if kind == PIECE:
            out += bytes([dur | 0x80, flags]) + value.to_bytes(2, "big")
        else:
            rel = value - (f + 2)
            if not -0x8000 <= rel <= 0x7FFF:
                raise ValueError(f"q{k}: lista de comandos fora do alcance de 16 bits")
            out += bytes([dur, flags]) + (rel & 0xFFFF).to_bytes(2, "big")
    return bytes(out)


NEW_FRAMES = frame_bytes(FRAME_LIST)
STARTUP = sum(f[0] for f in FRAMES[:5])
assert STARTUP == 11

PATCH = Patch(
    id="kououken-weak-startup",
    title="Ryo: Kou'ouken fraco com startup de 11 frames (era 23)",
    spec="src/backend/specs/SPEC-009-ryo-kououken-weak-startup.md",
    data=[
        # lista de quadros nova, nas entradas vazias da tabela de animações
        Data(FRAME_LIST, "00" * len(NEW_FRAMES), NEW_FRAMES.hex()),
        # entrada da animação $17F: 12 quadros em FRAME_LIST
        Data(ANIM_TABLE + NEW_ANIM * 4, "00000000",
             (len(FRAMES) << 24 | FRAME_LIST).to_bytes(4, "big").hex()),
        # Kou'ouken fraco ($013) passa a usar $17F
        Data(WEAK_MOVE_ATTR_ANIM, f"{ORIGINAL_ANIM:04x}", f"{NEW_ANIM:04x}"),
    ],
)
