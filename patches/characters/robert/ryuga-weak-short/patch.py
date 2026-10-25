"""ryuga-weak-short (Robert) — SPEC-029.

Ryuga fraco (comando $47, golpe $049, botão A; SPEC-004) com as mesmas
propriedades do Kohou fraco do Ryo (SPEC-010): sobe pouco, acerta 1 vez,
derruba e recupera rápido. O Ryuga forte ($048) não muda.

Original (anim $1C5, compartilhada pelo $048 e $049), igual ao Kohou:
  q0-q2 (t=0..9)  hit no chão (peça $1146)
  q3 (t=9)        lista de comandos $5476B: c7 som, eb, de, dd 01,
                  d2 [alinhamento] vy $000CC000, gravidade $FF70,
                  vx $0180, atrito 0; peça $0C1D (só caixa de ataque: 2º hit)
  q4/q5 no ar ($0C1E/$0C1F), q6 segura até o chão, q7-q9 aterrissagem
  byte 6 do golpe = $0B (efeito do 1º hit, sem queda)

Ryuga fraco:
  - animação própria $2AA (id livre) = cópia da $1C5;
  - lista do lançamento copiada com vy $00070000 (7 px/frame, ~43 px, como
    o Kohou fraco) e a peça $0C1E (só corpo) no lugar de $0C1D -> só o hit
    do chão;
  - byte 6 = $01: derruba (o efeito do 2º hit do forte, via "dd 01").

Os dados ficam nas entradas vazias da tabela de animações dos ids
$2F0-$2FF ($50BC0-$50BFF), ao alcance do offset de 16 bits da lista de
aterrissagem ($54780). A lista copiada fica num endereço ímpar, como a
original ($5476B), para o byte de alinhamento do $D2 cair igual.
"""
from patchlib import Data, Patch

ANIM_TABLE = 0x050000
NEW_ANIM = 0x2AA
WEAK_ID = 0x049
ATTR = 0x23BA4 + WEAK_ID * 16
ORIGINAL_ANIM = 0x01C5

FRAME_LIST = 0x050BC0          # 10 quadros x 4 bytes (entradas livres $2F0-$2F9)
LAUNCH_COPY = 0x050BE9         # ímpar, como o original

WEAK_VY = 0x00070000
LAUNCH_ORIGINAL = bytes.fromhex("c7003eebdedd01d200" "000cc000" "ff70" "0180" "0000" "0c1d")
LAUNCH_WEAK = (LAUNCH_ORIGINAL[:9] + WEAK_VY.to_bytes(4, "big")
               + LAUNCH_ORIGINAL[13:19] + bytes.fromhex("0c1e"))

PIECE, CMD = "piece", "cmd"
FRAMES = [
    (2, 0x10, PIECE, 0x1144),        # q0
    (2, 0x10, PIECE, 0x1145),        # q1
    (5, 0x10, PIECE, 0x1146),        # q2  hit no chão
    (0, 0x30, CMD, LAUNCH_COPY),     # q3  lançamento (vy menor, sem 2º hit)
    (10, 0x00, PIECE, 0x0C1E),       # q4
    (10, 0x00, PIECE, 0x0C1F),       # q5
    (0, 0x00, PIECE, 0x0C20),        # q6  segura até o chão
    (6, 0x00, CMD, 0x054780),        # q7  lista original da aterrissagem
    (6, 0x00, PIECE, 0x0B71),        # q8
    (0, 0x80, PIECE, 0x0B71),        # q9  quadro final
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
assert LAUNCH_COPY % 2 == 1 and LAUNCH_COPY >= FRAME_LIST + len(NEW_FRAMES)
assert LAUNCH_COPY + len(LAUNCH_WEAK) <= 0x050C00

PATCH = Patch(
    id="ryuga-weak-short",
    title="Robert: Ryuga fraco curto (sobe pouco, 1 hit, derruba), como o Kohou fraco do Ryo",
    spec="src/backend/specs/SPEC-029-robert-ryuga-weak-short.md",
    data=[
        Data(FRAME_LIST, "00" * len(NEW_FRAMES), NEW_FRAMES.hex()),
        Data(LAUNCH_COPY, "00" * len(LAUNCH_WEAK), LAUNCH_WEAK.hex()),
        Data(ANIM_TABLE + NEW_ANIM * 4, "00000000",
             (len(FRAMES) << 24 | FRAME_LIST).to_bytes(4, "big").hex()),
        Data(ATTR + 6, "0b", "01"),                                   # derruba
        Data(ATTR + 10, f"{ORIGINAL_ANIM:04x}", f"{NEW_ANIM:04x}"),   # animação própria
    ],
)
