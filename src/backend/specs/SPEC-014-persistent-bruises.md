# SPEC-014: Rosto machucado persistente entre rounds

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/global/persistent-bruises` (global)

## Comportamento desejado

Quando o personagem fica com o rosto inchado (machucado), ele **continua assim no round seguinte da mesma luta**. Numa luta nova, o rosto começa limpo.

## Mapa de engenharia reversa

| Endereço / campo | O que é |
|---|---|
| `$5B` do **objeto de sprite** do jogador (`a4`, slot no byte `$3` do jogador) | Nível do rosto: 0 normal, 1 machucado, 2 muito machucado. É o seletor de peça alternativa usado pelo desenho (`$4C88`: `move.b $5B(a6),d0` escolhe a variante) |
| `$22384` | A cada acerto, `$26C` desce; ao zerar, recarrega com `$26D` e `$5B` + 1 (teto 2) |
| `$06C0–$0766` | Inicialização genérica de objetos; zera `$5B` em `$074A`. O sprite do jogador é recriado no round novo |
| `$A990–$A9BA` | Fim do round: compara as vidas e soma 1 nas **vitórias de round** do vencedor (`-$190` do jogador, word: P1 `$1090F0`, P2 `$1091F0`) |
| `$A9F8` / `$402(a5)` | Número do round; zerado no início da luta (`$19A52`, `$19A70`, `$19AB6`) |
| `$25A` do jogador | "BEAT BY": adversários vencidos em sequência no arcade (**não** é o placar da luta) |

**Como foi achado:** `tools/lua/field_watch.lua` gravou os campos raros dos registros dos jogadores. O endereço `$10955B` (o `$5B` do sprite do P1) foi o único que fez `0 → 1 → 2` enquanto o P1 apanhava e voltou a 0 no início do round 2.

## Implementação

Hook em `$074A` (`move.b d0,$5B(a0)` / `move.b d0,$5C(a0)`). O `$5B` **não** é zerado quando:
1. o objeto inicializado é o sprite de um jogador (`a0 == a5 + byte($3 do P1 ou P2) << 8`), **e**
2. algum jogador já venceu um round nesta luta (`$1090F0` ou `$1091F0` ≠ 0).

Nos outros casos, inclusive no 1º round de cada luta, a inicialização é a original.

## Pendências / riscos

- **Ordem da recriação:** o teste usa o slot de sprite ainda registrado no jogador (byte `$3`). Se o jogo trocar de slot ou atualizar esse byte antes de inicializar o objeto novo, o patch não reconhece o sprite e o rosto zera como antes. Confirmar em jogo.
- **Animações de entrada:** se alguma animação de início de round gravar `$5B` (opcode de peça `$4E72`), ela pode sobrescrever o valor mantido.
- **Round empatado (0 × 0):** se o 1º round terminar empatado, ninguém tem vitória e o rosto zera no round seguinte.

## Critérios de aceite

- [ ] Rosto machucado no round 1 → continua machucado no round 2
- [ ] Nível 1 e nível 2 mantidos como estavam
- [ ] Luta nova (próximo oponente no arcade): rosto limpo
- [ ] O personagem que não apanhou continua normal
