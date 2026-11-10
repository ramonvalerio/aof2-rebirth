# SPEC-083: Ryo — START na seleção escolhe o quimono preto

- Patch de personagem: `characters/ryo/black-gi-start`.
- Status: implementado e conferido no FBNeo (START → preto; B → azul
  original); validação na MiSTer pendente.

Escolher o Ryo com **START** dá a mesma roupa da escolha com chute forte
(botão B no layout da SPEC-002, cor 1), mas com o quimono **preto** no lugar
do azul-claro. Faixa, luvas e demais detalhes vermelhos, pele e cabelo não
mudam.

## Como o jogo escolhe a cor

- Seleção ($C77E): lê a borda dos botões na BIOS ($10FD97 P1 / $10FD9D P2) e
  usa só A–D ($F0). A tabela $C84C dá a cor: A 0, B 1, C 2, D 3. A cor vai
  para `$3A(a6)` do cursor e `$276` do registro do jogador. Mesmo personagem
  dos dois lados: o jogo troca a cor para não repetir ($1EF6). Tempo esgotado
  confirma como A ($C756 → $C7F4).
- Pedido de paleta da luta ($A030/$A04C): P1 no banco 6 ($104000), P2 no
  banco 7 ($104400). Bloco = tabela $A060 por personagem e `cor >> 1`
  (Ryo: $4D para cores 0/1, $5A para 2/3).
- Carregador ($1D8A): 16 paletas de 48 bytes (R, G, B de 6 bits) em
  `$80(a5)` + bloco × $300, base $68000. O bit 0 da cor escolhe a metade do
  bloco na sprite ($1B440: `(lado×2 + cor&1) × 8`).

## Implementação

- **$C7CE** (confirmação): sem A–D, a borda de START em $10FDAD (bit 0 P1,
  bit 2 P2) confirma como B e liga a flag `$3DA` do registro. A–D desligam a
  flag. No caminho de continuação (`$29(a6)`), cor e flag são mantidas.
- **$C75E** (tempo esgotado): desliga a flag antes de confirmar como A.
- **$A05E** (pedido): Ryo com cor 1 e flag pede o bloco $FE, que nenhuma
  cena nem personagem usa.
- **$1D92** (carregador): bloco $FE lê as paletas do patch em vez de
  $68000 + $FE × $300. São uma cópia do bloco $4D com a rampa azul da cor 1
  (paletas 0, 5, 6 e 7) trocada por tons escuros:

| Azul (R,G,B) | Preto |
|---|---|
| 58,62,62 | 24,24,26 |
| 46,58,62 | 18,18,20 |
| 32,46,52 | 12,12,14 |
| 22,32,38 | 8,8,8 |
| 14,22,28 | 4,4,4 |

A flag fica em `$3DA`, na faixa livre do registro ($39B–$3DE).

## Retrato grande

O retrato da seleção ($C940) e o do "select enemy" ($E196) leem a tabela
$C96C (bloco, metade) por personagem e cor e chamam $D81A, que copia as
paletas 5 e 6 da metade (+$180 se metade 1, +$F0). Usam os mesmos blocos da
luta; o $4D é só do Ryo.

- **$C962 / $E1B6**: bloco $4D, metade 1 e flag no registro (`$1C(a6)`) →
  pede o bloco $FE.
- **$D828**: bloco $FE lê as paletas 5–6 pretas (96 bytes no patch); o
  endereço é ajustado para $D81A somar $180 + $F0 de volta.

## Build

A P-ROM não tinha mais espaço nas áreas reservadas. `tools/build_rom.py`
ganhou `FREE_EXTRA`: $F5C10–$F6000 e $FBCC0–$FBFF0, preenchimento zerado
antes de fronteiras alinhadas, sem nenhum ponteiro da P-ROM apontando para
dentro. As regiões novas ficam no fim da lista, então os blocos que já cabiam
não mudam de lugar.

## Limites

- Com o mesmo personagem dos dois lados, se o jogo trocar a cor 1 por outra,
  a flag não tem efeito (só vale com cor 1).

## Validação

FBNeo: START na seleção → retrato e P1 Ryo de quimono preto com
vermelhos; B → azul-claro original. Testar na MiSTer, como P2, e contra Ryo da CPU.
