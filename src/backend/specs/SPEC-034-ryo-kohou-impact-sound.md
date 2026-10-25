# SPEC-034: Ryo: som de impacto no Kohou com os 2 hits

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/kohou-impact-sound` (personagem; hook compartilhado `$224BE`, `charlib.HIT_SOUND`)

## Comportamento desejado

Quando o Kohou forte pega os **2 hits**, **os dois** tocam o mesmo som de acerto "pesado" dos hits do Hien Shippuukyaku. Como no 1º hit o 2º ainda não aconteceu, a regra é: 1º hit **sem defesa e colado** no oponente (origens `$10` a até **80 px**) → o 2º vem. O 2º hit tem caixa de 0 a 42 px à frente do Ryo e a frente do corpo do oponente fica a ~34 px da origem dele; o 1º hit alcança até ~114 px, então de mais longe só o 1º pega. Defendido, ou 2º hit sozinho (ex.: antiaéreo), continua com o som original.

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| opcode `$E7 xxxx` (`$2299E`, via `$1B0F6`) | Grava `xxxx` em `$A5C` do jogador: **som fixo de acerto** do golpe. O Hien tem `e7 0140` na lista `$533BC`; o Kohou não tem `$E7` |
| `$1DF08` / `$1E5EC` | Zeram `$A5C` (início de golpe / reset) |
| `$224BE` | No contato corpo a corpo (`$2248E`, a6 = defensor, a0 = `$64` atacante): `$A5C` do atacante → `$A5E` do defensor. Projéteis: `$224EA` (`$30` do projétil) |
| `$21E34` | Som do acerto: toca `$A5E` se ≠ 0; senão sorteia na tabela `$21E60` (força pelo `d1 & $C` + aleatório 0–7). Zera `$A5E` |

## Implementação

Bloco no hook compartilhado `$224BE` (roda depois da cópia original). Atacante Ryo (`$62(a0) = 1`):

| Caso | Ação |
|---|---|
| Defendido (`$7C(a6) & $F = 3`, como `$21872`) | som original; desmarca |
| `$230 = $47` (Kohou), efeito `$20A(a0) = $0B` (hit 1) e `\|$10(a0) - $10(a6)\| <= 80` | `$A5E(a6) = $0140`; marca `$3A8(a0) = 1` |
| Hit 1 mais longe que 80 px | som original; desmarca |
| Kohou com efeito `$01` (hit 2; `dd 01` no lançamento `$53645`) com a marca | `$A5E(a6) = $0140`; desmarca |
| Hit 2 sem a marca | som original |
| Outro golpe do Ryo | desmarca |

`$3A8` é livre no registro do jogador (`ram_scan.lua`: nunca muda durante o jogo; o hit-counter usa `$3A0`–`$3A7`).

O Kohou fraco (SPEC-010) tem um hit só, com efeito `$01` e sem marca: nunca toca o som novo.

**Correção (2026-10-25):** a 1ª versão separava os hits pela altura (`$18`). De perto o 2º hit acerta no frame do lançamento, com `$18` ainda 0, e era tratado como 1º hit: o som não tocava. Agora usa o efeito de acerto `$20A`.

## Pendências / riscos

- **Limite de 80 px** é estimado pelas caixas (SPEC-007/análise de frame data). Se tocar com 1 hit perto do limite, diminuir `CLOSE`; se não tocar colado, aumentar.
- Se o 1º hit acerta, o 2º erra, e no **próximo** Kohou só o 2º acerta (sem outro golpe do Ryo acertando entre eles), a marca antiga faz tocar o som de impacto.

## Critérios de aceite

- [ ] Kohou forte colado, 2 hits: os 2 hits têm o som do Hien
- [ ] Kohou forte de longe, só o 1º hit: som original
- [ ] Kohou forte só com o 2º hit (antiaéreo): som original
- [ ] Kohou forte defendido: som de defesa original
- [ ] Hien Shippuukyaku e outros golpes: sem mudança

## Kohou médio com som original

O filtro agora exige a animação exclusiva $17B do forte (SPEC-062), em vez
de aceitar qualquer comando $47. O médio ($025, animação $145) e o fraco
($024, $17E) mantêm o som original já copiado pelo motor. A marca $3A8 é
limpa nesses casos, impedindo herdar o som pesado de um forte anterior.
As demais condições do som pesado no forte continuam iguais.
