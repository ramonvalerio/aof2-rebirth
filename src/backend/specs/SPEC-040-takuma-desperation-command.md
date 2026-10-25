# SPEC-040: Takuma: comando do DESPERATION (Ryukou Ranbu)

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/takuma/desperation-command` (personagem, dados). Substitui `takuma/desperation-ryo-command` (SPEC-028)

## Comportamento desejado

Ryukou Ranbu do Takuma com **↓↘→↓↘→ + soco fraco + soco forte (C+D)**. As condições do original continuam (vida ≤ `$20`, barra ≥ `$60`).

## Implementação

O Takuma volta a usar a própria lista (comando `$45` → `$25D04 + $966`; só ele a referencia). Não há espaço livre ao alcance de 16 bits da tabela para uma lista nova, então ela é reescrita no lugar e termina em nós que já existem (de outra lista, só lidos):

| Nó | Original | Novo |
|---|---|---|
| `$966` | ↓ → `$96E` | igual |
| `$96E` | ↘ → `$976` | igual |
| `$976` | → → `$97E` | igual |
| `$97E` | ← (`ff04`) → `$986` | **↓** (`ff02`) |
| `$986` | → (`ff08`) → `$98E` | **↘** (`ff0a`) → **`$374`** |
| `$374` (outra lista, não muda) | → (prazo 30) → `$37C` | — |
| `$37C` (outra lista, não muda) | final `f0 50`: botões exatamente `$50` = C+D (SPEC-002) | — |

No controle original `$50` era A+B; no layout novo (SPEC-002) é soco fraco + soco forte.

## Pendências / riscos

- **Kou'ouken fraco no fim:** ↓↘→ + C+D também é o Kou'ouken fraco do Takuma (SPEC-039). O leitor varre os comandos `$40`→`$4F` e o maior (`$45`) fica no `$218` quando os dois casam no mesmo frame.
- **Prazo:** o último → tem prazo de 30 frames (`$374`); os outros, 10–15.

## Critérios de aceite

- [ ] Vida baixa e barra cheia: ↓↘→↓↘→ + C+D solta o Ryukou Ranbu
- [ ] ↓↘→ + C+D (uma vez) continua sendo o Kou'ouken fraco
- [ ] O DESPERATION de Ryo e Yuri não muda
