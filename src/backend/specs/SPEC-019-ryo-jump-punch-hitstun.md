# SPEC-019: Ryo: pulo com soco forte com hitstun e aterrissagem rápida

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/hitstun-extra` (personagem; antes `jump-punch-hitstun`, ver SPEC-024)

## Comportamento desejado

Quando o pulo com soco forte do Ryo acerta, o oponente fica travado na reação por mais tempo, e o Ryo aterrissa rápido. Isso permite emendar um golpe no chão antes de o oponente se recuperar: a recuperação da aterrissagem precisa ser **menor** que o hitstun que sobra.

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Golpe | Comando `$2B` (soco forte no ar), golpe `$006`, animação `$0126` |
| `$0126` | q0 cmd, q1 `$070E` 6 frames, q2 fim `$80` (segura até tocar o chão), **q3–q7 aterrissagem**: 2 + 12 + 3 + 3 = 20 frames |
| Toque no chão | `$1C1F4` / `$1C226`: `$58` do sprite = 1 → a animação segue depois do quadro de fim |
| Reação: escolha | `$21314`: d1 = postura (0 em pé, `$10` agachado, `$20` no ar) + altura do acerto (+4/+8) + nível (+1 se `$72 > $10`, +2 no caso especial); `$20604` → animação `$20662[char][d1]`. **O byte 14 do golpe não entra na escolha** |
| Reação: estado 6 (`$1C434`) | Animação de reação parada enquanto o atacante está no hitstop (`$41 = 2`) |
| Reação: `$1C454` | Fim do hitstop: zera o contador do quadro (`$56` do sprite) e passa para o estado 7 |
| Reação: estado 7 (`$1C460`) | Toca a reação até o fim (`$A69` bit 7) = **hitstun** |
| Hitstop do atacante | `$1D0C8`: `$43` = byte 5 do golpe; no ar, caindo, ganha mais (`$1D0F6`–`$1D104`) |

## Implementação

- **Hook `$1C454`:** se o atacante (`$64` do defensor) é o Ryo com `$230 = $2B`, o contador do 1º quadro da reação vale **12** em vez de 0: o oponente fica 12 frames a mais na reação. Nos outros casos, o original.
- **Dados:** aterrissagem da `$0126`, q4 12 → 2, q5 3 → 2, q6 3 → 1. São **7 frames** no total (eram 20).

## Pendências

- **Calibrar:** os 12 frames extras são uma estimativa. Medir com `tools/lua/frame_data.lua` ou `knockdown_log.lua` e ajustar `EXTRA_HITSTUN`.
- **Pulo fundo × raso:** acertando alto, o Ryo demora mais para cair, e o hitstun extra pode não bastar.
- **SPEC-018:** como o byte 14 não escolhe a reação, a troca leve → pesada no baixo B provavelmente não fez efeito. O mesmo hook de hitstun pode ser usado no baixo B (`$230 = $38`).

## Critérios de aceite

- [ ] Pulo com soco forte acerta → soco/chute no chão emenda (2 HIT COMBO)
- [ ] A aterrissagem do pulo com soco forte fica visivelmente mais curta
- [ ] Os outros golpes e personagens não mudam
