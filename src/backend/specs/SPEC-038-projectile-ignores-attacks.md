# SPEC-038: Projétil não é dissipado ao receber golpe

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/global/projectile-ignores-attacks` (global)

## Comportamento desejado

Para todos os personagens: um golpe (caixa de ataque) que encosta num projétil **não o desfaz**. O projétil continua voando e pode acertar. Ele só some quando acerta alguém (corpo), quando bate em outro projétil (regra de força do original) ou ao sair da tela.

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| `$22F4C` | Estado do projétil: com contato (`$70` bit 7) chama `$22D80`; se `d0 ≠ 0`, vai para o estado `$E` (dissipar, `$22F80`) |
| `$22D80` | Decide o contato. `$6D` = id do objeto atingido |
| `$22D9C` | Objeto atingido é projétil (`$6F` bit 7, ligado na criação em `$22A46`): o mais fraco (`$6B`) some; o mais forte sobrevive (`$22DC4`: `bclr #7,$70` / `d0 = 0`) |
| `$22DD2` | Objeto não é projétil: estado `≠ 8` → `d0 = 1` (dissipa). Vale para o corpo do oponente **e** para a caixa de ataque dele |

## Implementação

Hook em `$22DD2`: se o id atingido (`$6D`) é o **filho 5 ou 6** (caixa de ataque) do sprite de P1 ou P2 (`$109283`/`$109383` → objeto, ids em `+7`/`+8`), o projétil sobrevive como em `$22DC4`. Senão, segue o original.

## Pendências / riscos

- **Caixa de ataque do oponente:** ao encostar no projétil, ela pode ficar marcada como "já acertou" (`$70` bit 7 do filho) e o golpe dele deixar de acertar o Ryo nesse ataque. Conferir em jogo.
- **Golpes que anulam projéteis de propósito** (se algum especial do original depende disso) passam a não anular.

## Critérios de aceite

- [ ] Golpe normal do oponente no Kou'ouken: o projétil continua e acerta
- [ ] Especial corpo a corpo no projétil: idem
- [ ] Projétil contra projétil: regra do original (o mais forte passa)
- [ ] Projétil acertando o corpo: some normalmente
