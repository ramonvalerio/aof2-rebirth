# SPEC-027: Especiais que prendem e batem várias vezes contam cada hit

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/global/multi-hit-rearm` (global, com tabela por personagem)
- **Combina com:** SPEC-013 (contador), SPEC-025 (Zanretsuken)

## Comportamento desejado

| Personagem | Golpe | Hits registrados |
|---|---|---|
| Ryo | Zanretsuken (`$44`) | **19** |
| Yuri | Hyakuretsu Binta (`$43`) | **10** |

## Mecanismo comum

Esses golpes prendem o oponente no 1º contato e depois só tocam uma animação de golpes:

| Golpe | Efeito | Estado do oponente | Animação dos golpes |
|---|---|---|---|
| Zanretsuken (`$01E`/`$01F`) | `$08` (`$217CA`) | `$19` | `$14E` (10 ciclos de 3 socos) |
| Hyakuretsu Binta (`$17F`) | `$83` → `$03` (`$2198A`) | `$1C`/`$1D` | `$643` (avanço) → `$646`/`$644` (tapas) |

A caixa de ataque (filhos 5/6 do sprite) fica com `$70` bit 7 ("já acertou") depois do 1º contato e nunca é rearmada. O golpe não tem hits extras (byte 7 = 0), então sai 1 hit.

## Implementação

- **Hook `$1C1DA`** (começo do estado de ataque: `clr.l $20(a6)` / `jsr $1DF7E`): para cada linha da tabela (`$62` + `$230`), depois do 1º contato (`$21B = 0`) e enquanto `$247 > 0`, limpa o `$70` bit 7 dos filhos 5/6 uma vez por peça (`$56` do sprite = 1). Com `$247 > 0`, o contato segue o caminho de vários hits (`$1CEC0` → `$1CFA0`), sem trocar a reação do oponente.
- **Dados por golpe:** byte 7 = hits − 1; dano por golpe ajustado para o total ficar perto do original.

| Golpe | Dano original | Por hit | Hits extras |
|---|---|---|---|
| `$01E` Zanretsuken forte | `$28` | `$02` | 18 |
| `$01F` Zanretsuken médio | `$1E` | `$02` | 18 |
| `$17F` Hyakuretsu Binta | `$28` | `$04` | 9 |

Para outro golpe do mesmo tipo, basta uma linha nova em `MOVES`.

## Pendências

- **Soltura:** ao fim, o oponente é solto com uma queda. Se isso contar como mais um hit, reduzir os hits extras em 1.
- **Quantidade de peças:** se a animação tiver menos peças de ataque do que hits pedidos, o total fica menor (os tapas do Binta são 2 animações curtas; confirmar se ela repete até os 10).

## Critérios de aceite

- [ ] Zanretsuken colado: 19 HIT COMBO
- [ ] Hyakuretsu Binta colado: 10 HIT COMBO
- [ ] O oponente fica preso até o fim nos dois
- [ ] Outros especiais não mudam
