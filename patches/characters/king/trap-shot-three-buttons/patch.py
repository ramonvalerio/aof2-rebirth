"""King: três versões do Trap Shot pelos chutes — SPEC-046."""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import MOVE_TABLE, SPECIAL_CHOSEN, only, shared_hook
from patchlib import Block, Data, Patch


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
    Ins("0c6d00d50010", "cmpi.w #$d5, $10(a5)"),
    Branch("bcs", "out"),
    Ins("0c6d00d70010", "cmpi.w #$d7, $10(a5)"),
    Branch("bhi", "out"),
    Ins("082e00030218", "btst.b #$3, $218(a6)"),
    Branch("bne", "strong"),
    Ins("082e00000218", "btst.b #$0, $218(a6)"),
    Branch("bne", "medium"),
    *pick(0xD7, 1, 0x80),
    Label("medium"),
    *pick(0xD6, 2, 0xA0),
    Label("strong"),
    *pick(0xD5, 3, 0xC0)[:-1],
    Label("out"),
    JmpNext(SPECIAL_CHOSEN),
]

PATCH = Patch(
    id="trap-shot-three-buttons",
    title="King: Trap Shot — chute fraco = fraco, chute forte = médio, dois chutes = forte",
    spec="src/backend/specs/SPEC-046-king-trap-shot-three-buttons.md",
    blocks=[Block("trap-shot_buttons", choose)],
    hooks=[shared_hook(SPECIAL_CHOSEN, "trap-shot_buttons")],
    # A versão original $D7 é falha. Torna-a funcional: sequência da média,
    # dano 12, tontura 3, custo zero como os especiais grátis do projeto.
    data=[Data(MOVE_TABLE + 0xD7 * 16,
               "22220000b31400004f3003b200000200",
               "0c0c030300000c004f30800800001000")],
)
