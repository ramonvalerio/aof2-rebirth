"""King: três versões do Moushuukyaku pelos chutes — SPEC-045."""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import SPECIAL_CHOSEN, only, shared_hook
from patchlib import Block, Patch


def pick(move, level, gauge):
    return [
        Ins(f"3b7c{move:04x}0010", f"move.w #${move:x}, $10(a5)"),
        Ins(f"197c{level:04x}005c", f"move.b #${level:x}, $5c(a4)"),
        Ins(f"1d7c00{gauge:02x}023f", f"move.b #${gauge:x}, $23f(a6)"),
        Branch("bra", "out"),
    ]


choose = [
    *only(6, SPECIAL_CHOSEN),
    Ins("082e00010218", "btst.b #$1, $218(a6)"),
    Branch("beq", "out"),
    Ins("0c6d00d90010", "cmpi.w #$d9, $10(a5)"),
    Branch("bcs", "out"),
    Ins("0c6d00db0010", "cmpi.w #$db, $10(a5)"),
    Branch("bhi", "out"),
    Ins("082e00030218", "btst.b #$3, $218(a6)"),
    Branch("bne", "strong"),
    Ins("082e00000218", "btst.b #$0, $218(a6)"),
    Branch("bne", "medium"),
    *pick(0xDB, 1, 0x80),
    Label("medium"),
    *pick(0xDA, 2, 0xA0),
    Label("strong"),
    *pick(0xD9, 3, 0xC0)[:-1],
    Label("out"),
    JmpNext(SPECIAL_CHOSEN),
]

PATCH = Patch(
    id="moushuukyaku-three-buttons",
    title="King: Moushuukyaku — chute fraco = fraco, chute forte = médio, dois chutes = forte",
    spec="src/backend/specs/SPEC-045-king-moushuukyaku-three-buttons.md",
    blocks=[Block("moushuukyaku_buttons", choose)],
    hooks=[shared_hook(SPECIAL_CHOSEN, "moushuukyaku_buttons")],
)
