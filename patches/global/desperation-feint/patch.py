"""DESPERATION pode ser fintado com LP+LK — SPEC-067."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext,LeaPc,Raw
from charlib import SPECIAL_CHOSEN,ATTACK_STATE,HIT_SOUND,PROJ_SPAWN_X,shared_hook,player_sprite
from patchlib import Patch,Block

DESP_MOVES=[0x22,0x47,0x6a,0x8d,0xb5,0xd8,0x100,0x117,0x142,0x162,0x185,0x1a0]
start=[
 Ins("422e03b7","clr.b $3b7(a6)"),Ins("422e03ba","clr.b $3ba(a6)"),
 Ins("082e00010218","btst.b #$1, $218(a6)"),Branch("beq","out"),
 Ins("302e0062","move.w $62(a6), d0"),
 Ins("5340","subq.w #$1, d0"),Ins("0c40000b","cmpi.w #$b, d0"),Branch("bhi","out"),
 Ins("d040","add.w d0, d0"),LeaPc("moves",1),
 Ins("30310000","move.w (a1, d0.w), d0"),
 Ins("b06d0010","cmp.w $10(a5), d0"),Branch("bne","out"),
 Ins("3d6e022403b8","move.w $224(a6), $3b8(a6)"),
 Ins("3d6d002003bc","move.w $20(a5), $3bc(a6)"),
 Ins("1d7c000103b7","move.b #$1, $3b7(a6)"),
 Label("out"),JmpNext(SPECIAL_CHOSEN),
 Label("moves"),Raw(''.join(f'{m:04x}' for m in DESP_MOVES)),
]

def active_child(off,label):
 return [Ins("7000","moveq #$0, d0"),Ins(f"1028{off:04x}",f"move.b ${off:x}(a0), d0"),
         Branch("beq",label),Ins("e148","lsl.w #$8, d0"),
         Ins("083500000070","btst.b #$0, $70(a5, d0.w)"),Branch("bne","disarm"),Label(label)]

cancel=[
 Ins("4a2e03b7","tst.b $3b7(a6)"),Branch("bne","check"),JmpNext(ATTACK_STATE),
 Label("check"),
 Ins("082e00040060","btst.b #$4, $60(a6)"),Branch("bne","disarm"),
 Ins("4a6e006c","tst.w $6c(a6)"),Branch("ble","disarm"),
 Ins("302e0230","move.w $230(a6), d0"),Ins("b06e03bc","cmp.w $3bc(a6), d0"),Branch("bne","disarm"),
 Ins("4a2e021b","tst.b $21b(a6)"),Branch("beq","disarm"),
 *player_sprite(),*active_child(7,"second"),*active_child(8,"ready"),
 Ins("4a2e03ba","tst.b $3ba(a6)"),Branch("beq","out"),
 Branch("bra","perform"),
 Label("disarm"),Ins("422e03b7","clr.b $3b7(a6)"),Ins("422e03ba","clr.b $3ba(a6)"),
 Label("out"),JmpNext(ATTACK_STATE),
 Label("perform"),
 # Grabs de DESPERATION podem ter preparado o vinculo antes do dano.
 Ins("082e0004003f","btst.b #$4, $3f(a6)"),Branch("beq","refund"),
 Ins("48e7080a","movem.l d4/a4/a6, -(a7)"),
 Ins("2c6e0064","movea.l $64(a6), a6"),
 Ins("08ae0003003f","bclr.b #$3, $3f(a6)"),
 Ins("422e0240","clr.b $240(a6)"),Ins("022e006f0060","andi.b #$6f, $60(a6)"),
 *player_sprite(),Ins("49d0","lea.l (a0), a4"),
 Ins("7801","moveq #$1, d4"),Ins("4eb90001d41e","jsr $1d41e.l"),
 Ins("4cdf5010","movem.l (a7)+, d4/a4/a6"),
 Label("refund"),
 Ins("3d6e03b80224","move.w $3b8(a6), $224(a6)"),
 Ins("422e03b7","clr.b $3b7(a6)"),Ins("422e03ba","clr.b $3ba(a6)"),
 Ins("422e0a6e","clr.b $a6e(a6)"),
 Ins("08ae0004003f","bclr.b #$4, $3f(a6)"),
 Ins("426e0218","clr.w $218(a6)"),Ins("426e0274","clr.w $274(a6)"),
 Ins("426e0270","clr.w $270(a6)"),Ins("422e0247","clr.b $247(a6)"),
 Ins("422e0240","clr.b $240(a6)"),Ins("022e006f0060","andi.b #$6f, $60(a6)"),
 Ins("42ae0020","clr.l $20(a6)"),Ins("42ae0028","clr.l $28(a6)"),
 Ins("42ac0020","clr.l $20(a4)"),Ins("42ac0028","clr.l $28(a4)"),
 Ins("426e0030","clr.w $30(a6)"),Ins("426e0034","clr.w $34(a6)"),
 JmpAbs(0x1C2EA),
]
contact=[Ins("422803b7","clr.b $3b7(a0)"),Ins("422803ba","clr.b $3ba(a0)"),JmpNext(HIT_SOUND)]
projectile=[Ins("422e03b7","clr.b $3b7(a6)"),Ins("422e03ba","clr.b $3ba(a6)"),JmpNext(PROJ_SPAWN_X)]
PATCH=Patch(id="desperation-feint",title="DESPERATION: finta LP+LK antes do ataque, com Spirit restituido",
 spec="src/backend/specs/SPEC-067-desperation-feint.md",
 blocks=[Block("desp_prepare",start),Block("desp_feint",cancel),Block("desp_contact",contact),Block("desp_projectile",projectile)],
 hooks=[shared_hook(SPECIAL_CHOSEN,"desp_prepare"),shared_hook(ATTACK_STATE,"desp_feint"),
        shared_hook(HIT_SOUND,"desp_contact"),shared_hook(PROJ_SPAWN_X,"desp_projectile")])
