"""Título com "REBIRTH" sob o logo — SPEC-082.

A palavra usa a fonte dos nomes do retrato na seleção de personagem
(serifada itálica dourada com contorno azul, tiles de sprite $65C9-$65FF).
As letras foram recortadas desses nomes (R de RYO, E de LEE, B e I de BIG,
T de TAKUMA, H de JOHN) e o degradê dourado foi refeito na palavra inteira.

Vai na camada fix, em 30 tiles de 8x8 vazios e nunca exibidos da S-ROM,
com a paleta fix 15, que já é a paleta desses nomes (mesmos índices).
O mapa fix é escrito pela fila de textos do VBlank a cada frame do título.
"""
from asm68k import Ins, JmpAbs, Label, LeaPc, Raw
from patchlib import Block, Hook, Patch, RomData

S_ROM = "056-s1.s1"
PALETTE = 0xF            # paleta fix 15 = paleta dos nomes da seleção
COL, ROW = 10, 17        # x = COL*8-8 = 72, y = ROW*8-16 = 120 (sob "FIGHTING")
CELLS = 15               # 119 px de largura -> 15 colunas x 2 linhas

# Tiles fix vazios fora das fontes ativas e da área de kana/kanji; nenhum
# aparece no mapa fix depois do boot (medição em tools/lua, SPEC-082).
FREE_TILES = (
    list(range(0x31D, 0x320)) + list(range(0x41B, 0x420)) + list(range(0x4D8, 0x4E0))
    + list(range(0xDF0, 0xDF4)) + list(range(0xFBB, 0xFC0)) + list(range(0xFFA, 0xFFF))
)

# Índices da paleta: 1-13 degradê dourado, 14 contorno azul, "." transparente.
ART = [
    ".......................................................................................................................",
    "...2222333334ee...e...66666777778888ee...9aaaaabbbbee......dddccccee...baaaaa9999ee...e.e777666665555...444333ee222221e",
    "...222233333444ee.e...6666677777888ee....9aaaaabbbbbcee....dddccccee...baaaaa999998ee.e.e777666665555...444333ee222221e",
    "...e2223eeee4444ee....e6666eeeeee88ee....eaaaaeeeebbccee...eddcceeee...eaaaaeeee9988ee.e77eee6666eee...ee4433eeee222ee.",
    "...e2223ee..e444ee....e6666ee....eee.....eaaaaee.ebbccee...eddccee.....eaaaaee..e988ee.e77eee6666eee...ee4433ee.e222ee.",
    "...e2223ee..e444ee....e6666ee............eaaaee..ebbccee...eddccee.....eaaaaee..e988ee..eeeee6666ee....ee4433ee.e222ee.",
    "..e2222eeeee4444ee...e6666ee.77ee.......e9aaaee.ebbbcee...edddcee.....ebaaaeeeee9988ee.....e6666ee.....e4443eeee222ee..",
    "..e222233333444ee....e666667777ee.......e9aaaaabbbbbee....edddcee.....ebaaaaa999998ee......e6666ee....4e44433333222ee..",
    "..e22223333344ee.....e66666777ee........e9aaaaabbbbee.....edddcee.....ebaaaaa99999ee.......e6666ee....ee44433333222ee..",
    "..e2222eee334ee......e6666ee77ee........e9aaaeeeebbbee....edddcee.....ebaaaeee999ee........e6666ee....ee4443eeee222ee..",
    ".e2222ee.e3344ee....e5666ee.eee........e99aaaee.ebbbee...eddddee.....ebbaaee.e9999ee......e7666ee.....e4444ee.e322ee...",
    ".e2222ee..e344ee....e5666ee............e99aaee..ebbbee...eddddee.....ebbaaee..e999ee......e7666ee....ee4444ee.e322ee...",
    ".e2222ee..e344e4e...e5666ee...e788ee...e99aaee.ebbbbee...eddddee.....ebbaaee..e999e8e.....e7666ee....ee4444ee.e322ee...",
    "1122222ee.e34444...555666667777788ee..9999aaaaabbbbee...cdddddcee...bbbbaaaee.e99988....e7776666ee...5444443ee33222e...",
    "1122222ee..e444e...55566666777778ee...9999aaaaabbee.....cdddddcee...bbbbaaaee..e998e....e7776666ee...5444443ee33222e...",
    ".......................................................................................................................",
]


def cell(cx, cy):
    """Pixels 8x8 da célula (cx, cy) da arte."""
    return [[int(ART[cy * 8 + y][cx * 8 + x], 16) if cx * 8 + x < len(ART[0])
             and ART[cy * 8 + y][cx * 8 + x] != "." else 0 for x in range(8)] for y in range(8)]


def fix_tile(px):
    """Formato da S-ROM: bytes $10-$17 colunas 0-1, $18-$1F 2-3, $00-$07 4-5,
    $08-$0F 6-7 (uma linha por byte; nibble baixo = pixel da esquerda)."""
    out = bytearray(32)
    for y in range(8):
        for pair, base in enumerate((0x10, 0x18, 0x00, 0x08)):
            out[base + y] = px[y][pair * 2] | px[y][pair * 2 + 1] << 4
    return bytes(out)


CELL_TILES = [(cx, cy) for cy in range(2) for cx in range(CELLS)]
assert len(CELL_TILES) == len(FREE_TILES)
TILE_OF = dict(zip(CELL_TILES, FREE_TILES))


def fix_addr(col, row):
    return 0x7000 + col * 0x20 + row


def record():
    """Fila de texto do VBlank ($0FD8): cmd 2 VRAMMOD, cmd 1 (param 3) palavras
    com contagem, cmd 3 VRAMADDR, cmd 7 palavras inline, cmd 0 fim."""
    h = "2002" + f"0301{CELLS:04x}"
    for cy in range(2):
        h += f"0003{fix_addr(COL, ROW + cy):04x}0007"
        h += "".join(f"{PALETTE << 12 | TILE_OF[(cx, cy)]:04x}" for cx in range(CELLS))
    return Raw(h + "0000")


# $157DE: rotina de cada frame da tela de título (move.w #$90,d0 / jsr $41be.w).
title = [
    Ins("303c0090", "move.w #$90, d0"),
    Ins("4eb841be", "jsr $41be.w"),
    Ins("48e700a0", "movem.l a0/a2, -(a7)"),
    Ins("522dfa0c", "addq.b #$1, -$5f4(a5)"),
    Ins("206dfa08", "movea.l -$5f8(a5), a0"),
    LeaPc("record", 2),
    Ins("20ca", "move.l a2, (a0)+"),
    Ins("2b48fa08", "move.l a0, -$5f8(a5)"),
    Ins("532dfa0c", "subq.b #$1, -$5f4(a5)"),
    Ins("4cdf0500", "movem.l (a7)+, a0/a2"),
    JmpAbs(0x157E6),
    Label("record"),
    record(),
]

PATCH = Patch(
    id="title-rebirth",
    title="Título: REBIRTH sob o logo com a fonte dos nomes da seleção",
    spec="src/backend/specs/SPEC-082-title-rebirth.md",
    blocks=[Block("title_rebirth", title)],
    hooks=[Hook(0x157DE, "303c00904eb841be", to_block="title_rebirth")],
    rom_data=[RomData(S_ROM, t * 32, "00" * 32, fix_tile(cell(*c))) for c, t in TILE_OF.items()],
)
