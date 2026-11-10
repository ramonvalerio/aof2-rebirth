"""John: Overdrive Kick EX lanca em juggle no ultimo contato — SPEC-074."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext
from charlib import SPECIAL_CHOSEN,JOHN,only,shared_hook
from patchlib import Patch,Block
choose=[
 *only(JOHN,SPECIAL_CHOSEN),
 Ins("422e03bf","clr.b $3bf(a6)"),
 Ins("082e00010218","btst.b #$1, $218(a6)"),Branch("beq","out"),
 Ins("0c6d01210010","cmpi.w #$121, $10(a5)"),Branch("bcs","out"),
 Ins("0c6d01230010","cmpi.w #$123, $10(a5)"),Branch("bhi","out"),
 Ins("082e00030218","btst.b #$3, $218(a6)"),Branch("beq","out"),
 Ins("3b7c01210010","move.w #$121, $10(a5)"),
 Ins("197c0003005c","move.b #$3, $5c(a4)"),
 Ins("1d7c00c0023f","move.b #$c0, $23f(a6)"),
 Ins("1d7c000103bf","move.b #$1, $3bf(a6)"),
 Label("out"),JmpNext(SPECIAL_CHOSEN),
]
PATCH=Patch(id="overdrive-ex-juggle",title="John: Overdrive Kick EX lanca em juggle apenas no ultimo hit",
 spec="src/backend/specs/SPEC-074-john-overdrive-ex-juggle.md",
 blocks=[Block("john_overdrive_ex",choose)],
 hooks=[shared_hook(SPECIAL_CHOSEN,"john_overdrive_ex")])
