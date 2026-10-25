"""hyakuretsu-binta-10-hits (Yuri) — SPEC-027.

O Hyakuretsu Binta (comando $43) prende o oponente e bate várias vezes;
cada tapa passa a contar como hit (10 no total), com o dano por golpe
reduzido. Mecanismo em charlib.multi_hit_block, no hook compartilhado do
estado de ataque ($1C1DA, charlib.ATTACK_STATE).
"""
from charlib import ATTACK_STATE, YURI, multi_hit_block, multi_hit_data, shared_hook
from patchlib import Block, Patch

HYAKURETSU_BINTA = 0x43
HITS = 10

PATCH = Patch(
    id="hyakuretsu-binta-10-hits",
    title="Yuri: Hyakuretsu Binta conta cada tapa: 10 hits",
    spec="src/backend/specs/SPEC-027-multi-hit-rearm.md",
    blocks=[Block("multi_hit", multi_hit_block(YURI, HYAKURETSU_BINTA))],
    hooks=[shared_hook(ATTACK_STATE, "multi_hit")],
    data=multi_hit_data([(0x17F, 0x28, 0x04)], HITS),
)
