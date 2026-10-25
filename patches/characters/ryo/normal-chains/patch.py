"""normal-chains (Ryo) — SPEC-018 / SPEC-020.

Normais que, ao conectar, cancelam no próximo golpe (chain), no hook
compartilhado da janela de ataque ($1C066, charlib.ATTACK_WINDOW; rotina em
charlib.normal_chain_block):
  baixo B ($38)          -> chute (baixo B / baixo D)   SPEC-018
  soco forte perto ($23) -> B+D (chute baixo, d4 $34)   SPEC-020

Bits do byte alto de $270: 5 = chute, 6 = "C segurado" (B+D = chute baixo,
SPEC-002).

Hitstun do baixo B: byte 14 do golpe $00D, $01 -> $02. É o que o Ryo usava
quando o combo passou a funcionar; a SPEC-019 indica que a reação vem de
postura/altura/dano ($21314), então o efeito do byte não está confirmado
(no Robert estragava o baixo B, por isso fica só aqui).
"""
from charlib import ATTACK_WINDOW, MOVE_TABLE, RYO, normal_chain_block, shared_hook
from patchlib import Block, Data, Patch

CROUCH_LK = 0x38
CLOSE_HP = 0x23
KICK = 0x20                 # $270 bit 5
LOW_KICK = 0x60             # $270 bits 5 + 6 (B+D)
CROUCH_LK_MOVE = 0x00D
REACTION = 14

PATCH = Patch(
    id="normal-chains",
    title="Ryo: chains ao conectar: baixo B -> chute, soco forte perto -> B+D",
    spec="src/backend/specs/SPEC-020-ryo-normal-chains.md",
    blocks=[Block("normal_chain", normal_chain_block(RYO, [
        (CROUCH_LK, KICK),      # SPEC-018
        (CLOSE_HP, LOW_KICK),   # SPEC-020
    ]))],
    hooks=[shared_hook(ATTACK_WINDOW, "normal_chain")],
    data=[Data(MOVE_TABLE + CROUCH_LK_MOVE * 16 + REACTION, "01", "02")],
)
