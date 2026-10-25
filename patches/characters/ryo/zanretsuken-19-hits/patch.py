"""zanretsuken-19-hits (Ryo) — SPEC-025.

O Zanretsuken (comando $44) prende o oponente e bate várias vezes; cada
golpe passa a contar como hit (19 no total), com o dano por golpe reduzido.
Mecanismo em charlib.multi_hit_block (SPEC-027), no hook compartilhado do
estado de ataque ($1C1DA, charlib.ATTACK_STATE).
"""
from charlib import ATTACK_STATE, RYO, multi_hit_block, multi_hit_data, shared_hook
from patchlib import Block, Patch

ZANRETSUKEN = 0x44
HITS = 19

PATCH = Patch(
    id="zanretsuken-19-hits",
    title="Ryo: Zanretsuken conta cada golpe: 19 hits",
    spec="src/backend/specs/SPEC-025-ryo-zanretsuken-19-hits.md",
    blocks=[Block("multi_hit", multi_hit_block(RYO, ZANRETSUKEN))],
    hooks=[shared_hook(ATTACK_STATE, "multi_hit")],
    data=multi_hit_data([(0x01E, 0x28, 0x02), (0x01F, 0x1E, 0x02)], HITS),
)
