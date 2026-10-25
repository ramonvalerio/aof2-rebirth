"""desperation-ryo-command (Yuri) — SPEC-028.

O DESPERATION (Hien Hou'oukyaku, comando $45, original
-> <- -> v> v <v <- + B+C, lista +$5D8) sai com o comando do Ryo:
v v> -> v> v <v <- + C (lista +$A0E). A lista original não muda.
"""
from charlib import RYO_DESPERATION, YURI, desperation_slot
from patchlib import Data, Patch

PATCH = Patch(
    id="desperation-ryo-command",
    title="Yuri: DESPERATION com o comando do Ryo (v v> -> v> v <v <- + C)",
    spec="src/backend/specs/SPEC-028-desperation-ryo-command.md",
    data=[Data(desperation_slot(YURI, 0x45), "05d8", f"{RYO_DESPERATION:04x}")],
)
