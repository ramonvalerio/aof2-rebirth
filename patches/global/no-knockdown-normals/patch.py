"""no-knockdown-normals — SPEC-012.

Golpe normal não derruba: só tontura (dizzy) e especiais derrubam.

Regras de queda do original (reação montada em $21314):
  - tontura: $3F bit 2 do defensor -> $1CEAE liga $3F bit 7 (queda)
  - oponente fora do chão: $21BBE testa a altura $18; se > 0, $21BD4 liga
    $3F bit 7 (queda) e usa o grupo de reações aéreas (d1 = $20)
A segunda regra derrubava com qualquer golpe que pegasse o oponente com
altura > 0, inclusive na decolagem/aterrissagem do pulo e em saltinhos,
o que parecia queda "sem motivo".

Aqui, se o golpe do atacante é normal ($230 < $40; a0 = atacante desde
$21314), a marca de queda não é ligada: o oponente leva a reação aérea e
cai de pé (air reset). Especiais ($230 >= $40) e tontura não mudam.
"""
from asm68k import Branch, Ins, Label
from patchlib import Block, Hook, Patch

FIRST_SPECIAL_CMD = 0x40

# Substitui: bset.b #$7,$3f(a6) / moveq #$20,d1 / rts  em $21BD4
air_hit = [
    Ins(f"0c68{FIRST_SPECIAL_CMD:04x}0230", f"cmpi.w #${FIRST_SPECIAL_CMD:x}, $230(a0)"),
    Branch("bcs", "normal"),
    Ins("08ee0007003f", "bset.b #$7, $3f(a6)"),     # especial: queda (original)
    Label("normal"),
    Ins("7220", "moveq #$20, d1"),                   # grupo de reações aéreas
    Ins("4e75", "rts"),
]

PATCH = Patch(
    id="no-knockdown-normals",
    title="Golpe normal não derruba (só tontura e especiais)",
    spec="src/backend/specs/SPEC-012-no-knockdown-normals.md",
    blocks=[Block("air_hit", air_hit)],
    hooks=[
        Hook(addr=0x21BD4, expect="08ee0007003f72204e75", to_block="air_hit"),
    ],
)
