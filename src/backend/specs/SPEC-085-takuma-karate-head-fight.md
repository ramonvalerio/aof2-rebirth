# SPEC-085: Takuma — máscara de tengu na luta (START)

- Patch de personagem: `characters/takuma/karate-head-fight`.
- Depende de `global/start-select-flag` (SPEC-083): START confirma como B
  (cor 1) e liga `$3DA` no registro do jogador.
- Status: **protótipo** — só a guarda parada (animação $580). Conferido no
  FBNeo; validação na MiSTer pendente.

Escolhido com START, o Takuma luta com o **rosto coberto pela máscara de tengu
do Mr. Karate** (só a face: vermelha, nariz longo, olho) e o **cabelo original**.

Histórico: a cabeça inteira do Mr. Karate colada no corpo não combinou; o nariz
alongado desenhado à mão ficou artificial e está salvo no branch
`takuma-nariz-tengu`.

## Como os quadros de luta são desenhados

- Quadro de animação → peça ($CE000, base $D4004): caixas de colisão e lista
  de comandos; cada opcode `$85` desenha um gráfico (`$CA`, `$CB`, id).
- Guarda parada: corpo inteiro (ex.: $169E, 6×9 tiles, formato $24, que já
  inclui a cabeça) + cabeça sobreposta normal ($169F) e machucada ($16A0).
- Os 406 gráficos do Takuma (10 formatos) foram decodificados rodando o
  próprio decodificador do jogo ($6364) no Unicorn (M68000). Os tiles dele
  ficam no banco 1 ($1A400–$1B5FF); usam as paletas 0–4 do jogador.

## Implementação

- **$6364** (entrada comum dos decodificadores): se `a6` é o sprite (slot do
  byte `$3` do registro) de um jogador com `$62 = $A`, cor 1 e flag, o
  decodificador roda como sub-rotina. Depois, as colunas (`d6`) e linhas
  (`d5`) recém-escritas a partir do sprite `d3` são relidas na VRAM: tile do
  banco 1 que está na tabela vira o tile novo, com o mesmo atributo.
- **Tabela:** tile original → tile novo, em ordem crescente (busca linear com
  saída antecipada). Os tiles da máscara aparecem uma única vez em todos os
  gráficos do Takuma; os das cabeças sobrepostas (normal e machucada, que
  cobririam a máscara) vão para o tile vazio $11660.
- **Tiles novos:** C-ROM $11661–$11669 (sequência zerada $1165B–$116FF,
  banco 1), via `RomData`.
- **Cores:** os vermelhos 7–11 e o contorno 12 já existem na paleta 0 da cor 1
  do Takuma; nenhuma paleta muda.

## Arte

- Máscara: recorte da cabeça do Mr. Karate na demo do AOF1 (P2 forçado para o
  id 9, guarda virada para a direita). Ficam só as linhas da máscara (12–27 do
  recorte): pixels vermelhos/amarelos e o que estiver entre eles na mesma linha,
  sem cinzas (cabelo e barba); brilhos brancos internos viram vermelho claro;
  componentes soltos com menos de 8 pixels saem.
- Espelhada (nos dados o rosto do Takuma olha para a esquerda; o jogo espelha)
  e alinhada pelo olho: o olho do Takuma é o primeiro pixel de contorno com pele
  dos dois lados, procurando da esquerda para a direita nas linhas 10–17 abaixo
  do topo da cabeça.
- Contorno: a máscara ocupa exatamente o rosto do Takuma. A região do rosto é
  um preenchimento a partir do olho por pixels de pele (1–6, paleta 0), numa
  caixa de olho−6 a olho+6 linhas e olho−5 a olho+7 colunas (na última linha,
  só à direita do olho, para não pegar o braço). Isso cobre o queixo e para
  no cabelo, na orelha e no pescoço.
- Dentro do rosto: pixel da máscara do Mr. Karate onde houver; senão a pele
  vira vermelho pela própria sombra (1–2→7, 3→8, 4→9, 5→10, 6→11). O
  contorno (12) e o cabelo do Takuma ficam.
- Fora do rosto, só o nariz: pixels da máscara à esquerda do rosto, com as
  falhas de cada linha preenchidas pela cor do vizinho mais próximo até a
  borda do rosto, e contorno escuro em cima e embaixo onde estava vazio.
- Cores fixas na paleta 0 da cor 1: 7 laranja (brilho), 8 vermelho, 9 escuro,
  10 sombra, 11 mais escuro, 12 contorno, 1 olho (amarelado).

## Ferramentas

- `asm68k.Dbra(reg, rótulo)`: laço `dbra` com conferência pelo capstone.
- `build_rom.FREE_EXTRA`: blocos de paleta zerados $5D, $60 e $6B
  ($79700, $7A000, $7C100), fora das tabelas de cena/personagem e nunca
  pedidos durante o attract.

## Próximos passos

Estender a máscara às outras animações (guarda $581, andar, golpes), quadro a
quadro, conferindo encaixe, ângulo do rosto e tiles compartilhados.
Com centenas de entradas, trocar a busca linear por busca binária.
