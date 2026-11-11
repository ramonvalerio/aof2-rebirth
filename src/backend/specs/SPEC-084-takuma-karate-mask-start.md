# SPEC-084: Takuma — START na seleção mostra o Mr. Karate no retrato

- Patch de personagem: `characters/takuma/karate-mask-start`.
- Depende de `global/start-select-flag` (SPEC-083): START confirma como B
  (cor 1) e liga `$3DA` no registro do jogador.
- Escopo combinado: só os retratos grandes. Na luta o Takuma não muda.
- Status: implementado e conferido no FBNeo; validação na MiSTer pendente.

Escolher o Takuma com **START** troca o retrato grande pelo do **Mr. Karate
de máscara de tengu** do primeiro Art of Fighting (`rom/aof.zip`).

## Retrato do AOF2

- O objeto do retrato fica no slot do byte `$34` do cursor ($1E80/$1F80);
  `$50` aponta a lista de sprites (Takuma: $6777A). O opcode `$85` da lista
  ($50FC → $5226) traz `$CA`, `$CB` e o id do gráfico.
- Gráficos: tabela $80004 (1 long por id), dados em $89008 + 19 bits. O
  tamanho vem da tabela $5272 e o formato dos bits $3C00 da word alta.
- Takuma: animação $0DF2–$0E03, todos 8×8 tiles. O $0DF2 usa o formato $18
  ($7EAA): word de atributo ($8500), 1º tile, 1 byte de máscara por coluna
  (bit 7 = linha de cima); tiles em sequência, pulando os que terminam em $00.
- Paletas do retrato: $D81A copia as paletas 5–6 da metade do bloco da
  tabela $C96C (Takuma: bloco $47, metade = cor & 1).

## Arte do AOF1

- Mr. Karate forçado na demo do AOF1 (`$1093C3 = 9`; ids: Ryo 0, Robert 1,
  Todo 2, Jack 3, Lee 4 …). O retrato grande de vitória fica na C-ROM do aof
  em $3510–$354F (8 linhas de 8 tiles; a arte ocupa as colunas 0–5).
- A tela de vitória do AOF1 é sépia, então as cores foram montadas pelas
  rampas do desenho (adjacência dos índices): cinza 15→13→1→14→2→3 (cabelo,
  barba, faixa) e quente 12→4→5→6→7→10→11→8 (pele → máscara vermelha),
  9 = brilho da máscara, com as cores do Mr. Karate na luta.

## Implementação

- **Tiles:** 43 tiles na C-ROM a partir de $DEA0 (banco 0; sequência zerada
  $DE9C–$DEFF do par c3/c4), via `RomData`. Arte 6×8 nas colunas 1–6 de um
  quadro 8×8; colunas vazias e o fragmento de outro desenho ficam em branco.
- **$5226** (id do gráfico): id em $0DF2–$0E03, objeto `a6` igual ao do slot
  `$34` ou `$3C` de um cursor confirmado (`$3E`), registro com flag e cor 1 →
  devolve o gráfico novo (formato $18, 8×8), em vez da tabela.
- **$C962 / $E1B6** (encadeados com o Ryo, `charlib.start_portrait`): entrada
  ($47, 1) com flag → ($FD, 1).
- **$D828** (encadeado): bloco $FD → as duas paletas do retrato viram a do
  Mr. Karate.

`charlib` registra os três pontos do retrato como hooks compartilhados
(`SELECT_PORTRAIT`, `ENEMY_PORTRAIT`, `PORTRAIT_PALETTE`).

## Validação

FBNeo: cursor sobre o Takuma → retrato normal; START → retrato do Mr. Karate
na tela "select enemy"; B → retrato normal da cor 1; Ryo com START continua
de quimono preto. Testar na MiSTer e como P2.
