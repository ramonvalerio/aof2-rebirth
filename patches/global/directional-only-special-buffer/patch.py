"""Buffer direcional adicional apenas durante travas — SPEC-052.

Não modifica CMD_STEP, cancels, hitstop de normais ou buffers existentes.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

reader = [
    Ins("122e0270", "move.b $270(a6), d1"),
    Ins("0c2e000f0040", "cmpi.b #$f, $40(a6)"),
    Branch("beq", "directions"),
    Ins("0c2e00030040", "cmpi.b #$3, $40(a6)"),
    Branch("bne", "original"),
    Ins("0c6e00400230", "cmpi.w #$40, $230(a6)"),
    Branch("bcs", "original"),
    Label("directions"),
    # Só a cópia lida pelo detector é filtrada; $270 não é modificado.
    Ins("0201000f", "andi.b #$f, d1"),
    Label("original"),
    Ins("302efe62", "move.w -$19e(a6), d0"),
    JmpAbs(0x1DFA8),
]

PATCH = Patch(
    id="directional-only-special-buffer",
    title="Buffer direcional na defesa e recuperação, preservando todos os cancels",
    spec="src/backend/specs/SPEC-052-directional-only-special-buffer.md",
    blocks=[Block("directional_reader", reader)],
    hooks=[Hook(0x1DFA0, "122e0270302efe62", to_block="directional_reader")],
)
