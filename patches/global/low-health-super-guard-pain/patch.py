"""Vida <= 32: SUPER defendido abre punição em cheap KO; dano letal preservado — SPEC-051."""
from asm68k import Branch, Ins, JmpAbs, Label, LeaPc, Raw
from patchlib import Block, Data, DataBlock, Hook, Patch

# Comandos cujos handlers originais são $1D5A8 (SUPER), personagem 1..12.
SUPERS = (0xFFFF, 0x42, 0x41, 0x44, 0x43, 0x44, 0x45,
          0x47, 0x41, 0x45, 0x41, 0x41, 0x42)


def eligible():
    return [
        Ins("4a6e006c", "tst.w $6c(a6)"),
        Branch("ble", "original"),
        Ins("0c6e0020006c", "cmpi.w #$20, $6c(a6)"),
        Branch("bhi", "original"),
        Ins("720f", "moveq #$f, d1"),
        Ins("c22e007c", "and.b $7c(a6), d1"),
        Ins("0c010003", "cmpi.b #$3, d1"),
        Branch("bne", "original"),
        Ins("206e0064", "movea.l $64(a6), a0"),
        Ins("32280062", "move.w $62(a0), d1"),
        Ins("0c410001", "cmpi.w #$1, d1"),
        Branch("bcs", "original"),
        Ins("0c41000c", "cmpi.w #$c, d1"),
        Branch("bhi", "original"),
        Ins("d241", "add.w d1, d1"),
        LeaPc("supers", 1),
        Ins("32311000", "move.w (a1, d1.w), d1"),
        Ins("b26e0a6a", "cmp.w $a6a(a6), d1"),
        Branch("bne", "original"),
    ]


table = [Label("supers"), Raw("".join(f"{cmd:04x}" for cmd in SUPERS))]

pain = [
    # Código deslocado: dois JSR relativos ao PC, agora absolutos.
    Ins("4eb90001d378", "jsr $1d378.l"),
    Ins("4eb900021aa6", "jsr $21aa6.l"),
    *eligible(),
    # $14 é a reação de cheap KO: tabela de derrota $212E4,
    # entradas de defesa em pé/agachado -> $14. Não usa derrota do round.
    Ins("7214", "moveq #$14, d1"),
    Ins("422e0a69", "clr.b $a69(a6)"),
    Ins("197c00010058", "move.b #$1, $58(a4)"),
    # Índice já convertido: entra diretamente no seletor por personagem,
    # sem passar de novo pela tabela de reações de quem continua vivo.
    Ins("4eb900020604", "jsr $20604.l"),
    Ins("302e0062", "move.w $62(a6), d0"),
    Ins("064007b0", "addi.w #$7b0, d0"),
    Ins("3d40006e", "move.w d0, $6e(a6)"),
    Ins("08ae0007003f", "bclr.b #$7, $3f(a6)"),
    Ins("022e007e0070", "andi.b #$7e, $70(a6)"),
    Ins("4e75", "rts"),
    Label("original"),
    JmpAbs(0x205A4),
    *table,
]

