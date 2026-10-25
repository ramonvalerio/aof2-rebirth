"""Micky: chute forte agachado derruba — SPEC-049."""
from charlib import MOVE_TABLE
from patchlib import Data, Patch

PATCH = Patch(
    id="crouching-heavy-kick-knockdown",
    title="Micky: chute forte agachado derruba",
    spec="src/backend/specs/SPEC-049-micky-crouching-heavy-kick-knockdown.md",
    # Comando $39, golpe $0E9, animação $42B. Efeito de rasteira $15.
    data=[Data(MOVE_TABLE + 0x0E9 * 16 + 6, "00", "15")],
)
