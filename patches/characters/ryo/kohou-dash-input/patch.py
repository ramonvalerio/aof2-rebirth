"""Ryo: Kohou tolerante a baixo-frente durante dash — SPEC-057."""
from asm68k import Branch, Ins, JmpAbs, JmpNext, Label
from charlib import CMD_STEP, RYO, only, shared_hook
from patchlib import Block, Patch

command = [
    *only(RYO, CMD_STEP),
    Ins("0c450047", "cmpi.w #$47, d5"),
    Branch("bne", "out"),
    Ins("0c2e00100040", "cmpi.b #$10, $40(a6)"),
    Branch("beq", "dash"),
    Ins("0c2e00110040", "cmpi.b #$11, $40(a6)"),
    Branch("bne", "out"),
    Label("dash"),
    Ins("0c440258", "cmpi.w #$258, d4"),
    Branch("beq", "down"),
    Ins("0c440260", "cmpi.w #$260, d4"),
    Branch("bne", "out"),
    Ins("0c01001a", "cmpi.b #$1a, d1"),
    Branch("bne", "out"),
    JmpAbs(0x1E0E0),
    Label("down"),
    # Frente já registrada: diagonal + soco fresco concluem no mesmo frame.
    Ins("0c01001a", "cmpi.b #$1a, d1"),
    Branch("bne", "direction"),
    JmpAbs(0x1E0E0),
    Label("direction"),
    # Na etapa de baixo, ignora apenas frente. Cima/trás/botões não mudam.
    Ins("020000f7", "andi.b #$f7, d0"),
    Label("out"),
    JmpNext(CMD_STEP),
]

PATCH = Patch(
    id="kohou-dash-input",
    title="Ryo: Kohou facilitado durante o dash (aceita baixo-frente + soco)",
    spec="src/backend/specs/SPEC-057-ryo-kohou-dash-input.md",
    blocks=[Block("kohou_dash_command", command)],
    hooks=[shared_hook(CMD_STEP, "kohou_dash_command")],
)