# Cópias curtas das animações nativas; identificam a janela sem RAM nova.
CHIP_FRAMES = [[(6, 0, 1645), (6, 0, b'\xc7\x03\xc4\x06n'), (6, 0, 1647), (6, 0, 1648), (0, 128, 1648)],
 [(4, 0, 2994),
  (4, 0, b'\xca\x03\xc6\x046\x0b\xbe'),
  (4, 0, 3007),
  (4, 0, 3008),
  (4, 0, 3009),
  (4, 0, 3010),
  (0, 128, 3010)],
 [(4, 0, 1122),
  (4, 0, b'\xc7\x03\xd8\x04c'),
  (4, 0, 1124),
  (4, 0, 1125),
  (4, 0, 1127),
  (4, 0, 1126),
  (0, 128, 1126)],
 [(8, 0, 1370), (8, 0, b'\xc7\x03\xc8\x05['), (8, 0, 1372), (0, 128, 1372)],
 [(6, 0, 2872), (6, 0, b'\xc7\x03\xca\x0b9'), (6, 0, 2874), (6, 0, 2878), (0, 128, 2878)],
 [(6, 0, 1835), (6, 0, b'\xca\x03\xcc\x03\xcc\x07+'), (12, 0, 1836), (0, 128, 1836)],
 [(8, 0, 913),
  (4, 0, b'\xc7\x03\xce\x03\x92'),
  (4, 0, 915),
  (4, 0, 966),
  (4, 0, 967),
  (0, 128, 967)],
 [(4, 0, 739),
  (4, 0, b'\xca\x03\xd0\x04D\x02\xe4'),
  (4, 0, 741),
  (4, 0, 742),
  (4, 0, 743),
  (4, 0, 744),
  (0, 128, 744)],
 [(6, 0, 3202), (6, 0, b'\xc7\x03\xd2\x0c\x83'), (6, 0, 3204), (6, 0, 3205), (0, 128, 3205)],
 [(6, 0, 2583), (6, 0, b'\xc7\x03\xd4\n\x18'), (6, 0, 2585), (6, 0, 2586), (0, 128, 2586)],
 [(4, 0, 329),
  (4, 0, b'\xc7\x03\xd6\x01J'),
  (4, 0, 331),
  (4, 0, 332),
  (4, 0, 333),
  (4, 0, 334),
  (0, 128, 334)],
 [(8, 0, 567),
  (4, 0, b'\xc7\x03\xda\x028'),
  (4, 0, 569),
  (4, 0, 570),
  (4, 0, 571),
  (0, 128, 571)],
 [(3, 0, 1463),
  (3, 0, b'\xc7\x03\xdc\x05\xb8'),
  (3, 0, 1465),
  (3, 0, 1466),
  (3, 0, 1467),
  (3, 0, 1468),
  (3, 0, 1469),
  (3, 0, 2769),
  (0, 128, 2769)]]


def chip_animation(frames, org):
    out, streams = bytearray(), bytearray()
    for k, (duration, flags, value) in enumerate(frames):
        if isinstance(value, bytes):
            target = org + len(frames) * 4 + len(streams)
            out += bytes((duration, flags)) + (target - (org + k * 4 + 2)).to_bytes(2, "big")
            streams += value + bytes(len(value) & 1)
        else:
            out += bytes((duration | 0x80, flags)) + value.to_bytes(2, "big")
    return bytes(out + streams)


vulnerable = [
    Ins("0c6e07b1006e", "cmpi.w #$7b1, $6e(a6)"),
    Branch("bcs", "store"),
    Ins("0c6e07bd006e", "cmpi.w #$7bd, $6e(a6)"),
    Branch("bhi", "store"),
    # Contato durante a janela: retira a classificação de defesa.
    # A nova reação substitui $6E e encerra a janela deste patch.
    Ins("020000f0", "andi.b #$f0, d0"),
    Label("store"),
    Ins("1d40007c", "move.b d0, $7c(a6)"),
    Ins("4e75", "rts"),
]


PATCH = Patch(
    id="low-health-super-guard-pain",
    title="Vida até 32: defender SUPER abre 24 frames de punição em cheap KO",
    spec="src/backend/specs/SPEC-051-low-health-super-guard-pain.md",
    blocks=[Block("super_guard_pain", pain),
            Block("super_guard_vulnerable", vulnerable)] + [
        DataBlock(f"cheap_pose_{char}", len(chip_animation(frames, 0)),
                  lambda org, frames=frames: chip_animation(frames, org))
        for char, frames in enumerate(CHIP_FRAMES, 1)
    ],
    data=[Data(0x50000 + (0x7B0 + char) * 4, "00000000",
               lambda addrs, char=char, count=len(frames):
               (count << 24 | addrs[f"cheap_pose_{char}"]).to_bytes(4, "big").hex())
          for char, frames in enumerate(CHIP_FRAMES, 1)],
    hooks=[
        Hook(0x223F6, "1d40007c4e75", to_block="super_guard_vulnerable"),
        Hook(0x2059C, "4ebacdda61001504", to_block="super_guard_pain"),
    ],
)
