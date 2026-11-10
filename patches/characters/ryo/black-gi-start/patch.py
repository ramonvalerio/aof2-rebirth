"""Ryo: START na seleção escolhe o quimono preto — SPEC-083.

A seleção ($C77E) converte o botão em cor: A 0, B 1, C 2, D 3 ($C84C), salva
em $276 do registro do jogador. A cor 1 (B, chute forte no layout da
SPEC-002) é o quimono azul-claro com detalhes vermelhos.

O pedido de paleta da luta ($A04C) usa a tabela $A060: bloco por personagem
e cor>>1 (Ryo: $4D para cores 0/1, $5A para 2/3). O carregador ($1D8A) lê
16 paletas de 48 bytes (RGB de 6 bits) em $80(a5) + bloco*$300 ($68000).
O bit 0 da cor escolhe a metade do bloco ($1B440).

START (sem A-D) confirma como B e liga a flag $3DA no registro. Ryo com cor
1 e flag pede o bloco mágico $FE, que o carregador troca por BLOCK abaixo:
cópia do bloco $4D com a rampa azul do quimono da cor 1 trocada por preto.
"""
from asm68k import Branch, Ins, JmpAbs, Label, LeaPc, Raw
from patchlib import Block, Hook, Patch

FLAG = 0x3DA            # registro do jogador, faixa livre $39B-$3DE
MAGIC = 0xFE00          # bloco que nenhuma cena/personagem usa
P1_RECORD = 0x109280
RYO = 1

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

# $C7CE: andi.w #$f0,d0 / beq.w $c84a (confirmação da seleção).
select = [
    Ins("024000f0", "andi.w #$f0, d0"),
    Ins("4a2e0029", "tst.b $29(a6)"),
    Branch("bne", "check"),                      # continue: mantém cor e flag
    Ins("226e001c", "movea.l $1c(a6), a1"),
    Ins("4a40", "tst.w d0"),
    Branch("beq", "try_start"),
    Ins(f"4229{FLAG:04x}", f"clr.b ${FLAG:x}(a1)"),     # A-D: cor normal
    Branch("bra", "check"),
    Label("try_start"),
    Ins("12390010fdad", "move.b $10fdad.l, d1"),         # bordas de START/SELECT
    Ins(f"b3fc{P1_RECORD:08x}", f"cmpa.l #${P1_RECORD:x}, a1"),
    Branch("beq", "p1"),
    Ins("e409", "lsr.b #$2, d1"),                         # P2: bit 2
    Label("p1"),
    Ins("08010000", "btst.b #$0, d1"),
    Branch("beq", "none"),
    Ins(f"137c0001{FLAG:04x}", f"move.b #$1, ${FLAG:x}(a1)"),
    Ins("7020", "moveq #$20, d0"),                       # confirma como B (cor 1)
    Label("check"),
    Ins("4a40", "tst.w d0"),
    Branch("beq", "none"),
    JmpAbs(0xC7D6),
    Label("none"),
    JmpAbs(0xC84A),
]

# $C75E: move.w #$10,d0 / bra.w $c7f4 (tempo esgotado confirma como A).
timeout = [
    Ins("226e001c", "movea.l $1c(a6), a1"),
    Ins(f"4229{FLAG:04x}", f"clr.b ${FLAG:x}(a1)"),
    Ins("303c0010", "move.w #$10, d0"),
    JmpAbs(0xC7F4),
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

# Retrato grande: tabela $C96C (bloco, metade) por personagem e cor; $D81A
# copia as paletas 5 e 6 da metade (+$180 se metade 1, +$F0 = 5 paletas).
# Bloco $4D é só do Ryo; metade 1 = cor 1. Com a flag, pede o bloco $FE.
PORTRAIT_PALETTES = 0x180 + 5 * 0x30            # paletas 5-6 da cor 1


def portrait_request(resume):
    """Substitui: move.w (a0)+,d5 / move.w (a0),d6 (+ a instrução seguinte)."""
    return [
        Ins("3a18", "move.w (a0)+, d5"),
        Ins("3c10", "move.w (a0), d6"),
        Ins("0c45004d", "cmpi.w #$4d, d5"),
        Branch("bne", "done"),
        Ins("0c460001", "cmpi.w #$1, d6"),
        Branch("bne", "done"),
        Ins("2f08", "move.l a0, -(a7)"),
        Ins("206e001c", "movea.l $1c(a6), a0"),          # registro do jogador
        Ins(f"4a28{FLAG:04x}", f"tst.b ${FLAG:x}(a0)"),
        Ins("205f", "movea.l (a7)+, a0"),
        Branch("beq", "done"),
        Ins(f"3a3c{MAGIC >> 8:04x}", f"move.w #${MAGIC >> 8:x}, d5"),
        Label("done"),
        *resume,
    ]


# $C962: move.w (a0)+,d5 / move.w (a0),d6 / bsr.w $d81a (seguido de rts).
select_portrait = portrait_request([JmpAbs(0xD81A)])

# $E1B6: move.w (a0)+,d5 / move.w (a0),d6 / movem.l a6,-(a7) (retrato com a cor do cursor).
enemy_portrait = portrait_request([Ins("48e70002", "movem.l a6, -(a7)"), JmpAbs(0xE1BE)])

# $D828: movea.l $80(a5),a1 / lsl.w #8,d5 / adda.w d5,a1 (x3).
portrait_loader = [
    Ins(f"0c45{MAGIC >> 8:04x}", f"cmpi.w #${MAGIC >> 8:x}, d5"),
    Branch("bne", "normal"),
    LeaPc("palettes", 1),
    Ins(f"92fc{PORTRAIT_PALETTES:04x}", f"suba.w #${PORTRAIT_PALETTES:x}, a1"),  # $D81A soma de volta
    JmpAbs(0xD834),
    Label("normal"),
    Ins("226d0080", "movea.l $80(a5), a1"),
    Ins("e14d", "lsl.w #$8, d5"),
    Ins("d2c5", "adda.w d5, a1"),
    Ins("d2c5", "adda.w d5, a1"),
    Ins("d2c5", "adda.w d5, a1"),
    JmpAbs(0xD834),
    Label("palettes"),
    Raw("".join(BLOCK)[PORTRAIT_PALETTES * 2:(PORTRAIT_PALETTES + 2 * 0x30) * 2]),
]

PATCH = Patch(
    id="black-gi-start",
    title="START na seleção: quimono preto com detalhes vermelhos",
    spec="src/backend/specs/SPEC-083-ryo-black-gi-start.md",
    blocks=[Block("select_start", select), Block("select_timeout", timeout),
            Block("palette_request", request), Block("palette_loader", loader),
            Block("select_portrait", select_portrait), Block("enemy_portrait", enemy_portrait),
            Block("portrait_loader", portrait_loader)],
    hooks=[
        Hook(0xC7CE, "024000f067000076", to_block="select_start"),
        Hook(0xC75E, "303c001060000090", to_block="select_timeout"),
        Hook(0xA05E, "30fb00004e75", to_block="palette_request"),
        Hook(0x1D92, "246d0080d5c1d5c1d5c1", to_block="palette_loader"),
        Hook(0xC962, "3a183c1061000eb2", to_block="select_portrait"),
        Hook(0xE1B6, "3a183c1048e70002", to_block="enemy_portrait"),
        Hook(0xD828, "226d0080e14dd2c5d2c5d2c5", to_block="portrait_loader"),
    ],
)
