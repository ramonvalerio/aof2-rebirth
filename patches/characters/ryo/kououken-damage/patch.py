"""Kou'ouken: referência 16/12/8 em acerto, 4/2/2 na defesa — SPEC-053."""
from charlib import MOVE_TABLE
from patchlib import Data, Patch

# Na condição medida, a escala nativa é aproximadamente 0,8.
# Bases 20/15/10 produzem referência 16/12/8. Fraco já usa 10/3.
PATCH = Patch(
    id="kououken-damage",
    title="Ryo: Kou'ouken com dano reduzido (referência forte 16, médio 12, fraco 8)",
    spec="src/backend/specs/SPEC-053-ryo-kououken-damage.md",
    data=[
        Data(MOVE_TABLE + 0x011 * 16, "24240909", "14140505"),
        Data(MOVE_TABLE + 0x012 * 16, "14140505", "0f0f0303"),
    ],
)
