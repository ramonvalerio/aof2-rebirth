# SPEC-037: Ryo: comando do DESPERATION (Ryukou Ranbu)

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/desperation-command` (personagem, dados)
- **Relacionadas:** SPEC-002 (botões), SPEC-028 (Takuma e Yuri usam a lista do Ryo)

## Comportamento desejado

Ryukou Ranbu com **↓↘→↘↓↙← + C** (C = soco fraco no layout novo). Continuam valendo as condições do original (vida ≤ `$20` e barra ≥ `$60`, handler `$1D460`).

## Causa

| Item | Valor |
|---|---|
| Lista | comando `$46` do Ryo → `$25D04 + $A0E`: ↓ ↘ → ↘ ↓ ↙ ← e o passo final em `$26746` |
| Leitor | `$1DF7E`: compara o `$270` **traduzido** (`$1DFA0`) com cada passo `[máscara][valor][prazo][espera][próximo]` (`$1E05C`) |
| Passo final original | `f0 40`: botões exatamente `$40`, o bit 6 ("C segurado" do controle original) |
| Problema | o tradutor novo (SPEC-002) só liga o bit 6 junto de soco/chute (C+D = `$50`, B+D = `$C0`). `$40` sozinho nunca aparece: o DESPERATION não saía |

## Implementação

Passo final `$26746`: `f0 40` → **`f0 10`** (soco fraco sozinho = C).

A Yuri aponta o DESPERATION para essa mesma lista (SPEC-028), então também passa a sair com ↓↘→↘↓↙← + C. Sem este patch, os dois ficam sem DESPERATION. (O Takuma tem comando próprio desde a SPEC-040.)

## Pendências / riscos

- **Kou'ouken no meio do movimento:** o começo (↓↘→) + C também é o Kou'ouken médio. O leitor varre os comandos `$40`→`$4F` e o maior (`$46`) fica no `$218` se os dois casarem no mesmo frame. Confirmar em jogo que sai o DESPERATION.

## Critérios de aceite

- [ ] Vida baixa e barra cheia: ↓↘→↘↓↙← + C solta o Ryukou Ranbu
- [ ] Fora das condições: não sai (ou sai o golpe normal do original)
- [ ] ↓↘→ + C continua sendo o Kou'ouken médio
- [ ] Yuri: DESPERATION com o mesmo comando
