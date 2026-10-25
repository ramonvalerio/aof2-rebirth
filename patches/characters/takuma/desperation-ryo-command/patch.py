"""desperation-ryo-command (Takuma) — SPEC-028.

O DESPERATION (comando $45, original v v> -> <- -> + A+B, lista +$966)
sai com o comando do Ryo: v v> -> v> v <v <- + C (lista +$A0E). A lista
original não muda.
"""
from charlib import RYO_DESPERATION, TAKUMA, desperation_slot
from patchlib import Data, Patch

PATCH = Patch(
    id="desperation-ryo-command",
    title="Takuma: DESPERATION com o comando do Ryo (v v> -> v> v <v <- + C)",
    spec="src/backend/specs/SPEC-028-desperation-ryo-command.md",
    data=[Data(desperation_slot(TAKUMA, 0x45), "0966", f"{RYO_DESPERATION:04x}")],
)
