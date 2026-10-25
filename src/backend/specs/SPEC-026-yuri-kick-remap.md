# SPEC-026: Yuri: chutes em pé remapeados

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/global/normal-remap` (seção da Yuri; antes `characters/yuri/kick-remap`, ver SPEC-030)

## Comportamento desejado

| Entrada (em pé) | Golpe |
|---|---|
| **B**, em qualquer distância | Chute forte perto (`$170`, anim `$630`) |
| **Frente + B** | Chute forte longe, a "bundada" (`$177`, anim `$637`) |
| **Trás + D** | Animação do chute fraco (`$172`, anim `$632`) com dano de golpe forte |
| D neutro | Original (longe: bundada; perto: chute forte perto) |

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Seleção | `$1DC9E`: d4 = `$30` fraco longe, `$31` forte longe, `$32` fraco perto, `$33` forte perto → `$1D41E` |
| Tabela de comandos da Yuri | `$30`/`$32` → `$172`, `$31` → `$177`, `$33` → `$170` (handler `$1D65A`) |
| `$172` (chute fraco) | dano `$0A`, hitstop `$0A`, `$4F30`, anim `$632` |
| `$177` (bundada) | dano `$14`, hitstop `$0D`, efeito `$16`, anim `$637` |
| `$170` (forte perto) | dano `$0C`, hitstop `$08`, anim `$630` |

## Implementação

- **Hook `$1D41E`** (`andi.w #$7F,d4` / `move.w d4,$20(a5)`), só para a Yuri (`$62 = 11`) com d4 `$30`–`$33`. O lado vem do `$5E` do sprite, como no dash e no `overhead-kick` do Ryo:
  - fraco + frente → `$31` (bundada)
  - fraco sem frente → `$33` (chute forte perto)
  - forte + trás → `$30` (`$172`)
- **Dados:** como o B sempre é remapeado, o `$172` só sai pelo trás + D. O registro dele ganha dano **`$14`** e hitstop **`$0D`** (os da bundada). Com dano > `$10`, a reação do oponente é a pesada (`$21C42`). O efeito especial da bundada (`$16`) não foi copiado.

## Pendências

- **B agachado e no ar** não mudam (d4 `$38`, `$3A`).
- **D neutro perto** continua sendo o chute forte perto, igual ao novo B.

## Critérios de aceite

- [ ] B longe e perto: chute forte perto
- [ ] Frente + B: bundada
- [ ] Trás + D: animação do chute fraco, com a reação pesada e mais dano
- [ ] Chutes agachados e aéreos da Yuri iguais
- [ ] Outros personagens não mudam
