# SPEC-041: Robert: comando do DESPERATION (Ryukou Ranbu)

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/robert/desperation-command` (personagem, dados)
- **Relacionada:** SPEC-037 (mesma correção no Ryo)

## Comportamento desejado

Ryukou Ranbu do Robert com **↓↘→↘↓↙← + C** (C = soco fraco). Condições do original mantidas (vida ≤ `$20`, barra ≥ `$60`).

## Causa e implementação

Comando `$46` do Robert → lista própria `$25D04 + $A4E` (só ele a usa): ↓ ↘ → ↘ ↓ ↙ ← e o passo final em `+$A86` = `f0 40` (botões exatamente `$40`, o bit 6 "C segurado" do controle original). O tradutor novo (SPEC-002) só liga o bit 6 junto de soco/chute, então o DESPERATION não saía.

Passo final `+$A86`: `f0 40` → **`f0 10`** (soco fraco sozinho = C).

## Pendências / riscos

- O começo (↓↘→ + C) também é o Ryugekiken médio (SPEC-039); o maior comando (`$46`) fica no `$218` quando os dois casam no mesmo frame.

## Critérios de aceite

- [ ] Vida baixa e barra cheia: ↓↘→↘↓↙← + C solta o Ryukou Ranbu do Robert
- [ ] ↓↘→ + C continua sendo o Ryugekiken médio
