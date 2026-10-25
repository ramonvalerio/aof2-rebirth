# SPEC-025: Ryo: Zanretsuken com 19 hits

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/zanretsuken-19-hits` (mecanismo `charlib.multi_hit_block`, SPEC-027)
- **Combina com:** SPEC-013 (contador conta hits com o oponente preso)

## Comportamento desejado

O Zanretsuken acerta **19 socos** e o contador mostra **19 HIT COMBO**.

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Comando | `$44` → handler `$1D4DC` → níveis `$01E` (forte), `$01F` (médio) |
| Animação | Seq `$8018`/`$8019` → `$414E` → anim `$14E`: 40 quadros de 2 frames (80 frames), **10 ciclos** de [comando + 3 peças de ataque] |
| Comandos do ciclo | `$DC xx yy` (`$1D3C2`): grava `$26E/$26F` do atacante = posição do oponente preso; `$DD 01` muda o efeito; `$E6` |
| Efeito `$08` (`$217CA`) | 1º acerto: oponente no estado `$19` (preso, reação `$1A`). Já em `$19`, o acerto seguinte não troca a reação |
| Hits extras | Byte 7 do golpe → `$247` (`$1D7C4`); com `$247 ≠ 0` o contato segue o caminho de vários hits (`$1CEC0` → `$1CFA0`) e `$21338` desconta 1 |
| Caixa de ataque | Filhos 5/6 do sprite; depois do acerto ficam com `$70` bit 7 ("já acertou") e só voltam se alguém limpar (SPEC-008) |

**Original:** 1 hit, porque a caixa nunca é rearmada e não há hits extras. O resto da animação só segura o oponente.

## Implementação

- **Dados (`$01E`, `$01F`):** byte 7 (hits extras) `0` → **18**. Dano por soco (bytes 0 e 1) `$28`/`$1E` → **`$02`** (19 × 2 = 38, perto do original).
- **Hook `$1C1DA`** (começo do estado de ataque, hook compartilhado `charlib.ATTACK_STATE`): Ryo com `$230 = $44`, depois do 1º contato (`$21B = 0`) e com `$247 > 0`: limpa o `$70` bit 7 dos filhos 5/6 uma vez por peça (quando o contador do quadro do sprite, `$56`, vale 1). Com `$247` em 0, para de rearmar: 1 + 18 = 19 hits.

## Pendências

- **Soltura:** ao fim, o estado `$19` solta o oponente com uma queda (`$1C8E0`: `$20A = $01`). Se isso contar como mais um hit, o total vira 20. Ajustar os hits extras para 17 nesse caso.
- **Versão fraca:** o 3º nível (`$020`) aponta para outra animação; não foi mudado.
- **Dano:** `$02` por soco é uma estimativa; ajustar se ficar fraco ou forte demais.

## Critérios de aceite

- [ ] Zanretsuken colado: 19 HIT COMBO
- [ ] O oponente fica preso até o fim e cai
- [ ] Dano total parecido com o original
