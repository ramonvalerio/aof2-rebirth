"""King: rasteira e final do Moushuukyaku derrubam — SPEC-044."""
from charlib import MOVE_TABLE
from patchlib import Data, Patch

SWEEP = 0x0CA
ANIM_TABLE = 0x50000
NEW_FINAL = 0x790
FRAME_LIST = 0x51E80  # 9 quadros em entradas vazias $7A0..$7A8
FINAL_COMMAND = 0x51EB0  # entradas vazias $7AC/$7AD

# Cópia de $3CA: durações, flags e poses originais. Só q5 muda a lista.
FRAMES = [
    (2, 0x10, False, 0x583F1),
    (2, 0x10, True, 0x06E6),
    (3, 0x10, True, 0x0714),
    (3, 0x10, True, 0x0715),
    (3, 0x10, True, 0x0716),
    (6, 0x10, False, FINAL_COMMAND),
    (3, 0x00, True, 0x0718),
    (3, 0x00, True, 0x06C7),
    (0, 0x80, True, 0x06C7),
]


def frame_bytes():
    out = bytearray()
    for index, (duration, flags, piece, value) in enumerate(FRAMES):
        if piece:
            offset = value
        else:
            offset = value - (FRAME_LIST + index * 4 + 2)
            assert -0x8000 <= offset <= 0x7FFF
        out += bytes((duration | (0x80 if piece else 0), flags))
        out += (offset & 0xFFFF).to_bytes(2, 'big')
    return out.hex()


PATCH = Patch(
    id='knockdown-finishes',
    title='King: rasteira e último hit do Moushuukyaku forte derrubam',
    spec='src/backend/specs/SPEC-044-king-knockdown-finishes.md',
    data=[
        Data(MOVE_TABLE + SWEEP * 16 + 6, '00', '15'),
        Data(FRAME_LIST, '00' * 36, frame_bytes()),
        # E7 0140: som; DE: encerra hits extras; DD 15: queda; 0717: peça.
        Data(FINAL_COMMAND, '00' * 8, 'e70140dedd150717'),
        Data(ANIM_TABLE + NEW_FINAL * 4, '00000000',
             (9 << 24 | FRAME_LIST).to_bytes(4, 'big').hex()),
        # Só $0D9 / sequência $803F (forte). Média e fraca usam $3CA original.
        Data(0x236B2, '03ca', f'{NEW_FINAL:04x}'),
    ],
)
