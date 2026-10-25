"""desperation-command (Robert) — SPEC-041.

DESPERATION Ryukou Ranbu (comando $46, lista própria +$A4E da tabela $25D04,
só o Robert a usa): ↓↘→↘↓↙← + C (C = soco fraco no layout novo, SPEC-002).

Mesmo problema do Ryo (SPEC-037): o passo final original é f0 40 (botões
exatamente $40, bit 6 = "C segurado" do controle original), que o tradutor
novo nunca produz sozinho; o comando não saía. O passo passa a f0 10.
"""
from patchlib import Data, Patch

COMMANDS = 0x025D04
FINAL_STEP = COMMANDS + 0xA86     # [máscara][valor][prazo][espera][próximo]

PATCH = Patch(
    id="desperation-command",
    title="Robert: DESPERATION Ryukou Ranbu com v v> -> v> v <v <- + C",
    spec="src/backend/specs/SPEC-041-robert-desperation-command.md",
    data=[Data(FINAL_STEP, "f040", "f010")],
)
