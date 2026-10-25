# SPEC-057: Ryo — Kohou facilitado durante o dash

- Patch isolado: `characters/ryo/kohou-dash-input`.
- Status: implementado; validação de jogabilidade pendente.

## Causa e comportamento

O Kohou ($47) pede frente $250, baixo puro $258, baixo-frente $260 e
soco $268. As direções originais usam máscara $FF. Durante o dash o
jogador frequentemente mantém frente e passa direto a baixo-frente:
a etapa de baixo puro falha. Diagonal e soco juntos também podem falhar
na etapa direcional antes que o leitor alcance a etapa separada de botão.

Somente no dash (estado 16/17), o Kohou do Ryo aceita:

- Frente → baixo ou baixo-frente → baixo-frente → soco.
- Frente já reconhecida → baixo-frente + soco no mesmo frame.
- Frente → baixo → baixo-frente + soco no mesmo frame.

Frente sem diagonal + soco e baixo sem frente + soco não ganham atalho.
O lado continua sendo normalizado pelo leitor original. Vale para dash
para frente/trás e para as versões fraca/forte pelo soco pressionado.

## Implementação

Hook compartilhado CMD_STEP filtra Ryo, d5=$47 e estado $10/$11.
Na etapa $258, retira só bit 3 da máscara d0, aceitando $02 e $0A.
Em $258/$260, input normalizado d1=$1A (diagonal + soco) entra no
conclusor nativo $1E0E0: reconhecimento, prioridade e marcação de força
continuam nos mesmos caminhos originais. Não cria comando na RAM por fora
do leitor e não aceita dois socos como se fossem um soco isolado.

Fora dessas condições segue o hook compartilhado com a máscara intacta.
Não altera tabelas compartilhadas, prazos, danos, frames, custos, força,
cancel de normais nem regras globais de buffer. Sem RAM nova. O buffer
continua de direcionais; soco é exigido no frame da execução.

## Validação

Build completo/isolado e hooks. Testar em jogo dash → Kohou fraco/forte,
lado esquerdo/direito, dash após aterrissagem, comando tradicional e atalho;
confirmar que frente+soco/baixo+soco não disparam Kohou e que normais,
Kou'ouken, Renbuken e cancels continuam originais.
