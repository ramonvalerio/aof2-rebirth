"""Robert: frente + LK, subida normal e descida overhead — SPEC-069."""
from asm68k import Ins,Branch,Label,JmpNext
from charlib import ANIM_FRAME,shared_hook
from patchlib import Patch,Block

phase=[
 # $1B1 e exclusivo do chute forte perto do Robert, escolhido por frente+LK.
 Ins("0c6e01b10054","cmpi.w #$1b1, $54(a6)"),Branch("beq","robert"),
 JmpNext(ANIM_FRAME),Label("robert"),
 Ins("48e7c080","movem.l d0-d1/a0, -(a7)"),
 Ins("323c4f30","move.w #$4f30, d1"),
 Ins("0c2e0003005a","cmpi.b #$3, $5a(a6)"),Branch("bcs","chosen"),
 Ins("323c4b20","move.w #$4b20, d1"),Label("chosen"),
 Ins("41d6","lea.l (a6), a0"),
 Ins("7000","moveq #$0, d0"),Ins("10280007","move.b $7(a0), d0"),Branch("beq","second"),
 Ins("e148","lsl.w #$8, d0"),Ins("3b81006a","move.w d1, $6a(a5, d0.w)"),
 Label("second"),Ins("7000","moveq #$0, d0"),Ins("10280008","move.b $8(a0), d0"),Branch("beq","done"),
 Ins("e148","lsl.w #$8, d0"),Ins("3b81006a","move.w d1, $6a(a5, d0.w)"),
 Label("done"),Ins("4cdf0103","movem.l (a7)+, d0-d1/a0"),JmpNext(ANIM_FRAME),
]
PATCH=Patch(id="rising-kick-overhead",title="Robert: frente+LK dois hits perto, overhead somente na descida",
 spec="src/backend/specs/SPEC-069-robert-rising-kick-overhead.md",
 blocks=[Block("robert_kick_phase",phase)],hooks=[shared_hook(ANIM_FRAME,"robert_kick_phase")])
