# SPEC-024: Ryo: soco forte agachado com a vantagem do soco forte perto

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/crouch-punch-advantage` (personagem; antes `hitstun-extra`, junto com a SPEC-019, revertida)

## Comportamento desejado

O soco forte agachado do Ryo fica **igual** ao soco forte perto em vantagem de frames (no acerto).

## Frame data

| | Soco forte perto `$127` (`$007`) | Soco forte agachado `$124` (`$004`), antes | Depois |
|---|---|---|---|
| Startup | 3 | 4 | **3** |
| Ativos | 9 | 11 | **9** |
| Recuperação | 6 | 11 | **6** |
| Total | 18 | 26 | **18** |
| Hitstop (byte 5) | `$10` | `$0C` | **`$10`** |
| Reação do oponente em pé | pesada, 26 | leve, 16 | **16 + 10 = 26** |
| Reação do oponente agachado | 14 | 14 | 14 |

## Reação (hitstun)

`$21314` monta o índice da reação: postura (0 em pé, `$10` agachado, `$20` no ar) + altura do acerto (+4/+8) + nível (+1 se o dano `$72 > $10`, `$21C42`). A animação vem de `$20662[char][índice]`. Para todos os personagens:

| Índice | Duração |
|---|---|
| em pé, leve (0/4/8) | 16 |
| em pé, pesada (1/5/9) | 26 |
| agachado (`$10`/`$11`) | 14 |

O soco forte perto (dano `$14`) dá a pesada; o agachado (dano `$0C`), a leve. Em vez de mudar o dano, o hook de hitstun (`$1C454`, SPEC-019) dá **+10 frames** ao soco forte agachado (`$230 = $29`) quando o oponente está em pé (`$60` bit 5 = 0).

## Implementação

- **Animação `$124`:** q1 2 → 1, q3 9 → 7, q4 4 → 2, q5 4 → 2, q6 3 → 2.
- **Golpe `$004`:** byte 5 (hitstop) `$0C` → `$10`.
- **Hook `$1C454`:** `$29` + oponente em pé → `$56` = 10. O `$2B` (pulo com soco forte, +12) continua.

## Pendências

- **Soco fraco agachado** (`$123`, `$003`) não foi mudado. Se "soco abaixado" for ele, o mesmo ajuste se aplica.
- **Defesa:** o blockstun não passa pelo mesmo caminho; a vantagem na defesa não foi igualada.

## Critérios de aceite

- [ ] Soco forte agachado acerta → o mesmo golpe que emenda depois do soco forte perto também emenda
- [ ] Contra oponente agachado, igual ao soco forte perto
