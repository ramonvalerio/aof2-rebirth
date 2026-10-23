# SPEC-006: Ryo: Kou'ouken aéreo no pulo para frente (buff)

- **Status:** Implementada; limite de altura **a calibrar** com medição em jogo
- **Patch:** `patches/characters/ryo/air-fireball-forward-jump` (personagem)
- **Combina com:** SPEC-003 (custo) e SPEC-004 (força pelo botão); o patch continua em `$1D53E`, onde a SPEC-004 escolhe a força

## Comportamento desejado

| Pulo do Ryo | Original | Novo |
|---|---|---|
| Neutro | Kou'ouken aéreo sai | Igual |
| Para trás | Sai | Igual |
| Para frente | **Não sai** (vira soco/chute aéreo) | **Sai** |

Os outros personagens não mudam.

## Mapa de engenharia reversa

| Endereço / campo | O que é |
|---|---|
| `$62(a6)` | Personagem, na ordem da tela de seleção: 1 Ryo, 2 Robert, 3 Eiji, 4 Jack, 5 Lee, 6 King, 7 Micky, 8 John, 9 Mr.Big, 10 Takuma, 11 Yuri, 12 Temjin, 13 Geese (nomes em `$FDA3C`). A entrada 0 das tabelas por personagem é uma cópia não usada |
| `$18(a6)` | Altura (word alto de 16.16); `$28` = velocidade vertical; `$38` = gravidade (`$1C6CA`) |
| `$30(a6)` | Velocidade horizontal; o sinal segue a direção (`$1DD54`) |
| `$5E(a6)` bit 0 | Direção: 1 = olhando para a direita |
| `$60(a6)` bit 4 | No ar |
| `$1E3B6` | Início dos 3 pulos (comandos 9/11/13): estado 4 (`$1C32A`) e `$60` bit 4 |
| `$1D52A` | Kou'ouken aéreo para baixo (meia-lua + soco). No ar exige `$18 ≥ $60`, senão soco (`$1DC88`) |
| `$1D4EC` | Kou'ouken aéreo reto (meia-lua + chute). Exige ar e `$18 ≥ $60`, senão chute (`$1DC9E`) |

## Causa

A magia aérea só sai a partir de uma altura mínima (`$60`). O pulo para frente do Ryo não alcança essa altura, ou só a alcança tarde demais. Por isso o comando cai sempre na alternativa: soco ou chute aéreo.

## Implementação

Os dois testes de altura (`$1D534` e `$1D4F6`) passam por um bloco que, para o Ryo no pulo para frente, usa `FORWARD_MIN_HEIGHT` no lugar de `$60`. "Pulo para frente" significa que o sinal de `$30` combina com a direção (`$5E` bit 0). Pulo neutro (`$30 = 0`), pulo para trás e os outros personagens seguem o teste original.

## Calibração (pendente)

`FORWARD_MIN_HEIGHT` começa em `$30` (metade do original). O valor certo depende da altura máxima do pulo para frente do Ryo, que não foi lida estaticamente: os parâmetros do pulo ficam embutidos nos scripts de animação.

Medição: rodar `tools/lua/input_logger.lua`, fazer com o Ryo um pulo neutro, um para trás e um para frente, e ver as colunas `p1_height` / `p1_xvel` no CSV. O limite deve ficar abaixo do pico do pulo para frente, numa proporção parecida com a do pulo neutro (`$60` em relação ao pico dele).

## Critérios de aceite (teste manual no FBNeo)

- [ ] Ryo solta o Kou'ouken aéreo (A/C e B/D) no pulo para frente
- [ ] Pulo neutro e para trás continuam como antes
- [ ] Logo após sair do chão ainda não sai magia (o limite mínimo existe)
- [ ] Robert e os outros personagens não mudam
