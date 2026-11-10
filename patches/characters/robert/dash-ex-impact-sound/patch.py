"""Robert: estalo pesado no chute final do EX de dash — SPEC-073."""
from asm68k import Ins,Branch,Label,JmpNext
from charlib import HIT_SOUND,shared_hook
from patchlib import Patch,Block
sound=[
 Ins("0c6800020062","cmpi.w #$2, $62(a0)"),Branch("bne","out"),
 Ins("0c6800310230","cmpi.w #$31, $230(a0)"),Branch("bne","out"),
 Ins("0c28000303be","cmpi.b #$3, $3be(a0)"),Branch("bne","out"),
 Ins("700f","moveq #$f, d0"),Ins("c02e007c","and.b $7c(a6), d0"),
 Ins("0c000003","cmpi.b #$3, d0"),Branch("beq","out"),
 Ins("3d7c01400a5e","move.w #$140, $a5e(a6)"),
 Label("out"),JmpNext(HIT_SOUND),
]
PATCH=Patch(id="dash-ex-impact-sound",title="Robert: chute final do dash EX com estalo pesado",
 spec="src/backend/specs/SPEC-073-robert-dash-ex-impact-sound.md",
 blocks=[Block("robert_ex_impact",sound)],hooks=[shared_hook(HIT_SOUND,"robert_ex_impact")])
