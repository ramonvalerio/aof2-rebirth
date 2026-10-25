"""Mr. Big: três versões do Cross Diving pelos chutes — SPEC-048."""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import SPECIAL_CHOSEN, CMD_STEP, QCF_PUNCH_STEP, only, shared_hook
from patchlib import Block, Data, Patch


def pick(move, level, gauge):
    return [
        Ins(f"3b7c{move:04x}0010", f"move.w #${move:x}, $10(a5)"),
        Ins(f"197c{level:04x}005c", f"move.b #${level:x}, $5c(a4)"),
        Ins(f"1d7c00{gauge:02x}023f", f"move.b #${gauge:x}, $23f(a6)"),
        Branch("bra", "out"),
    ]


choose = [
    *only(9, SPECIAL_CHOSEN),
    Ins("082e00010218", "btst.b #$1, $218(a6)"),
    Branch("beq", "out"),
    Ins("0c6d013f0010", "cmpi.w #$13f, $10(a5)"),
    Branch("bcs", "out"),
    Ins("0c6d01410010", "cmpi.w #$141, $10(a5)"),
    Branch("bhi", "out"),
    Ins("082e00020218", "btst.b #$2, $218(a6)"),
    Branch("bne", "strong"),
    Ins("082e00000218", "btst.b #$0, $218(a6)"),
    Branch("bne", "medium"),
    *pick(0x141, 1, 0x80),
    Label("medium"),
    *pick(0x140, 2, 0xA0),
    Label("strong"),
    *pick(0x13F, 3, 0xC0)[:-1],
    Label("out"),
    JmpNext(SPECIAL_CHOSEN),
]

command = [
    *only(9, CMD_STEP),
    Ins(f"0c44{QCF_PUNCH_STEP:04x}", f"cmpi.w #${QCF_PUNCH_STEP:x}, d4"),
    Branch("bne", "out"),
    # O par de socos chega como $50; ignora a marca do uppercut.
    Ins("020000bf", "andi.b #$bf, d0"),
    Label("out"),
    JmpNext(CMD_STEP),
]

PATCH = Patch(
    id="cross-diving-three-buttons",
    title="Mr. Big: Cross Diving — soco fraco = fraco, soco forte = médio, dois socos = forte",
    spec="src/backend/specs/SPEC-048-mr-big-cross-diving-three-buttons.md",
    blocks=[Block("cross_diving_buttons", choose), Block("cross_diving_command", command)],
    hooks=[shared_hook(SPECIAL_CHOSEN, "cross_diving_buttons"),
           shared_hook(CMD_STEP, "cross_diving_command")],
    # Slot de Mr. Big, comando $43: HCF ($618) -> QCF ($1A0).
    data=[Data(0x25D04 + 8 * 0x20 + 3 * 2, "0618", "01a0")],
)
