# SPEC-022: Ryo: Hien Shippuukyaku fraco com startup instantâneo

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/hien-weak-startup` (personagem)
- **Combina com:** SPEC-004 (força pelo botão: B = versão fraca `$01D`)

## Comportamento desejado

O Hien Shippuukyaku fraco (↙ carregado, → + B) começa a chutar na hora, sem a pausa inicial.

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Comando | `$43` (↙ segurado 20 frames, → + chute; lista `+$238` da linha do Ryo) → handler `$1D504` |
| Versões | `$01B` forte (anim seq `$8000` → `$4144`), `$01C` média, `$01D` fraca (seq `$8006` → `$413E`) |
| `$013E` | 1 quadro: comando de **12 frames**. Lista `$533BC`: `c7` som, `e5`, `c7` som, `e7 0140`, `d2` velocidade (vy `$48000`, gravidade `$FFD0`, vx `$0600`), `cf 00 4144` (próxima animação: o voo do forte), peça `$068B` |
| `$0144` | q0: o mesmo arranque de 12 frames (vx `$0A00`); q1–q11: chutes (peças `$1000`, `$068C`, `$1009`–`$100B`), q13 aterrissagem |
| `$CF` (`$4F44`) | Grava 3 bytes em `$5A`/`$54`/`$55` do objeto: a próxima animação |

O startup do fraco são os 12 frames da peça de arranque `$068B`. A velocidade já é aplicada no início, mas as caixas de ataque só vêm na `$0144`.

## Implementação

`$013E` q0: duração **12 → 1** (byte `$53340`). O forte não muda.

## Pendências

- **Altura/alcance:** com a velocidade aplicada só 1 frame antes dos chutes, o fraco começa a chutar mais baixo e anda menos antes do 1º chute. Conferir se ainda acerta de perto.
- Se a versão média (`$01C`, mesmo arranque do forte) também precisar, a peça está no q0 da `$0144`.

## Critérios de aceite

- [ ] ↙ (segurar), → + B: o Ryo chuta logo no início
- [ ] Hien forte (→ + D) igual ao original
