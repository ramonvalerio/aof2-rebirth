"""Eiji: chute forte agachado derruba — SPEC-050."""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import HIT_SOUND, shared_hook
from patchlib import Block, Patch

# Atributos já copiados: a0 = atacante, a6 = defensor. O primeiro
# contato ainda tem $247 = 1; o segundo tem 0 (também zerado por DE em q4).
finish = [
    Ins("0c6800030062", "cmpi.w #$3, $62(a0)"),
    Branch("bne", "out"),
    Ins("0c6800390230", "cmpi.w #$39, $230(a0)"),
    Branch("bne", "out"),
    Ins("4a280247", "tst.b $247(a0)"),
    Branch("bne", "out"),
    Ins("1d7c0015024b", "move.b #$15, $24b(a6)"),
    Label("out"),
    JmpNext(HIT_SOUND),
]

PATCH = Patch(
    id="crouching-heavy-kick-knockdown",
    title="Eiji: chute forte agachado mantém 2 hits e derruba no segundo",
    spec="src/backend/specs/SPEC-050-eiji-crouching-heavy-kick-knockdown.md",
    blocks=[Block("eiji_sweep_finish", finish)],
    hooks=[shared_hook(HIT_SOUND, "eiji_sweep_finish")],
)
