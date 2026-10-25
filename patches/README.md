# Patches

Cada pasta é uma alteração isolada da P-ROM. As regras estão em [SPEC-001](../src/backend/specs/SPEC-001-rom-build-and-patches.md) e as decisões em [ADR-0001](../src/backend/adr/ADR-0001-modular-patch-architecture.md) e [ADR-0005](../src/backend/adr/ADR-0005-global-vs-character-patches.md).

```
python tools/build_rom.py         # gera rom/aof2r.zip
python tools/build_rom.py --list  # lista patches ativos por categoria
```

## Categorias

```
patches/
  manifest.json                           # ordem: "global" e depois "characters"
  global/<id>/patch.py                    # regra que vale para TODOS os personagens
  characters/<personagem>/<id>/patch.py   # alteração de UM personagem
```

- **Global**: botões, controles e mecânicas do jogo (barra, força dos especiais, custo etc.). A regra é a mesma para o elenco inteiro, mesmo que o patch altere dados de vários personagens.
- **Personagem**: muda um personagem específico (dano, frames, comandos ou golpes de um lutador), sem efeito nos outros.

Os globais são aplicados antes dos de personagem.

## Globais

| Patch | Spec |
|---|---|
| `controls-4button-layout` (C/D fortes, A+C arremesso, A+D uppercut, B+D chute baixo, START provoca) | [SPEC-002](../src/backend/specs/SPEC-002-controls-4button-layout.md) |
| `free-special-moves` (especiais não gastam barra; SUPER e DESPERATION mantêm o custo) | [SPEC-003](../src/backend/specs/SPEC-003-free-special-moves.md) |
| `special-strength-by-button` (A/B = especial fraco, C/D = especial forte, independente da barra) | [SPEC-004](../src/backend/specs/SPEC-004-special-strength-by-button.md) |
| `spirit-charge-abc` (carregar a barra exige A+B+C juntos) | [SPEC-005](../src/backend/specs/SPEC-005-spirit-charge-abc.md) |
| `special-cancel-input-buffer` (special cancel global ao conectar; comandos com 12 frames entre direcionais) | [SPEC-008](../src/backend/specs/SPEC-008-special-cancel-input-buffer.md) |
| `dash-snappy` (dash e dash para trás sem os quadros parados de início e fim) | [SPEC-011](../src/backend/specs/SPEC-011-dash-snappy.md) |
| `no-knockdown-normals` (golpe normal não derruba; só tontura e especiais) | [SPEC-012](../src/backend/specs/SPEC-012-no-knockdown-normals.md) |
| `hit-counter` (contador "N HIT COMBO" na tela, com a fonte do HUD) | [SPEC-013](../src/backend/specs/SPEC-013-hit-counter.md) |
| `persistent-bruises` (rosto machucado continua nos rounds seguintes da mesma luta) | [SPEC-014](../src/backend/specs/SPEC-014-persistent-bruises.md) |
| `rush-specials-true-combo` (especiais de sequência — Renbuken do Ryo, Robert, Takuma, Eiji e Yuri — com todos os hits em combo) | [SPEC-015](../src/backend/specs/SPEC-015-rush-specials-true-combo.md) |
| `jump-instant` (pulo sai na hora: quadro parado inicial de 2-3 → 1 frame; zera a velocidade de andar) | [SPEC-023](../src/backend/specs/SPEC-023-jump-instant.md) |
| `multi-hit-rearm` (especiais que prendem e batem várias vezes contam cada hit: Ryo Zanretsuken 19, Yuri Hyakuretsu Binta 10) | [SPEC-027](../src/backend/specs/SPEC-027-multi-hit-rearm.md), [SPEC-025](../src/backend/specs/SPEC-025-ryo-zanretsuken-19-hits.md) |
| `desperation-ryo-command` (DESPERATION de Robert, Takuma e Yuri com o comando do Ryo: ↓↘→↘↓↙← + C) | [SPEC-028](../src/backend/specs/SPEC-028-desperation-ryo-command.md) |
| `normal-remap` (chutes em pé por personagem — Yuri: B = forte perto, frente+B = bundada, trás+D = fraco com dano forte; Robert: frente+B = forte perto overhead, trás+D = forte longe, D neutro = fraco com dano forte, chute forte do dash derruba) | [SPEC-026](../src/backend/specs/SPEC-026-yuri-kick-remap.md), [SPEC-030](../src/backend/specs/SPEC-030-robert-kick-remap.md) |
| `normal-chains` (ao conectar, por personagem — Ryo: baixo B → chute, soco forte perto → B+D; Robert: soco forte perto → B+D) | [SPEC-018](../src/backend/specs/SPEC-018-ryo-crouch-kick-combo.md), [SPEC-020](../src/backend/specs/SPEC-020-ryo-normal-chains.md), [SPEC-031](../src/backend/specs/SPEC-031-robert-close-hp-chain.md) |

## Personagens

| Personagem | Patch | Spec |
|---|---|---|
| Ryo | `air-fireball-forward-jump` (Kou'ouken aéreo também no pulo para frente) | [SPEC-006](../src/backend/specs/SPEC-006-ryo-air-fireball-forward-jump.md) |
| Ryo | `kououken-weak-startup` (Kou'ouken fraco com startup de 11 frames) | [SPEC-009](../src/backend/specs/SPEC-009-ryo-kououken-weak-startup.md) |
| Ryo | `kohou-weak-short` (Kohou fraco: sobe pouco, 1 hit, derruba) | [SPEC-010](../src/backend/specs/SPEC-010-ryo-kohou-weak-short.md) |
| Ryo | `overhead-kick` (overhead em frente + B, chute forte longe em trás + D, D neutro novo) | [SPEC-016](../src/backend/specs/SPEC-016-ryo-overhead-kick.md) |
| Ryo | `renbuken-juggle` (Renbuken gasta 20% e recupera rápido depois do 4º hit; juggle pendente) | [SPEC-017](../src/backend/specs/SPEC-017-ryo-renbuken-juggle.md) |
| Ryo | `hitstun-extra` (pulo com soco forte: +12 de hitstun e aterrissagem 20 → 7; soco forte agachado com a vantagem do soco forte perto) | [SPEC-019](../src/backend/specs/SPEC-019-ryo-jump-punch-hitstun.md), [SPEC-024](../src/backend/specs/SPEC-024-ryo-crouch-punch-advantage.md) |
| Ryo | `haoh-easy-input` (Haoh Shoukouken: frente, trás, baixo, frente + soco, diagonais aceitas, 20 frames por passo) | [SPEC-021](../src/backend/specs/SPEC-021-ryo-haoh-easy-input.md) |
| Ryo | `hien-weak-startup` (Hien Shippuukyaku fraco: arranque de 12 → 1 frame) | [SPEC-022](../src/backend/specs/SPEC-022-ryo-hien-weak-startup.md) |
| Robert | `ryuga-weak-short` (Ryuga fraco: sobe pouco, 1 hit, derruba, como o Kohou fraco do Ryo) | [SPEC-029](../src/backend/specs/SPEC-029-robert-ryuga-weak-short.md) |

## Criar um patch

1. Escolha a categoria e crie `patches/global/<id>/patch.py` ou `patches/characters/<personagem>/<id>/patch.py`, exportando `PATCH` (o `id` é igual ao nome da pasta).
2. Escreva a spec em `src/backend/specs/`.
3. Adicione o id em `manifest.json`: em `"global"`, ou em `"characters": {"<personagem>": [...]}`.
4. Rode o build.
