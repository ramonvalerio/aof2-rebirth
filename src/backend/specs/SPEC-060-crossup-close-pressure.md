# SPEC-060: Cross global — anular afastamento do hit

- Patch global: `crossup-close-pressure`.
- Status: correção de teleporte implementada; teste no emulador pendente.
- Aplica-se a todo o elenco, sem filtros de personagem.

## Regra atual

Ao receber um hit em cross, o defensor não recebe afastamento horizontal
adicionado pela reação. Interrompe a deriva horizontal do atacante ao
conectar e libera a aterrissagem para pressão. Preserva a posição natural
do contato e a colisão de corpos. Não fixa distância, não puxa personagens,
não lê X do outro jogador para reposicionar e não grava coordenadas.

Cross: normal aéreo $2A/$2B/$3A/$3B, atacante acima do chão, defensor
vivo no chão, hit não defendido, atacante já cruzou o centro do alvo
mantendo a direção original. Sprite olhando à direita e atacante à direita
do alvo, ou olhando à esquerda e atacante à esquerda. Centros iguais não
contam. Jump-in frontal, whiff, defesa, projétil e alvo aéreo ficam fora.

## Implementação

- HIT_SOUND: limpa marcas do novo contato, identifica cross e grava
  $3AF no defensor/$3B0 no atacante. Zera velocidades horizontais $20,
  $30/$34 de ambos e $20 dos sprites. Não muda X, Y ou física vertical.
- $1CBB8: anula contribuições horizontais de filhos de animação para o
  defensor marcado em reação 6/7 e para o atacante marcado em normal no ar.
  Conserva o teste nativo de hitstop e segue $1CBBE.
- $22682: filtro de velocidade residual, não de posição. Se o defensor
  está marcado, vivo, no chão e em reação 6/7, zera $20 do sprite e do
  jogador, $30/$34. Então executa exatamente a integração original:
  `d0 = X atual do próprio sprite + velocidade horizontal` e segue $2268A.
  Sem marca ou fora da reação, a integração é integralmente original.
- LANDING_ATTACK ($1C234): consome marca do atacante quando tocar o chão,
  limpa $240/$60 bit 7 e passa pela saída nativa $1C2EA, preservando os
  buffers e permitindo entrada de ataque no chão. KO do atacante não
  ganha saída para neutro.
- PROJ_HIT_SOUND e novos contatos corpo a corpo limpam/substituem a marca
  do defensor. A regra não se transfere à reação de outro golpe.

## RAM

| Campo | Uso |
|---|---|
| $3AF | Defensor recebeu cross: anula afastamento durante reação |
| $3B0 | Atacante acertou cross: interrompe deriva e libera aterrissagem |

Faixa livre documentada $39B–$3DE, após $3A8–$3AA do Ryo e $3AB–$3AE do
dash de aterrissagem. $3B1, usado pela versão revertida, não é mais lido
ou escrito. Não há snapshot de posição nem timer de posição travada.

## Reversão da estratégia de distância fixa

O usuário relatou teleporte de personagem para outro lado do cenário na
versão que impunha X do atacante ±24 px. O bloco cross_anchor, constante
de distância, marcador de lado e todo cálculo baseado em X do adversário
foram removidos. No ponto de integração há apenas cancelamento de velocidade,
seguido da soma nativa com o X atual do próprio sprite.

## Limites e compatibilidade

A proximidade inicial depende do ponto em que o cross acertou: não aproxima
artificialmente um hit distante. A colisão nativa e as caixas continuam
ativas, podendo acomodar os corpos. Não acrescenta hitstun, dano ou combo
garantido após cross alto. SPEC-059 do Ryo continua isolada para seu chute
fraco frontal; no cross o global zera o componente após esse ajuste.

## Validação

Build completo/isolado, hooks e teste do filtro com posições/velocidades
variadas: cross elegível resulta em X atual, jamais X do adversário;
outros estados mantêm X + velocidade. Confirmar ausência de instruções
que escrevam coordenadas nos blocos do patch e ausência do antigo anchor.

Em jogo: Robert/Takuma e todo o elenco, lados/P1/P2, centro/canto; cross
fundo → soco fraco, reação sem deslocamento extra, sem teleporte, defesa,
frontal, ar e whiff originais, liberação após novo hit/fim da reação.
