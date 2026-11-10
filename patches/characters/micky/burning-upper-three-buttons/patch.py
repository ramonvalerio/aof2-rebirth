"""Micky: Burning Upper LP/HP/dois socos, EX com juggle — SPEC-077."""
from asm68k import Ins,Branch,Label,JmpNext
from charlib import MICKY,SPECIAL_CHOSEN,CMD_STEP,PROJ_SPAWN_X,only,shared_hook
from patchlib import Patch,Block

def pick(mid,level,gauge):
 return [Ins(f"3b7c{mid:04x}0010",f"move.w #${mid:x}, $10(a5)"),
         Ins(f"197c{level:04x}005c",f"move.b #${level:x}, $5c(a4)"),
         Ins(f"1d7c{gauge:04x}023f",f"move.b #${gauge:x}, $23f(a6)"),Branch("bra","out")]
choose=[
 *only(MICKY,SPECIAL_CHOSEN),
 Ins("422e03c1","clr.b $3c1(a6)"),
 Ins("082e00010218","btst.b #$1, $218(a6)"),Branch("beq","out"),
 Ins("0c6d00f30010","cmpi.w #$f3, $10(a5)"),Branch("bcs","out"),
 Ins("0c6d00f50010","cmpi.w #$f5, $10(a5)"),Branch("bhi","out"),
 Ins("082e00020218","btst.b #$2, $218(a6)"),Branch("bne","ex"),
 Ins("082e00000218","btst.b #$0, $218(a6)"),Branch("bne","medium"),
 *pick(0xf5,1,0x80),
 Label("medium"),*pick(0xf4,2,0xa0),
 Label("ex"),Ins("1d7c000103c1","move.b #$1, $3c1(a6)"),*pick(0xf3,3,0xc0)[:-1],
 Label("out"),JmpNext(SPECIAL_CHOSEN),
]
command=[
 *only(MICKY,CMD_STEP),
 Ins("0c450040","cmpi.w #$40, d5"),Branch("bne","out"),
 Ins("0c4401b8","cmpi.w #$1b8, d4"),Branch("bne","out"),
 Ins("020000bf","andi.b #$bf, d0"),
 Label("out"),JmpNext(CMD_STEP),
]
# Transporta a propriedade no projetil: nao depende da acao atual do dono
# quando ele atingir. Bit 7 do efeito e removido pelo dispatcher nativo.
spawn=[
 *only(MICKY,PROJ_SPAWN_X),
 Ins("0c6e00400230","cmpi.w #$40, $230(a6)"),Branch("bne","out"),
 Ins("4a2e03c1","tst.b $3c1(a6)"),Branch("beq","out"),
 Ins("08e800070037","bset.b #$7, $37(a0)"),
 Label("out"),JmpNext(PROJ_SPAWN_X),
]
PATCH=Patch(id="burning-upper-three-buttons",title="Micky: Burning Upper fraco, medio e EX de dois socos com juggle",
 spec="src/backend/specs/SPEC-077-micky-burning-upper-three-buttons.md",
 blocks=[Block("micky_burning_buttons",choose),Block("micky_burning_command",command),Block("micky_burning_projectile",spawn)],
 hooks=[shared_hook(SPECIAL_CHOSEN,"micky_burning_buttons"),shared_hook(CMD_STEP,"micky_burning_command"),shared_hook(PROJ_SPAWN_X,"micky_burning_projectile")])
