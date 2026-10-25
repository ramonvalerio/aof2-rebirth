"""ryugekiken-three-buttons (Robert) — SPEC-039.

Ryugekiken (comando $40, golpes $039/$03A/$03B, anim $1C0) pelo botão:
  ↓↘→ + C + D -> fraco $03B (derruba; para cancel e combos)
  ↓↘→ + C     -> médio $03A (não derruba)
  ↓↘→ + D     -> forte $039 (não derruba)
Mecanismo em charlib.fireball_three_buttons (SPEC-033, o mesmo do Ryo).
"""
from charlib import ROBERT, fireball_three_buttons
from patchlib import Patch

BLOCKS, HOOKS, DATA = fireball_three_buttons(ROBERT, 0x039, "ryugekiken")

PATCH = Patch(
    id="ryugekiken-three-buttons",
    title="Robert: Ryugekiken fraco = C+D (derruba), médio = C, forte = D",
    spec="src/backend/specs/SPEC-039-robert-takuma-fireball-three-buttons.md",
    blocks=BLOCKS,
    hooks=HOOKS,
    data=DATA,
)
