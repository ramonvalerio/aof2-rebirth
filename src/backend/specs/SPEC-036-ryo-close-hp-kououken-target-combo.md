# SPEC-036: Ryo: target combo soco forte perto → Kou'ouken fraco

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/close-hp-kououken-target-combo` (personagem; hooks compartilhados `$1D676` e `$22AC2`)
- **Depende de:** SPEC-008 (special cancel), SPEC-009 (Kou'ouken fraco com startup 11), SPEC-033 (fraco = ↓↘→ + C+D)

## Comportamento desejado

Soco forte perto que acertou, cancelado em ↓↘→ + C+D (Kou'ouken fraco), **sempre** combina: em qualquer distância, no canto ou fora dele, contra qualquer personagem.

## Por que falhava

| Situação | Causa |
|---|---|
| Canto / colado | O projétil nasce 96 px à frente do Ryo (`$229C0`, argumento `$FFA0`) e a caixa do pequeno (anim `$172`) fica de 4 a 42 px **atrás** da origem: cobre 54–92 px à frente. Colado, o corpo do oponente fica antes de 54 px e o projétil nasce depois dele |
| Pushback grande / personagem pequeno | O oponente fica longe da área de nascimento e o projétil leva mais frames para chegar |

## Implementação

1. **Marca no cancel** (hook compartilhado `$1D676`, `charlib.SPECIAL_CHOSEN`, depois do `kououken-three-buttons` na ordem do manifest): `$230` ainda é o golpe que está sendo cancelado (`$1D6E2` só grava o novo depois). Se `$230 = $23` (soco forte perto), `$21B = 0` (já conectou) e a versão escolhida é `$013` (fraco), marca `$3A9` do Ryo e **zera o empurrão do oponente** (`$20` velocidade X, `$30`/`$34` vx e atrito, como `$1C6EE`–`$1C6FE`); senão desmarca.
2. **Projétil em cima do oponente** (hook compartilhado `$22AC2`, `charlib.PROJ_SPAWN_X`: `add.w $10(a3),d3` / `move.w d3,$10(a0)`): projétil do Ryo com a marca nasce com X = X do oponente (`$64`). A caixa do pequeno ocupa 4–42 px de um lado da origem e o corpo do oponente ~30 px para cada lado, então encosta qualquer que seja o lado. Desmarca.

**Correção 2 (2026-10-25):** os blocos do `$22AC2` testavam `$62(a3)`/`$3A9(a3)`, mas no `$229C0` (opcode `$D8` da animação) `a3` é o objeto de **sprite**; o jogador é `a6`. A marca nunca era encontrada e o projétil nascia na mão. Corrigido para `a6`. Também passou a zerar o empurrão do oponente no cancel.

**Correção 1 (2026-10-25):** a 1ª versão punha a origem 20 px à frente do oponente, supondo a caixa atrás da origem. Em jogo não acertava (o projétil passava além do oponente): a caixa fica do outro lado. Na origem do oponente vale para os dois casos.

O tempo cabe: o projétil sai 11 frames depois do cancel e a caixa liga 2 frames depois; o soco forte perto dá reação pesada (26 frames) mais hitstop (`$10`).

`$3A9` é livre no registro do jogador (`ram_scan.lua`; `$3A0`–`$3A7` hit-counter, `$3A8` kohou-impact-sound).

## Pendências / riscos

- **Defesa:** com o soco defendido (`$21B` também zera), o projétil também nasce em cima do oponente (defendido como um projétil normal).
- **Visual:** nesse combo o projétil aparece já junto do oponente, não saindo da mão do Ryo.
- **Hitstun:** não é estendido. Se em algum caso o oponente sair da reação antes (ex.: cancel muito tarde), o próximo ajuste é congelar a reação até o projétil.

## Critérios de aceite

- [ ] Soco forte perto → ↓↘→ + C+D: combina no meio da tela
- [ ] Idem com o oponente no canto
- [ ] Idem contra personagens grandes e pequenos (ex.: Jack, Yuri)
- [ ] Kou'ouken fraco sem cancel: nasce na mão, como antes
- [ ] Kou'ouken médio/forte no cancel: comportamento normal
