# SPEC-081: Dash imediato ao levantar do agachamento

- Patch global: `crouch-stand-dash`.
- Combina com `dash-snappy` (SPEC-011), detector de dois toques por bordas,
  e segue a ideia de `landing-dash` (SPEC-056).
- Status: implementado; validação ao vivo pendente.

Levantar do agachamento travava o dash. O detector de dois toques $1CCDA só
roda no neutro ($1BA16) e ao andar ($1BAA4/$1BAD0). O agachado (estado 5,
$1BEA4) não o chama, ao contrário do que a SPEC-011 supunha. Soltar o baixo
emite o comando 8, que leva ao estado 11 ($1BE4A, $20C=$87, levantando).
Esse estado espera o fim da animação ($A69 bit 7) para voltar ao neutro.
Toques dados no frame de soltar o baixo e durante o levantar se perdiam.

## Estados envolvidos

| Estado $40 | $20C | Handler | Situação |
|---|---|---|---|
| 10 | $84 | $1BDDC | agachando |
| 5 | $85 | $1BEA4 | agachado |
| 5 | $86 | $1BEA4 | defesa agachada |
| 11 | $87 | $1BE4A | levantando |

## Implementação

Hook $1BECE (estado 5, `btst #1,$270 / bne`): com baixo segurado, nada muda.
No frame em que o baixo é solto, fora da defesa agachada ($86), chama $1CCDA
antes do comando 8. Se o segundo toque chega nesse frame, o dash sai direto.

Hook $1BE74 (estado 11, depois da checagem de defesa $1BE16): chama $1CCDA
a cada frame da animação de levantar. A defesa mantém a prioridade, como já
acontece no neutro; golpes ($1D808) vêm depois do dash, na mesma ordem do
neutro ($1BA5C → $1BA64).

Ao detectar o dash, repete a limpeza do fim do estado 11: $60 bit 5
(agachado) e o bit do jogador em $17BD(a5). Depois salta para $1BC84, que
escolhe dash para frente ou para trás pelo lado atual (comandos 4/5).

O detector continua sem aceitar toques com baixo ou cima segurados, então
meia-lua e comandos especiais não viram dash. Um toque dado durante o
levantar pode ser completado no neutro, e vice-versa: o estado $212/$213/$210
do detector é o mesmo. Nenhum byte de RAM novo é usado.

## Validação

Build completo. Testar no emulador e na MiSTer: agachado → soltar → dois
toques para frente/trás (dash imediato, sem esperar levantar); segundo toque
no frame de soltar o baixo; defesa agachada → sem dash; meia-lua + soco
partindo do agachado continua saindo o especial; golpe durante o levantar
continua saindo; P1/P2 e lados trocados.
