# SPEC-010: Ryo: Kohou fraco curto

- **Status:** Implementada, aguardando teste em emulador. Combo após soco forte perto **depende do pushback** (pendente)
- **Patch:** `patches/characters/ryo/kohou-weak-short` (personagem)
- **Combina com:** SPEC-003 (sem custo), SPEC-004 (botão fraco → id `$024`), SPEC-007 (animação), SPEC-008 (cancel)

## Comportamento desejado

Kohou com soco fraco (A) como resposta rápida:

| | Kohou original (`$023`/`$024`) | Kohou fraco novo (`$024`) |
|---|---|---|
| Startup | 4 | 4 |
| Hits | 2 (chão em q2 + subida em q4) | **1** (só o do chão) |
| Subida | vy 12,75 px/f (~145 px, ~23 f até o topo) | **vy 7 px/f** (~43 px, ~12 f até o topo) |
| Queda do oponente | 1º hit: efeito `$0B` (sem queda); 2º hit: efeito `$01` (derruba) | efeito **`$01`** no único hit: **mesma queda do Kohou forte** |
| Recuperação | aterrissa depois de ~45 f no ar | aterrissa bem antes (~25 f no ar) |

O Kohou forte (C, `$023`) não muda.

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| anim `$0145` | Kohou (`$535E2`, 11 quadros). q2 (t=4–9) peça `$1143` = só caixa de ataque (filho 5). q3 = lista de comandos `$53645`. q4 peça `$0AE8` = corpo + ataque (2º hit) |
| `$53645` | Lista do lançamento: `de eb dd 01 c7 00 3e`, depois o opcode **`$D2`** e a peça `$0AE8` |
| opcode `$D2` → `$1DD92` | Alinha o ponteiro (`$22814`, `(a0+1) & ~1`) e chama `$1DE88`: lê **vy** (long), **gravidade** (word), **vx** (word) e **atrito** (word) e grava em `$28`, `$38`, `$30`, `$34` do jogador |
| `$2135E` | Efeitos de acerto pelo byte 6 do golpe (`$24B` no defensor, tabela `$21362`) |
| efeito `$0A` → `$2174C` | Se não foi defesa (`$21872`: `$7C & $F ≠ 3`): oponente no ar, reação `$1A` (cair), estado `$1F` |
| efeito `$08` → `$217CA` | Igual, com estado `$19` (usado pelo Zanretsuken) |
| efeito `$0B` → `$21734` | Só marca `$268`; sem queda |
| opcode `$DD` → `$1D3D6` | `move.b (a0)+,$20A`: troca o efeito de acerto no meio do golpe. No Kohou, `dd 01` no lançamento faz o 2º hit usar o efeito `$01` |
| efeito `$01` → `$21AD2` | Ajusta a direção (`$21AA6`) e a variante de reação (`$258 = $20` se não foi defesa). É a queda do 2º hit do Kohou forte (e do Haoh Shoukouken) |

## Implementação (patch de dados)

| Alteração | Onde | Original | Novo |
|---|---|---|---|
| Lista de quadros (11 × 4) | `$51F40` (ids livres `$7D0+`) | zeros | cópia da `$0145`; q4 usa `$0AE9` em vez de `$0AE8` |
| Lista do lançamento | `$51F71` (ímpar, como a original) | zeros | cópia de `$53645` com vy `$00070000` e peça final `$0AE9` |
| Animação `$17E` | `$050000 + $17E*4` | `0` | `$0B051F40` |
| Efeito de acerto do `$024` | `$23BA4 + $24*16 + 6` | `$0B` | `$01` (o do 2º hit do Kohou forte) |
| Animação do `$024` | `$23BA4 + $24*16 + 10` | `$0145` | `$017E` |

## Pendências

- **Combo com soco forte perto:** o hit do Kohou fraco é o do chão (frame 4), com o mesmo alcance do original. Se o pushback do soco forte deixa o oponente fora desse alcance, o combo ainda não sai. A medição está pronta em `frame_data.lua` (`pushback.csv`); o ajuste do pushback no cancel (SPEC-008, item 3) depende dela.
- **Duração no ar:** os quadros q4–q7 (24 f) e o q8 (espera) vêm do original. Com a subida menor, ele deve aterrissar perto do q8. Confirmar a recuperação real com `frame_data.lua`.
- **Visual:** a pose da subida passa a ser a `$0AE9` desde o lançamento (pula a `$0AE8`).

## Critérios de aceite

- [ ] Kohou com A: 1 hit, sobe pouco, o oponente cai com a mesma animação do Kohou com C
- [ ] Kohou com A na defesa: sem queda, sem 2º hit
- [ ] Kohou com C igual ao original (2 hits, sobe alto)
- [ ] `frame_data.lua`: total do Kohou fraco menor que o do forte
- [ ] Soco forte perto → Kohou fraco (cancel) combando (depende do pushback)

## Histórico

- A primeira versão usava o efeito `$0A` (reação `$1A`, estado `$1F`), que derruba com outra animação. Trocado para `$01`, o efeito que o próprio Kohou forte usa no hit que derruba.

## Specs relacionadas

Dano do Kohou fraco/forte: [SPEC-054](SPEC-054-ryo-kohou-damage.md).
