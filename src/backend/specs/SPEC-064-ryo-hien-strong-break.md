# SPEC-064: Ryo — Hien forte com cancelamento opcional

## Regra vigente: restaurada a versão manual

A pedido do usuário, removido o retorno/juggle automático das últimas
revisões. O Hien forte volta a poder ser cancelado no segundo acerto.

- Chute fraco: $01D; chute forte: médio $01C; dois chutes: forte $01B.
- Forte mantém custo global de 20% de Spirit (SPEC-063).
- Segundo acerto real: LP+LK (C+A físicos) durante o hitstop pede o break.
- Com break: flip vertical $11E, no mesmo X, e adversário relançado em
  juggle com poses de queda, velocidade 8, gravidade -0,25 e recuo zero.
- Sem break: sequência de ataque e retorno nativos do Hien.
- Defesa, erro, primeiro acerto, KO e fraco/médio não habilitam o break.

Estágios $3B4/$3B5 compartilhados com Kohou: forte inicia em 1; acertos
reais incrementam até 3; defesa desarma. O tradutor consome LP+LK apenas
no hitstop do estágio 3; fora dele o arremesso continua original.
ATTACK_STATE exige pedido, estágio 3 e adversário vivo antes de executar.
A reação direta automática de Hien em $21344 foi retirada. Relançamento
volta a acontecer exclusivamente ao consumir o cancelamento manual.

Flip usa a cópia do retorno $147, com velocidade horizontal/atrito zero,
impulso vertical 11,75 e gravidade -0,5625. Posição atual preservada.
A SPEC-065 mantém o adversário atingível no alto durante o juggle.
O cancelamento do Kohou continua manual e inalterado.

## Verificação

Build completo com 59 patches e hook_check aprovados. 96 cenários
simulados verificam exigência do pedido, estágio, vida, comando e Ryo;
verificada a remoção do Hien do despacho automático de reação.
Validação na partida pendente: forte → segundo acerto → LP+LK → flip e
juggle; sem LP+LK, retorno original; defesa/erro e Spirit 20%.
