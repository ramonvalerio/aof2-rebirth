# SPEC-021: Ryo: Haoh Shoukouken com comando mais fácil

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/haoh-easy-input` (personagem)
- **Combina com:** SPEC-004 (força pelo botão), SPEC-008 (prazo dos passos)

## Comportamento desejado

O SUPER Haoh Shoukouken sai com **frente, um "C" (trás → baixo → frente) e soco** (A ou C), com mais folga.

| | Original | Novo |
|---|---|---|
| Passos | → ← ↙ ↓ ↘ → + soco, **exatos** | → ← ↓ → + soco, **diagonais aceitas** |
| Prazo por passo | 10 frames (12 com a SPEC-008) | 20 frames |

Os outros requisitos do SUPER (golpe aprendido no bônus e barra, `$1D5A8`) não mudam.

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Tabela de comandos | `$1DFC2`: linha = `$25D04 + ($62 − 1) × $20`. **O Ryo usa a 1ª linha** (`$25D04`), não `+$20` |
| Linha do Ryo | `$40` `+$1A0` Kou'ouken (↓↘→+P), `$41` `+$1C0` (↓↘→+K), **`$42` `+$2DC` Haoh Shoukouken**, `$43` `+$238`, `$45` `+$1E0` Renbuken (↓↙←+P), `$46` `+$A0E`, `$47` `+$250` Kohou (→↓↘+P) |
| Passo | Lista de **alternativas** de 6 bytes `[máscara][valor][prazo][segurar][próximo (offset)]`, terminada por máscara `0` (`$1E05C`). Uma alternativa Vale quando `(direção & máscara) == valor`. Direções relativas ao lado (8 frente, 4 trás, 2 baixo, 1 cima); botões nos bits 4–7 (`$10` soco, `$20` chute). Próximo `$FFFF` = comando completo |
| Lista `+$2DC` | → ← ↙ ↓ ↘ → + soco. Também é usada por outros 6 personagens (Robert, Lee, Micky, John, Takuma e Yuri) |
| Listas órfãs | `$26018`–`$26087` (`+$314`, `+$34C`): mesmo movimento + chute / + A+B. **Nenhuma linha aponta para elas** |

## Implementação (patch de dados)

- A lista órfã `+$314` (`$26018`) vira a lista nova: frente (máscara 8), trás (máscara 4), baixo (máscara 2), frente (máscara 8), soco (`$F0`/`$10`), com 20 frames por passo.
- A word do `$42` na linha do Ryo (`$25D08`) passa de `$02DC` → `$0314`. A lista original continua igual para os outros personagens.

## v2: comando rápido

**Sintoma:** feito devagar, o comando saía; feito rápido, não.

**Causa:** o leitor (`$1DFF4`/`$1E048`) avança **um passo por frame**. No comando rápido, a última frente e o soco chegam no mesmo frame: o frame é gasto no passo "frente", e o soco (evento de 1 frame em `$270`) já passou quando o passo "soco" é testado.

**Correção:** alternativas que fecham dois passos no mesmo frame.

| Passo | Alternativas (máscara/valor → próximo) |
|---|---|
| 0 | `09/08` frente **sem cima** → 1 (com cima, `$A0E` bloqueava o pulo para frente, SPEC-023) |
| 1 | `06/06` trás-baixo → **3**; `04/04` trás → 2 |
| 2 | `02/02` baixo → 3 |
| 3 | `F8/18` **frente + soco → fim**; `08/08` frente → 4 |
| 4 | `F0/10` soco → fim |

São 52 bytes, dentro da lista órfã (56).

## v3: o Kohou roubava o comando rápido

**Sintoma:** mesmo com as alternativas da v2, o comando rápido não saía.

**Causa:** o leitor percorre os comandos `$40` → `$4F` a cada frame, e cada comando completo grava o pendente `$218` (`$1E102`, que arma `$A77 = $3C`). Feito rápido, → ← ↓ → + soco **também completa o Kohou** (`$47`: → ↓ ↘ + soco; o 1º → começa o Kohou, e o ↓ ↘ + soco chegam dentro do prazo dele). Como o `$47` vem depois do `$42`, o Kohou sobrescrevia o Haoh no mesmo frame. Devagar, o prazo do Kohou acaba entre o → e o ↓, e só o Haoh completa. O Kou'ouken (`$40`, ↓ ↘ → + soco) também completa, mas vem antes do `$42` e é sobrescrito por ele.

**Correção:** hook em `$1E0E0` (comando completo, antes de gravar). Para o Ryo, se o novo comando é o Kohou e o `$218` tem o Haoh gravado **neste frame** (`$A77 = $3C`), não grava (`$1E10C`).

## Pendências / riscos

- **Lista órfã:** foi achada pela varredura das linhas da tabela. Se algum outro código (ex.: IA) a usar diretamente, ele passa a ver o comando novo.
- **Comandos parecidos:** com as diagonais aceitas, → ← ↓ → + soco fica mais fácil também por acidente. O Kou'ouken (↓↘→) não sai por engano, porque o SUPER exige começar com → ←.

## Critérios de aceite

- [ ] → ← ↓ → + A (ou C): sai o Haoh Shoukouken (com o golpe aprendido e barra)
- [ ] O movimento original (→ ← ↙ ↓ ↘ → + soco) continua funcionando
- [ ] Rápido (soco junto com a última frente): sai o Haoh, não o Kohou
- [ ] Kohou sozinho (→ ↓ ↘ + soco) continua saindo
- [ ] Kou'ouken, Kohou e Renbuken não mudam
- [ ] O SUPER dos outros personagens não muda
