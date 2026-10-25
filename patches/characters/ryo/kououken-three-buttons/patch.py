"""kououken-three-buttons (Ryo) — SPEC-033.

Versão do Kou'ouken (comando $40, golpes $011/$012/$013) pelo botão:
  v v> -> + soco fraco + soco forte (C+D) -> fraco $013 (startup 11, derruba;
                                             para cancel e combos)
  v v> -> + soco fraco (C)                -> médio $012 (não derruba)
  v v> -> + soco forte (D)                -> forte $011 (não derruba)

Hook compartilhado em $1D676 (charlib.SPECIAL_CHOSEN), depois da escolha
da versão pelo special-strength-by-button (SPEC-004): com o comando vindo do
jogador ($218 bit 9), troca $10(a5)/$5C(a4) e a barra equivalente $23F
(tamanho do projétil, $22A5C) pelas marcas do botão: bit 10 = C+D
(special-strength-by-button), bit 8 = forte. A CPU (sem bit 9) não muda.

Derrubar: byte 6 (efeito de acerto, $2135E) do $013, $00 -> $01, o efeito
da queda do Kohou forte (SPEC-010). O projétil leva o efeito do jogador
($20A -> $37 do projétil, $22A3A).

Comando: o passo final do ↓↘→ + soco ($1B8) aceita o par C+D só para o Ryo.
Mecanismo em charlib.fireball_three_buttons (o mesmo do Robert e do Takuma).
"""
from charlib import RYO, fireball_three_buttons
from patchlib import Patch

BLOCKS, HOOKS, DATA = fireball_three_buttons(RYO, 0x011, "kououken")

PATCH = Patch(
    id="kououken-three-buttons",
    title="Ryo: Kou'ouken fraco = C+D (derruba), médio = C, forte = D",
    spec="src/backend/specs/SPEC-033-ryo-kououken-three-buttons.md",
    blocks=BLOCKS,
    hooks=HOOKS,
    data=DATA,
)
