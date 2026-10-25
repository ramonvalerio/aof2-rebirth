"""desperation-command (Takuma) — SPEC-040.

DESPERATION Ryukou Ranbu: ↓↘→↓↘→ + soco fraco + soco forte (C+D).

Lista própria do Takuma (comando $45 -> +$966 da tabela $25D04; só ele a
usa). Original: ↓ ↘ → ← → + $50 (no controle original A+B; no layout novo
$50 = C+D, SPEC-002). Cada nó = [máscara][valor][prazo][espera][próximo].
Sem espaço livre ao alcance de 16 bits para uma lista nova, então a lista
é reescrita no lugar e termina num nó que já existe:
  $966 ↓ -> $96E ↘ -> $976 →            (iguais)
  $97E ← -> ↓   (ff04 -> ff02)
  $986 → -> ↘   (ff08 -> ff0a), próximo $98E -> $374
  $374 → -> $37C final f0 50 (C+D)       (nós de outra lista, só lidos)
Antes (SPEC-028) o Takuma apontava para a lista do Ryo; o slot volta ao
original ($966).
Prioridade: o fim (↓↘→ + C+D) também é o Kou'ouken fraco (comando $40); o
leitor varre $40..$4F e o maior ($45) fica no $218.
"""
from patchlib import Data, Patch

COMMANDS = 0x025D04
LIST = 0x966

PATCH = Patch(
    id="desperation-command",
    title="Takuma: DESPERATION Ryukou Ranbu com v v> -> v v> -> + C+D",
    spec="src/backend/specs/SPEC-040-takuma-desperation-command.md",
    data=[
        Data(COMMANDS + 0x97E, "ff04", "ff02"),            # ← -> ↓
        Data(COMMANDS + 0x986, "ff08", "ff0a"),            # → -> ↘
        Data(COMMANDS + 0x986 + 4, "098e", "0374"),        # -> → + C+D (nós $374/$37C)
    ],
)
