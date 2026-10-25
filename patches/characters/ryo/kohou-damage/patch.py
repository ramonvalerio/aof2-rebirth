"""Ryo: Kohou forte com referência de 9 por hit, fraco 8 — SPEC-054."""
from charlib import MOVE_TABLE
from patchlib import Data, Patch

PATCH = Patch(
    id="kohou-damage",
    title="Ryo: Kohou forte 18 total (9 por hit), fraco 8 — referência",
    spec="src/backend/specs/SPEC-054-ryo-kohou-damage.md",
    # Escala medida ~0,8: base 11 -> referência 9 por hit; chip 3 -> 2.
    # Fraco $024 já tem base 10/2, referência 8/2: não precisa mudar.
    data=[Data(MOVE_TABLE + 0x023 * 16, "10100404", "0b0b0303")],
)
