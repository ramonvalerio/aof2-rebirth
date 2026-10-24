# SPEC-011: Dash mais ágil

- **Status:** Implementada, aguardando teste em emulador (detector de dois toques reescrito)
- **Patch:** `patches/global/dash-snappy` (global)

## Comportamento desejado

Dash para frente e dash para trás (dois toques) com início e fim rápidos, para uma jogabilidade menos travada. Vale para todos os personagens.

| Ryo | Antes | Depois |
|---|---|---|
| Parado no início | 4 frames | **1 frame** |
| Deslizando (8,5 px/frame) | 24 frames | 24 frames (igual) |
| Parado no fim | 4 frames | **1 frame** |
| Total | 32 frames | **26 frames** |

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| `$1CCDA` | Detecção de dois toques: máquina de estados em `$212`, direção em `$213`, janela de 16 frames (`$210`) |
| `$1BC84` | Dispara o dash: comando 4 (frente) ou 5 (trás), conforme `$1BBF0` |
| `$1E290` / `$1E2E0` | Handlers do dash: animação = id da lista (`$1E24E`), estado `$10`/`$11` |
| `$1BCAC` / `$1BCE4` | Estado de dash (16/17): aceita ataques e especiais (`jsr $1D808`); termina ao soltar ou trocar a direção ou no fim da animação (comando 1) |
| `$1BD2C` | Velocidade do dash: tabela `$1BD5C` (8 bytes por personagem: frente, trás; Ryo `±$00088000` = 8,5 px/f). **Zero nos quadros com flag `$40`** |

As animações de dash têm quadros com flag `$40` (parado) no início e no fim. Ex.: Ryo `$104`/`$105` = `4/$40, 6, 12, 6, 4/$40, fim`.

## Implementação (patch de dados)

Todo quadro com flag `$40` das animações de dash (comandos 4 e 5 dos 13 personagens) passa a durar **1 frame**: 55 quadros em 26 animações. A duração mantém o bit 7 (quadro simples).

Sem quadros parados (não mudam): dash para frente do Jack (`$284`), dash para trás de Mr.Big (`$505`) e de Geese (`$705`).

## Detector de dois toques (correção)

**Sintoma:** vindo da direção oposta (ex.: segurando ← e fazendo → →), o dash não saía.

**Causa:** a máquina de estados original (`$1CCDA`, estados em `$212`):

| Estado | Exigência |
|---|---|
| 0 | input bruto `$68` **todo zerado** (nenhuma direção e nenhum botão) para armar |
| 1 | 1º toque exatamente ← ou → (`$68` = 4 ou 8) |
| 2 | soltar dentro do prazo (`$210`) |
| 3 | 2º toque igual (`$213`) em até 16 frames → dash |

Passando direto da direção oposta para o dash, `$68` nunca zera: o estado 0 não arma e o 1º toque é ignorado. O mesmo acontece com um botão segurado.

**Correção:** `$1CCDA` reescrito com as **bordas de aperto** (`$69`), que já implicam ter soltado antes:

- borda ← ou → com cima e baixo soltos → 1º toque: `$212 = 1`, `$213` = direção, `$210 = 16`;
- borda na mesma direção com `$212` pendente → **dash** (`d0 = 1`, mesmo retorno do original);
- borda com cima ou baixo segurado (diagonal, meia-lua) ou ← e → juntos → recomeça;
- sem borda → `$210` decrementa e, se esgotar, recomeça.

`$213` continua sendo a direção que o estado de dash (`$1BCD6`) compara. A contagem do prazo só avança quando o detector é chamado (neutro, andando, agachado), como no original.

## Pendências / riscos

- **Visual:** a pose de arranque e a de frenagem aparecem por 1 frame.
- **Janela de dois toques** (16 frames) e **distância** do dash não mudam. Se quiser um dash mais curto ou mais longo, o próximo ajuste é a duração dos quadros em movimento ou a velocidade da tabela `$1BD5C`.

## Critérios de aceite

- [ ] Dash para frente do Ryo começa a deslizar quase imediatamente
- [ ] Ao soltar a direção, o Ryo para na hora
- [ ] Golpe durante o dash continua saindo
- [ ] Dash para trás idem
- [ ] Outros personagens: dash sem a pausa inicial
- [ ] Segurando ←, fazer → →: o dash para frente sai (e o inverso para o dash para trás)
- [ ] Dash com um botão segurado
- [ ] Meia-lua (↓↘→) repetida não dispara dash
