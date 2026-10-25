"""close-hp-chain (Robert) — SPEC-031.

Soco forte perto ($23), ao conectar, cancela no B+D (chute baixo), como o
do Ryo (SPEC-020). Hook compartilhado da janela de ataque ($1C066,
charlib.ATTACK_WINDOW; rotina em charlib.normal_chain_block).
"""
from charlib import ATTACK_WINDOW, ROBERT, normal_chain_block, shared_hook
from patchlib import Block, Patch

CLOSE_HP = 0x23
LOW_KICK = 0x60             # $270 bits 5 + 6 (B+D)

PATCH = Patch(
    id="close-hp-chain",
    title="Robert: soco forte perto -> B+D ao conectar",
    spec="src/backend/specs/SPEC-031-robert-close-hp-chain.md",
    blocks=[Block("normal_chain", normal_chain_block(ROBERT, [(CLOSE_HP, LOW_KICK)]))],
    hooks=[shared_hook(ATTACK_WINDOW, "normal_chain")],
)
