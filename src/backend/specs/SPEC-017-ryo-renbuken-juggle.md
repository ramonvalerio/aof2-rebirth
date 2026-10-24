# SPEC-017: Ryo: Renbuken com custo, recuperação curta e juggle

- **Status:** Custo e recuperação implementados, aguardando teste. Juggle **pendente** (medição)
- **Patch:** `patches/characters/ryo/renbuken-juggle` (personagem; antes `renbuken-cancel`)
- **Combina com:** SPEC-003 (especiais grátis), SPEC-015 (Renbuken em combo)

## Comportamento desejado

| Item | Resultado |
|---|---|
| Custo | O Renbuken gasta **20%** da barra |
| Recuperação | Curta depois do 4º hit, para emendar outro golpe (ex.: Kohou) |
| 4º hit | O oponente sobe **reto para cima** (sem ser jogado para trás) e fica **em juggle**: pode levar mais um golpe antes de cair |
| Cancel | **Retirado** (v1/v2 tinham cancel em Kohou fraco +20% / Zanretsuken +40%) |

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Barra | `$224(a6)` word, o byte alto é a unidade. Máximo em `$256(a6)` |
| Custo | `$1D7B2` copia o byte 4 do golpe para `$241`; `$1D7DE` desconta (mínimo 1) |
| Sequência | `$2385E`: `$8120 $8122(→$817D, SPEC-015) $8120 $0121`. A `$0121` também é o uppercut (golpe `$001`) |
| `$0121` | q0 cmd (`c7 0044 c7 0172` + peça `$0622`), q1 `$0623`, q2 cmd (`de` + peça `$0624`), q3 `$0625` 9 frames (4º hit), q4 cmd (`d0` + peça `$0624`) 5, q5 `$0623` 5, q6 `$0622` 4 |
| Reação do defensor | `$21344` despacha pelo efeito (`$24B`) na tabela `$21362`; nível da reação nos bits 0–1 de d1 |
| Efeito `$0A` (`$2174C`) | Só age se `$7C & $F = 3` (`$21872`). Liga `$60` bit 4, reação `$1A`, estado `$40 = $1F` |
| Estado `$1F` (`$1C96A`) | **"Pegada":** o defensor fica preso à posição do atacante (`$1C818`, tabela `$20BAC`) enquanto o atacante está em ataque (`$40 = 3`). Quando o ataque acaba (`$1C8E0`), gera uma queda (`$20A = $01`). **Não é juggle** |
| Efeito `$0B` (`$21734`) | 1º hit do Kohou forte: nível 0 e `$268 = 1` (provável marca de "pode ser acertado no ar", o 2º hit do Kohou pega o oponente subindo) |
| Física do jogador | `$1C710`: `$30` vel. x (word), `$34` atrito, `$28` vel. y (long), `$38` gravidade; `$18` altura |

## Implementação atual

- **Hook `$1D7B2`:** para o Ryo e o golpe `$021`, `$241` = 20% do máximo.
- **Animação `$11D`** (id livre): cópia da `$0121` com a recuperação **5+5+4 → 2+2+2** (8 frames a menos). As três listas de comandos vão copiadas num bloco de dados. A sequência passa a terminar em `$011D`; o uppercut continua com a `$0121`.

## Histórico

- **v1:** cancel no hitstop do 4º hit (Kohou fraco / Zanretsuken, com custo). Trocar o efeito do Renbuken para `$01` fez o golpe derrubar no 1º hit (o efeito vale para todos os hits); revertido.
- **v2:** buffer do comando durante o Renbuken; o Kohou do cancel usava o efeito `$0A`. Não funcionou como juggle: o `$1F` é uma pegada.
- **v3 (atual):** sem cancel. Custo, recuperação curta e medição do juggle.

## Juggle: próximo passo (medição)

Antes de implementar o juggle é preciso ver, em jogo, o estado de um oponente acertado no ar. Com `tools/lua/knockdown_log.lua` (agora grava também `$268`, `$7C`, x, altura e velocidades):

1. **Kohou forte** acertando: o 2º hit pega o oponente no ar (juggle natural do jogo).
2. **Renbuken** completo, com o patch novo.

Com isso dá para escolher a reação do 4º hit (subir reto, `$268`, gravidade) e quanto tempo o oponente fica no ar.

## Critérios de aceite

- [ ] Renbuken desconta 20% da barra
- [ ] Depois do 4º hit, o Ryo volta a agir bem mais cedo
- [ ] Uppercut (A+D) continua igual
- [ ] (pendente) 4º hit: oponente sobe reto e pode levar mais um golpe
