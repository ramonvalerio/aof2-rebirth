"""kououken-three-buttons (Takuma) — SPEC-039.

Kou'ouken (comando $40, golpes $155/$156/$157, anim $5C0) pelo botão:
  ↓↘→ + C + D -> fraco $157 (derruba; para cancel e combos)
  ↓↘→ + C     -> médio $156 (não derruba)
  ↓↘→ + D     -> forte $155 (não derruba)
Mecanismo em charlib.fireball_three_buttons (SPEC-033, o mesmo do Ryo).
"""
from charlib import TAKUMA, fireball_three_buttons
from patchlib import Patch

BLOCKS, HOOKS, DATA = fireball_three_buttons(TAKUMA, 0x155, "kououken")

PATCH = Patch(
    id="kououken-three-buttons",
    title="Takuma: Kou'ouken fraco = C+D (derruba), médio = C, forte = D",
    spec="src/backend/specs/SPEC-039-robert-takuma-fireball-three-buttons.md",
    blocks=BLOCKS,
    hooks=HOOKS,
    data=DATA,
)
