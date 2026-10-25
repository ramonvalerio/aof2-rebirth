# SPEC-030: Robert: chutes em pé remapeados (overhead em frente + B)

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/robert/kick-remap` (hooks compartilhados `$1D41E` e `$1D75C`, `charlib.KICK_SELECT`/`MOVE_RECORD`; a Yuri tem o próprio, SPEC-026)
- **Referência:** SPEC-016 (o mesmo esquema no Ryo)

## Comportamento desejado

| Entrada (em pé) | Golpe |
|---|---|
| **Frente + B**, em qualquer distância | Chute forte perto (`$031`, anim `$1B1`), **overhead** |
| **Trás + D** | Chute forte longe (`$032`, anim `$1B2`) |
| **D neutro** | Animação do chute fraco (`$1B0`) com propriedades e dano de golpe forte |
| B | Chute fraco, sem mudança |
| **Chute forte durante o dash** | **Derruba** (o chute fraco do dash não muda) |

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Tabela de comandos do Robert | `$1EC98`: `$30`/`$32` → entrada 9 (`$030`), `$31` → 11 (`$032`), `$33` → 10 (`$031`); `$3F` livre (`$FF`) |
| `$030` chute fraco | dano `$0C`, hitstop `$0C`, `$4F30`, reação `$01`, anim `$1B0` |
| `$031` chute forte perto | dano `$0C`, hitstop `$10`, `$4F30`, anim `$1B1` |
| `$032` chute forte longe | dano `$1C`, hitstop `$14`, reação `$02`, anim `$1B2` |
| Leitura do golpe | `$1D75C` (`$23BA4 + id × 16`); o `overhead-kick` do Ryo já usa `$1D762` |

## Implementação

- **Hook `$1D41E`** (seção do Robert, `$62 = 2`, d4 `$30`–`$33`; lado pelo `$5E` do sprite):
  - fraco + frente → `$33` (chute forte perto)
  - forte + trás → `$31` (chute forte longe)
  - forte sem trás → `$3F` (novo)
- **Hook `$1D75C`:** Robert com `$20(a5) = $3F` → registro do bloco: cópia do `$030` com dano **`$1C`**, hitstop **`$14`** e reação **`$02`**; segue em `$1D770`. Nos outros casos segue em `$1D762`, que é o hook do Ryo quando ele está ligado.
- **Dados:** `$031` bytes 8–9 `$4F30` → **`$4B20`** (overhead; o `$031` só sai pelo frente + B). Tabela de comandos `$1EC98 + $3F` `$FF` → `$0B` (entrada 11, mesmo handler do chute forte).

## Chute forte do dash

No dash (`$20C = $91`), `$1DCBC` troca a base do chute para `$2C`: d4 = `$3C` (fraco) / `$3D` (forte). Na tabela do Robert os dois vão para a entrada 18, golpe **`$038`** (dano `$0C`, hitstop `$08`, efeito `$00`, `$4710`, anim `$1B9`).

O hook `$1D75C` dá ao `$3D` um registro próprio: cópia do `$038` com efeito (byte 6) **`$15`**, o mesmo da rasteira do Robert (baixo D, `$035`, handler `$21616`): o oponente cai do mesmo jeito. (A 1ª versão usava `$01`, a queda do Kohou.) O `no-knockdown-normals` só impede a queda de golpe normal no **ar** (`$21BD4`), então no chão o oponente cai.

## Pendências

- **2 hits perto:** o chute forte perto do Ryo dava 2 hits perto (SPEC-016). Conferir se o do Robert também; se sim, zerar a flag do quadro do 2º hit.
- **Reação:** o tipo de reação vem de postura/altura/dano (`$21314`); o dano `$1C` (> `$10`) já dá a pesada.

## Critérios de aceite

- [ ] Frente + B longe e perto: chute forte perto, defensável só em pé
- [ ] Trás + D: chute forte longe
- [ ] D neutro: animação do chute fraco, com a reação pesada e mais dano
- [ ] B: chute fraco normal
- [ ] Trocando de lado, as direções acompanham
- [ ] Dash + D: o oponente cai como na rasteira (baixo D)
- [ ] Dash + B: igual ao original
