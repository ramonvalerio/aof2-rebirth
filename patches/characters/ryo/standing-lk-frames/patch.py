"""standing-lk-frames (Ryo) — SPEC-032.

Chute fraco em pé (golpe $009, longe e perto; anim $130) com o tempo do
soco fraco em pé (anim $120: startup 2, ativo 4, recuperação 1, total 7).

  anim $130 original: q0 2 (cmd) + q1 2 | q2 8 ATAQUE | q3 4 + q4 4 | q5 fim
                      startup 4, ativo 8, recuperação 8, total 20
  novo:               q0 1 (cmd) + q1 1 | q2 4 ATAQUE | q3 1 | q4 = fim
                      startup 2, ativo 4, recuperação 1, total 7
q4 vira o quadro final (flags $80, mesma peça $62C do q5); q5 deixa de ser
alcançado. A anim $130 só é usada pelo golpe $009.
"""
from patchlib import Data, Patch

FRAMES = 0x052FAC   # lista de quadros da anim $130

# (endereço, original, novo): [duração][flags][peça]; duração bit 7 = quadro simples
CHANGES = [
    (FRAMES + 0 * 4, "02", "01"),            # q0 (lista de comandos): 2 -> 1
    (FRAMES + 1 * 4, "82", "81"),            # q1: 2 -> 1
    (FRAMES + 2 * 4, "88", "84"),            # q2 ativo: 8 -> 4
    (FRAMES + 3 * 4, "84", "81"),            # q3 recuperação: 4 -> 1
    (FRAMES + 4 * 4, "8400", "8080"),        # q4: vira o quadro final
]

PATCH = Patch(
    id="standing-lk-frames",
    title="Ryo: chute fraco em pé com startup, ativo e recovery do soco fraco em pé",
    spec="src/backend/specs/SPEC-032-ryo-standing-lk-frames.md",
    data=[Data(addr, old, new) for addr, old, new in CHANGES],
)
