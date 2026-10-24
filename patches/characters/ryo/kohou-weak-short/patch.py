"""kohou-weak-short (Ryo) — SPEC-010.

Kohou fraco (id $024, botão A; SPEC-004 usa id+1 porque o $025 é a versão
de falha): sobe pouco, acerta 1 vez, sempre derruba e recupera rápido.
O Kohou forte ($023) não muda.

Original (anim $0145, compartilhada pelo $023 e $024):
  q2 (t=4..9)  hit no chão (peça $1143, filho 5)
  q3 (t=9)     lista de comandos $53645: ... $D2 <vy $000CC000> <grav $FF70>
               <vx $0180> <atrito 0>, depois a peça $0AE8 (corpo + ataque)
  q4 (t=9..15) peça $0AE8 de novo: segundo hit, já subindo
  byte 6 do golpe = $0B (efeito de acerto do 1º hit, sem queda)

Kohou fraco:
  - animação própria $17E (id livre) = cópia da $0145
  - lista de comandos do lançamento copiada com vy menor e peça $0AE9
    (só corpo) no lugar de $0AE8; q4 também usa $0AE9 -> só o hit do chão
  - byte 6 = $01: o mesmo efeito do 2º hit do Kohou forte, que derruba.
    No forte, o hit do chão usa o $0B da tabela e o opcode "dd 01" da lista
    do lançamento ($DD -> $1D3D6: move.b (a0)+,$20A) troca o efeito para $01
    antes do 2º hit. Assim a queda do oponente é a mesma do Kohou forte.

Dados novos ficam nas entradas vazias da tabela de animações (ids $7D0+),
ao alcance do offset relativo de 16 bits das listas de comando.
"""
from patchlib import Data, Patch

ANIM_TABLE = 0x050000
NEW_ANIM = 0x17E
WEAK_ID = 0x024
ATTR = 0x23BA4 + WEAK_ID * 16
ORIGINAL_ANIM = 0x0145

FRAME_LIST = 0x051F40          # 11 quadros x 4 bytes (entradas livres $7D0-$7DA)
LAUNCH_COPY = 0x051F71         # endereço ímpar, como o original ($53645)

ORIGINAL_VY = 0x000CC000       # 12,75 px/frame para cima (~145 px de altura)
WEAK_VY = 0x00070000           # 7 px/frame (~43 px de altura)

# Lista de comandos original do lançamento ($53645..$53659):
#   de eb dd 01 c7 00 3e d2 | 0c (alinhamento) | 000cc000 ff70 0180 0000 | 0ae8
LAUNCH_ORIGINAL = bytes.fromhex("deebdd01c7003ed20c000cc000ff7001800000" "0ae8")
LAUNCH_WEAK = (LAUNCH_ORIGINAL[:9] + WEAK_VY.to_bytes(4, "big")
               + LAUNCH_ORIGINAL[13:19] + bytes.fromhex("0ae9"))

PIECE, CMD = "piece", "cmd"

# (duração, flags, tipo, valor); CMD = endereço absoluto da lista de comandos
FRAMES = [
    (2, 0x10, PIECE, 0x1141),        # q0
    (2, 0x10, PIECE, 0x1142),        # q1
    (5, 0x10, PIECE, 0x1143),        # q2  hit no chão (t=4..9)
    (0, 0x30, CMD, LAUNCH_COPY),     # q3  lançamento (vy menor, sem caixa de ataque)
    (6, 0x00, PIECE, 0x0AE9),        # q4  era $0AE8 (2º hit)
    (6, 0x00, PIECE, 0x0AE9),        # q5
    (6, 0x00, PIECE, 0x0AEC),        # q6
    (6, 0x00, PIECE, 0x0AEA),        # q7
    (0, 0x00, PIECE, 0x0AEB),        # q8
    (6, 0x00, CMD, 0x05365A),        # q9  lista original
    (0, 0x80, PIECE, 0x0605),        # q10 quadro final
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

PATCH = Patch(
    id="kohou-weak-short",
    title="Ryo: Kohou fraco curto (sobe pouco, 1 hit, derruba como o forte)",
    spec="src/backend/specs/SPEC-010-ryo-kohou-weak-short.md",
    data=[
        Data(FRAME_LIST, "00" * len(NEW_FRAMES), NEW_FRAMES.hex()),
        Data(LAUNCH_COPY, "00" * len(LAUNCH_WEAK), LAUNCH_WEAK.hex()),
        Data(ANIM_TABLE + NEW_ANIM * 4, "00000000",
             (len(FRAMES) << 24 | FRAME_LIST).to_bytes(4, "big").hex()),
        # byte 6: efeito de acerto $0B -> $01 (o do 2º hit do Kohou forte: derruba)
        Data(ATTR + 6, "0b", "01"),
        # animação do Kohou fraco
        Data(ATTR + 10, f"{ORIGINAL_ANIM:04x}", f"{NEW_ANIM:04x}"),
    ],
)
