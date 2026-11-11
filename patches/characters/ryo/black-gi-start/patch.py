"""Ryo: START na seleção escolhe o quimono preto — SPEC-083.

`global/start-select-flag` confirma START como B (cor 1) e liga `$3DA`.
A cor 1 (B, chute forte no layout da SPEC-002) é o quimono azul-claro com
detalhes vermelhos.

O pedido de paleta da luta ($A04C) usa a tabela $A060: bloco por personagem
e cor>>1 (Ryo: $4D para cores 0/1, $5A para 2/3). O carregador ($1D8A) lê
16 paletas de 48 bytes (RGB de 6 bits) em $80(a5) + bloco*$300 ($68000).
O bit 0 da cor escolhe a metade do bloco ($1B440).

Ryo com cor 1 e flag pede o bloco mágico $FE, que o carregador troca por
BLOCK abaixo: cópia do bloco $4D com a rampa azul da cor 1 trocada por preto.
Os retratos grandes (seleção e "select enemy") pedem $FE pela tabela $C96C.
"""
from asm68k import Branch, Ins, JmpAbs, Label, LeaPc, Raw
from charlib import (ENEMY_PORTRAIT, PORTRAIT_PALETTE, PORTRAIT_PALETTES, SELECT_PORTRAIT,
                     START_FLAG as FLAG, shared_hook, start_portrait, start_portrait_palette)
from patchlib import Block, Hook, Patch

MAGIC = 0xFE00          # bloco que nenhuma cena/personagem usa
RYO = 1
RYO_BLOCK = 0x4D

# Bloco $4D do Ryo ($76700): paletas 0-7 = cor 0, 8-15 = cor 1 (preta).
# Azul -> preto (R, G, B de 6 bits): (58,62,62)->(24,24,26), (46,58,62)->(18,18,20),
# (32,46,52)->(12,12,14), (22,32,38)->(8,8,8), (14,22,28)->(4,4,4).
BLOCK = [
    "002a003e3e343e3a2a3e2c1a3a24182e180e1e120a3e2e163e220a3614042c0c061c06000a0606141414242424303030",
    "0014003e3a2e3e34243c2a163620142a140a1a0e063e3a2e3e34243c2a163620142a140a3c2a160a06062a140a303030",
    "0020003e3a2e3e34243c2a163620142a140a1a0e063e3a3c3e323a3a2832301c282410183800000a0606200000303030",
    "1422003e3e3e3e3e2a3e3e183e360c3e28003e1c003a1400340c003e3e183e34143e2a103e200c3e16083e0c043e0000",
    "002a103e3e3e3e3e2a3e3e183e360c3e28003e1c003a1400340c003e3e3e2e3e3e183e3e0c363e00283e001c3e000c34",
    "0000223e3c363e36283c3022382818322014281612180a0a3a260e3218062806001a0000262a30181c220c1016000208",
    "0000223e3c363e36283c3022382818322014281612180a0a3a260e3218062806001a00003800002e201e22161a000208",
    "002a00002a00002a00002a00002a00002a00002a00002a00002a001c06002c0c063614043a20083e2a0e002a00002a00",
    "002a003e3a2e3e34243c2a163620142a140a1a0e0618181a1212140c0c0e0808080404041200002000003400003e0000",
    "0014003e3a2e3e34243c2a163620142a140a1a0e063e3a2e3e34243c2a163620142a140a3c2a160a06062a140a303030",
    "0020003e3a2e3e34243c2a163620142a140a1a0e063e3a3c3e323a3a2832301c282410183800000a0606200000303030",
    "1422003e3e3e3e3e2a3e3e183e360c3e28003e1c003a1400340c003e3e183e34143e2a103e200c3e16083e0c043e0000",
    "002a103e3e3e3e3e2a3e3e183e360c3e28003e1c003a1400340c003e3e3e2e3e3e183e3e0c363e00283e001c3e000c34",
    "080c043e3c363e36283c3022382818322014281612180a0a1212140c0c0e0808080404043e0a0a340000240404140202",
    "002a003e3c363e36283c3022382818322014281612180a0a1212140c0c0e0808080404043800002e201e22161a140202",
    "002a00002a00002a00002a00002a00002a00002a00002a00002a000404040808080c0c0e12121418181a002a00002a00",
]

# $A05E: move.w $a060(pc,d0.w),(a0)+ / rts (bloco de paleta do jogador a1).
request = [
    Ins("2f0a", "move.l a2, -(a7)"),
    Ins("45f90000a060", "lea.l $a060.l, a2"),
    Ins("30f20000", "move.w (a2, d0.w), (a0)+"),
    Ins("245f", "movea.l (a7)+, a2"),
    Ins(f"0c69{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a1)"),
    Branch("bne", "done"),
    Ins("0c6900010276", "cmpi.w #$1, $276(a1)"),
    Branch("bne", "done"),
    Ins(f"4a29{FLAG:04x}", f"tst.b ${FLAG:x}(a1)"),
    Branch("beq", "done"),
    Ins(f"317c{MAGIC:04x}fffe", f"move.w #${MAGIC:x}, -$2(a0)"),
    Label("done"),
    Ins("4e75", "rts"),
]

# $1D92: movea.l $80(a5),a2 / adda.l d1,a2 (x3)  (d1 = bloco << 8).
loader = [
    Ins(f"0c41{MAGIC:04x}", f"cmpi.w #${MAGIC:x}, d1"),
    Branch("bne", "normal"),
    LeaPc("palettes", 2),
    JmpAbs(0x1D9C),
    Label("normal"),
    Ins("246d0080", "movea.l $80(a5), a2"),
    Ins("d5c1", "adda.l d1, a2"),
    Ins("d5c1", "adda.l d1, a2"),
    Ins("d5c1", "adda.l d1, a2"),
    JmpAbs(0x1D9C),
    Label("palettes"),
    Raw("".join(BLOCK)),
]

PORTRAIT_HEX = "".join(BLOCK)[PORTRAIT_PALETTES * 2:(PORTRAIT_PALETTES + 2 * 0x30) * 2]

PATCH = Patch(
    id="black-gi-start",
    title="START na seleção: quimono preto com detalhes vermelhos",
    spec="src/backend/specs/SPEC-083-ryo-black-gi-start.md",
    blocks=[Block("palette_request", request), Block("palette_loader", loader),
            Block("select_portrait", start_portrait(RYO_BLOCK, MAGIC >> 8, SELECT_PORTRAIT)),
            Block("enemy_portrait", start_portrait(RYO_BLOCK, MAGIC >> 8, ENEMY_PORTRAIT)),
            Block("portrait_palette", start_portrait_palette(MAGIC >> 8, PORTRAIT_HEX))],
    hooks=[
        Hook(0xA05E, "30fb00004e75", to_block="palette_request"),
        Hook(0x1D92, "246d0080d5c1d5c1d5c1", to_block="palette_loader"),
        shared_hook(SELECT_PORTRAIT, "select_portrait"),
        shared_hook(ENEMY_PORTRAIT, "enemy_portrait"),
        shared_hook(PORTRAIT_PALETTE, "portrait_palette"),
    ],
)
