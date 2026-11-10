"""Robert: dash + dois chutes lanca em juggle por 20% — SPEC-068."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext,LeaPc,Raw
from charlib import MOVE_RECORD,only,shared_hook
from patchlib import Patch,Block,Hook

# Mesmo dano, animacao e propriedades baixas da rasteira do dash.
# A marca distingue o acerto EX na reacao; custo calculado na carga.
RECORD="0c0c000000080000471001b900000100"
record=[
 *only(2,MOVE_RECORD),
 Ins("0c2e000203be","cmpi.b #$2, $3be(a6)"),Branch("bne","normal"),
 Ins("0c6d00310020","cmpi.w #$31, $20(a5)"),Branch("bne","normal"),
 Ins("1d7c000303be","move.b #$3, $3be(a6)"),
 LeaPc("follow_record",0),JmpAbs(0x1D770),
 Label("normal"),
 Ins("422e03be","clr.b $3be(a6)"),
 Ins("0c6d003d0020","cmpi.w #$3d, $20(a5)"),Branch("bne","out"),
 Ins("7000","moveq #$0, d0"),Ins("102e0068","move.b $68(a6), d0"),
 Ins("020000a0","andi.b #$a0, d0"),Ins("0c0000a0","cmpi.b #$a0, d0"),Branch("bne","out"),
 Ins("1d7c000103be","move.b #$1, $3be(a6)"),
 LeaPc("ex_record",0),JmpAbs(0x1D770),
 Label("out"),JmpNext(MOVE_RECORD),Label("ex_record"),Raw(RECORD),
 Label("follow_record"),Raw("1c1c0000001400004f3001b200000200"),
]
cost=[
 Ins("1d6800050209","move.b $5(a0), $209(a6)"),
 Ins("0c6e00020062","cmpi.w #$2, $62(a6)"),Branch("bne","out"),
 Ins("4a2e03be","tst.b $3be(a6)"),Branch("beq","out"),
 Ins("0c6d003d0020","cmpi.w #$3d, $20(a5)"),Branch("bne","out"),
 Ins("48e7c000","movem.l d0-d1, -(a7)"),
 Ins("7000","moveq #$0, d0"),Ins("102e0256","move.b $256(a6), d0"),
 Ins("7205","moveq #$5, d1"),Ins("80c1","divu.w d1, d0"),
 Ins("1d400241","move.b d0, $241(a6)"),
 Ins("4cdf0003","movem.l (a7)+, d0-d1"),
 Label("out"),JmpAbs(0x1D7BE),
]
PATCH=Patch(id="dash-kick-juggle",title="Robert: dash + dois chutes, rasteira juggle de 20% Spirit",
 spec="src/backend/specs/SPEC-068-robert-dash-kick-juggle.md",
 blocks=[Block("robert_dash_ex",record),Block("robert_dash_ex_cost",cost)],
 hooks=[shared_hook(MOVE_RECORD,"robert_dash_ex"),Hook(0x1D7B8,"1d6800050209",to_block="robert_dash_ex_cost")])
