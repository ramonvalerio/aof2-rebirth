"""desperation-command (Ryo) — SPEC-037.

DESPERATION Ryukou Ranbu (comando $46, lista +$A0E da tabela $25D04):
↓↘→↘↓↙← + C (C = soco fraco no layout novo, SPEC-002).

O leitor de comandos compara o $270 traduzido ($1DFA0). O passo final
original é f0 40: botões exatamente $40 (bit 6 = "C segurado" do controle
original). O tradutor novo só liga o bit 6 junto de soco/chute (pares C+D
$50 e B+D $C0), então o comando não saía com nenhum botão. O passo passa a
f0 10 (soco fraco sozinho = C).

A lista é a mesma que a Yuri usa (yuri/desperation-ryo-command, SPEC-028):
ela também passa a sair com + C. (O Takuma tem comando próprio, SPEC-040.)
Prioridade: se no mesmo frame o Kou'ouken (↓↘→ + soco, comando $40) também
casar, o leitor varre $40..$4F e o maior ($46) fica no $218.
"""
from patchlib import Data, Patch

COMMANDS = 0x025D04
FINAL_STEP = COMMANDS + 0xA46     # [máscara][valor][prazo][espera][próximo]

PATCH = Patch(
    id="desperation-command",
    title="Ryo: DESPERATION Ryukou Ranbu com v v> -> v> v <v <- + C",
    spec="src/backend/specs/SPEC-037-ryo-desperation-command.md",
    data=[Data(FINAL_STEP, "f040", "f010")],
)
