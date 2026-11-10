"""Prioridade global dos DESPERATION â€” SPEC-080."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext,LeaPc,Raw
from charlib import SPECIAL_CHOSEN,PROJ_SPAWN_X,shared_hook
from patchlib import Patch,Block,Hook

MOVES=(0x22,0x47,0x6a,0x8d,0xb5,0xd8,0x100,0x117,0x142,0x162,0x185,0x1a0)
# Actor $3C3 active, $3C4 command snapshot. Projectile $80 persists until recycle.
start=[Ins("422e03c3","clr.b $3c3(a6)"),
 Ins("302e0062","move.w $62(a6), d0"),Ins("5340","subq.w #$1, d0"),
 Ins("0c40000b","cmpi.w #$b, d0"),Branch("bhi","out"),Ins("d040","add.w d0, d0"),
 LeaPc("moves",1),Ins("30310000","move.w (a1, d0.w), d0"),
 Ins("b06d0010","cmp.w $10(a5), d0"),Branch("bne","out"),
 Ins("1d7c000103c3","move.b #$1, $3c3(a6)"),
 Ins("3d6d002003c4","move.w $20(a5), $3c4(a6)"),
 Label("out"),JmpNext(SPECIAL_CHOSEN),Label("moves"),Raw(''.join(f'{v:04x}' for v in MOVES))]

def active(reg,fail):
 n={'a0':'28','a1':'29'}[reg]
 return [Ins(f"4a{n}03c3",f"tst.b $3c3({reg})"),Branch("beq",fail),
 Ins(f"0c{n}00030040",f"cmpi.b #$3, $40({reg})"),Branch("bne",fail),
 Ins(f"302{n[-1]}0230",f"move.w $230({reg}), d0"),
 Ins(f"b06{n[-1]}03c4",f"cmp.w $3c4({reg}), d0"),Branch("bne",fail)]

spawn=[Ins("42280080","clr.b $80(a0)"),Ins("2f08","move.l a0, -(a7)"),
 Ins("41d6","lea.l (a6), a0"),*active('a0','out'),
 Ins("2057","movea.l (a7), a0"),Ins("117c00010080","move.b #$1, $80(a0)"),
 Label("out"),Ins("205f","movea.l (a7)+, a0"),JmpNext(PROJ_SPAWN_X)]

# Before geometric overlap: only reject body contacts, never consume an attack.
# Body child -> sprite -> actor, using native $0B parent IDs.
filter_hit=[Ins("48e7c0c0","movem.l d0-d1/a0-a1, -(a7)"),
 LeaPc("check",1),Ins("4e91","jsr (a1)"),Ins("4a00","tst.b d0"),Branch("beq","reject_pair"),
 Ins("c94e","exg.l a4, a6"),LeaPc("check",1),Ins("4e91","jsr (a1)"),
 Ins("c94e","exg.l a4, a6"),Ins("4a00","tst.b d0"),Branch("beq","reject_pair"),
 Ins("4cdf0303","movem.l (a7)+, d0-d1/a0-a1"),
 Ins("1202","move.b d2, d1"),Ins("c22c006b","and.b $6b(a4), d1"),JmpAbs(0xF6B9E),
 Label("reject_pair"),Ins("4cdf0303","movem.l (a7)+, d0-d1/a0-a1"),JmpAbs(0xF6BD6),
 Label("check"),
 Ins("082c0007006f","btst.b #$7, $6f(a4)"),Branch("beq","body"),
 Ins("7001","moveq #$1, d0"),Ins("4e75","rts"),Label("body"),
 Ins("7000","moveq #$0, d0"),Ins("102c000b","move.b $b(a4), d0"),Ins("e148","lsl.w #$8, d0"),
 Ins("41f50000","lea.l (a5, d0.w), a0"),
 Ins("102c0002","move.b $2(a4), d0"),
 Ins("b0280003","cmp.b $3(a0), d0"),Branch("beq","hurtbox"),
 Ins("b0280004","cmp.b $4(a0), d0"),Branch("beq","hurtbox"),
 Ins("b0280005","cmp.b $5(a0), d0"),Branch("beq","hurtbox"),
 Ins("b0280006","cmp.b $6(a0), d0"),Branch("beq","hurtbox"),
 Ins("7001","moveq #$1, d0"),Ins("4e75","rts"),Label("hurtbox"),
 Ins("1028000b","move.b $b(a0), d0"),Ins("e148","lsl.w #$8, d0"),
 Ins("43f50080","lea.l -$80(a5, d0.w), a1"),
 Ins("b3fc00109280","cmpa.l #$109280, a1"),Branch("beq","player"),
 Ins("b3fc00109380","cmpa.l #$109380, a1"),Branch("bne","pass"),
 Label("player"),*active('a1','pass'),
 Ins("082e0007006f","btst.b #$7, $6f(a6)"),Branch("beq","reject"),
 Ins("4a2e0080","tst.b $80(a6)"),Branch("bne","pass"),
 Label("reject"),Ins("7000","moveq #$0, d0"),Ins("4e75","rts"),
 Label("pass"),Ins("7001","moveq #$1, d0"),Ins("4e75","rts")]

# Native projectile handler sees both contacts before resolving their strength.
# Both tagged -> native dissipation for both, irrespective of size/strength.
clash=[Ins("2f08","move.l a0, -(a7)"),Ins("41f51000","lea.l (a5, d1.w), a0"),
 Ins("4a2e0080","tst.b $80(a6)"),Branch("beq","other"),
 Ins("4a280080","tst.b $80(a0)"),Branch("beq","win"),Branch("bra","lose"),
 Label("other"),Ins("4a280080","tst.b $80(a0)"),Branch("beq","native"),
 Label("lose"),Ins("205f","movea.l (a7)+, a0"),JmpAbs(0x22DCE),
 Label("win"),Ins("205f","movea.l (a7)+, a0"),JmpAbs(0x22DC4),
 Label("native"),Ins("205f","movea.l (a7)+, a0"),
 Ins("082e0004005f","btst.b #$4, $5f(a6)"),JmpAbs(0x22DA8)]

throw=[Ins("48e78080","movem.l d0/a0, -(a7)"),Ins("206e0064","movea.l $64(a6), a0"),
 *active('a0','native'),Ins("4cdf0101","movem.l (a7)+, d0/a0"),
 Ins("003c0004","ori.b #$4, ccr"),Ins("4e75","rts"),
 Label("native"),Ins("4cdf0101","movem.l (a7)+, d0/a0"),
 Ins("082e00010a68","btst.b #$1, $a68(a6)"),Ins("4e75","rts")]
PATCH=Patch(id="desperation-priority",title="DESPERATION invencivel; projeteis DESPERATION se anulam",
 spec="src/backend/specs/SPEC-080-desperation-priority.md",
 blocks=[Block('desp_start',start),Block('desp_spawn',spawn),Block('desp_filter',filter_hit),Block('desp_clash',clash),Block('desp_throw',throw)],
 hooks=[shared_hook(SPECIAL_CHOSEN,'desp_start'),shared_hook(PROJ_SPAWN_X,'desp_spawn'),
 Hook(0xF6B98,'1202c22c006b',to_block='desp_filter'),
 Hook(0x22DA2,'082e0004005f',to_block='desp_clash'),
 Hook(0x1DC14,'082e00010a68',to_block='desp_throw')])
