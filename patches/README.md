# Patches

Documentação organizada por escopo: [índice das specs](../src/backend/specs/README.md),
[Ryo e balanceamento aprovado](../src/backend/specs/characters/ryo/README.md)
e [mecânicas globais](../src/backend/specs/global/README.md).

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

`crossup-close-pressure`: cross aéreo anula o afastamento do hit e libera
pressão na aterrissagem para todo o elenco ([SPEC-060](../src/backend/specs/SPEC-060-crossup-close-pressure.md)).

`landing-dash`: reconhece direcionais no fim do salto para iniciar dash
no primeiro frame de chão ([SPEC-056](../src/backend/specs/SPEC-056-landing-dash.md)).

`directional-only-special-buffer`: buffer só de direcionais, exigindo botão
novo na saída da defesa/recuperação ([SPEC-052](../src/backend/specs/SPEC-052-directional-only-special-buffer.md)).

`low-health-super-guard-pain`: com vida até 32, defender SUPER reproduz a
animação de cheap KO com 24 frames de punição (dano na defesa pode matar) ([SPEC-051](../src/backend/specs/SPEC-051-low-health-super-guard-pain.md)).

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
| `projectile-ignores-attacks` (projétil não é dissipado ao receber golpe; só some ao acertar ou contra outro projétil) | [SPEC-038](../src/backend/specs/SPEC-038-projectile-ignores-attacks.md) |
| `blockstun-command-buffer` (comando de especial feito durante a defesa sai no 1º frame livre) | [SPEC-042](../src/backend/specs/SPEC-042-blockstun-command-buffer.md) |

| `uppercut-juggle` (uppercut anti-aéreo lança o adversário para continuar o combo) | [SPEC-043](../src/backend/specs/SPEC-043-uppercut-juggle.md) |

## Personagens

| Personagem | Patch | Spec |
|---|---|---|
| Ryo | `lp-hp-hk-target-combo` (soco fraco em pé/agachado → forte perto → trás+chute forte) | [SPEC-061](../src/backend/specs/SPEC-061-ryo-lp-hp-hk-target-combo.md) |
| Ryo | `jump-lk-pressure` (chute fraco aéreo: recuo uniforme e aterrissagem livre ao conectar) | [SPEC-059](../src/backend/specs/SPEC-059-ryo-jump-lk-pressure.md) |
| Ryo | `kohou-dash-input` (Kohou aceita baixo-frente + soco durante dash) | [SPEC-057](../src/backend/specs/SPEC-057-ryo-kohou-dash-input.md) |
| Ryo | `kohou-damage` (forte: referência 9 por hit/18 total, fraco 8) | [SPEC-054](../src/backend/specs/SPEC-054-ryo-kohou-damage.md) |
| Ryo | `kououken-damage` (dano reduzido: referência forte 16, médio 12, fraco 8) | [SPEC-053](../src/backend/specs/SPEC-053-ryo-kououken-damage.md) |
| Eiji | `crouching-heavy-kick-knockdown` (chute forte agachado mantém 2 hits e derruba no segundo) | [SPEC-050](../src/backend/specs/SPEC-050-eiji-crouching-heavy-kick-knockdown.md) |
| Micky | `crouching-heavy-kick-knockdown` (chute forte agachado derruba) | [SPEC-049](../src/backend/specs/SPEC-049-micky-crouching-heavy-kick-knockdown.md) |
| Mr. Big | `cross-diving-three-buttons` (↓↘→ + soco: fraco, médio e dois socos = forte) | [SPEC-048](../src/backend/specs/SPEC-048-mr-big-cross-diving-three-buttons.md) |
| Mr. Big | `ground-blaster-three-buttons` (chute fraco = fraco, chute forte = médio, dois chutes = forte) | [SPEC-047](../src/backend/specs/SPEC-047-mr-big-ground-blaster-three-buttons.md) |
| King | `trap-shot-three-buttons` (chute fraco = fraco, chute forte = médio, dois chutes = forte) | [SPEC-046](../src/backend/specs/SPEC-046-king-trap-shot-three-buttons.md) |
| King | `moushuukyaku-three-buttons` (chute fraco = fraco, chute forte = médio, dois chutes = forte) | [SPEC-045](../src/backend/specs/SPEC-045-king-moushuukyaku-three-buttons.md) |
| King | `knockdown-finishes` (rasteira e último hit do Moushuukyaku forte derrubam) | [SPEC-044](../src/backend/specs/SPEC-044-king-knockdown-finishes.md) |
| Ryo | `air-fireball-forward-jump` (Kou'ouken aéreo também no pulo para frente) | [SPEC-006](../src/backend/specs/SPEC-006-ryo-air-fireball-forward-jump.md) |
| Ryo | `kououken-weak-startup` (Kou'ouken fraco com startup de 11 frames) | [SPEC-009](../src/backend/specs/SPEC-009-ryo-kououken-weak-startup.md) |
| Ryo | `kohou-weak-short` (Kohou fraco: sobe pouco, 1 hit, derruba) | [SPEC-010](../src/backend/specs/SPEC-010-ryo-kohou-weak-short.md) |
| Ryo | `overhead-kick` (overhead em frente + B, chute forte longe em trás + D, D neutro novo) | [SPEC-016](../src/backend/specs/SPEC-016-ryo-overhead-kick.md) |
| Ryo | `renbuken-juggle` (Renbuken gasta 20% e recupera rápido depois do 4º hit; juggle pendente) | [SPEC-017](../src/backend/specs/SPEC-017-ryo-renbuken-juggle.md) |
| Ryo | `crouch-punch-advantage` (soco forte agachado com a vantagem do soco forte perto) | [SPEC-024](../src/backend/specs/SPEC-024-ryo-crouch-punch-advantage.md) |
| Ryo | `haoh-easy-input` (Haoh Shoukouken: frente, trás, baixo, frente + soco, diagonais aceitas, 20 frames por passo) | [SPEC-021](../src/backend/specs/SPEC-021-ryo-haoh-easy-input.md) |
| Ryo | `hien-weak-startup` (Hien Shippuukyaku fraco: arranque de 12 → 1 frame) | [SPEC-022](../src/backend/specs/SPEC-022-ryo-hien-weak-startup.md) |
| Ryo | `normal-chains` (ao conectar: baixo B → chute, soco forte perto → B+D) | [SPEC-018](../src/backend/specs/SPEC-018-ryo-crouch-kick-combo.md), [SPEC-020](../src/backend/specs/SPEC-020-ryo-normal-chains.md) |
| Ryo | `zanretsuken-19-hits` (Zanretsuken conta cada golpe: 19 hits) | [SPEC-025](../src/backend/specs/SPEC-025-ryo-zanretsuken-19-hits.md) |
| Ryo | `standing-lk-frames` (chute fraco em pé com startup, ativo e recovery do soco fraco em pé) | [SPEC-032](../src/backend/specs/SPEC-032-ryo-standing-lk-frames.md) |
| Ryo | `kououken-three-buttons` (Kou'ouken: C+D = fraco que derruba, C = médio, D = forte) | [SPEC-033](../src/backend/specs/SPEC-033-ryo-kououken-three-buttons.md) |
| Ryo | `kohou-impact-sound` (Kohou com os 2 hits: o 2º toca o som de impacto do Hien) | [SPEC-034](../src/backend/specs/SPEC-034-ryo-kohou-impact-sound.md) |
| Ryo | `kououken-impact-sound` (Kou'ouken fraco toca o som de impacto do Hien) | [SPEC-035](../src/backend/specs/SPEC-035-ryo-kououken-impact-sound.md) |
| Ryo | `close-hp-kououken-target-combo` (target combo: soco forte perto → Kou'ouken fraco sempre acerta) | [SPEC-036](../src/backend/specs/SPEC-036-ryo-close-hp-kououken-target-combo.md) |
| Ryo | `desperation-command` (DESPERATION Ryukou Ranbu com ↓↘→↘↓↙← + C) | [SPEC-037](../src/backend/specs/SPEC-037-ryo-desperation-command.md) |
| Robert | `ryuga-weak-short` (Ryuga fraco: sobe pouco, 1 hit, derruba, como o Kohou fraco do Ryo) | [SPEC-029](../src/backend/specs/SPEC-029-robert-ryuga-weak-short.md) |
| Robert | `kick-remap` (frente+B = forte perto overhead, trás+D = forte longe, D neutro = fraco com dano forte, chute forte do dash derruba) | [SPEC-030](../src/backend/specs/SPEC-030-robert-kick-remap.md) |
| Robert | `close-hp-chain` (soco forte perto → B+D ao conectar) | [SPEC-031](../src/backend/specs/SPEC-031-robert-close-hp-chain.md) |
| Robert | `ryugekiken-three-buttons` (Ryugekiken: C+D = fraco que derruba, C = médio, D = forte) | [SPEC-039](../src/backend/specs/SPEC-039-robert-takuma-fireball-three-buttons.md) |
| Robert | `desperation-command` (DESPERATION Ryukou Ranbu com ↓↘→↘↓↙← + C) | [SPEC-041](../src/backend/specs/SPEC-041-robert-desperation-command.md) |
| Takuma | `kououken-three-buttons` (Kou'ouken: C+D = fraco que derruba, C = médio, D = forte) | [SPEC-039](../src/backend/specs/SPEC-039-robert-takuma-fireball-three-buttons.md) |
| Takuma | `desperation-command` (DESPERATION Ryukou Ranbu com ↓↘→↓↘→ + C+D) | [SPEC-040](../src/backend/specs/SPEC-040-takuma-desperation-command.md) |
| Yuri | `kick-remap` (B = forte perto, frente+B = bundada, trás+D = fraco com dano forte) | [SPEC-026](../src/backend/specs/SPEC-026-yuri-kick-remap.md) |
| Yuri | `hyakuretsu-binta-10-hits` (Hyakuretsu Binta conta cada tapa: 10 hits) | [SPEC-027](../src/backend/specs/SPEC-027-multi-hit-rearm.md) |
| Yuri | `desperation-ryo-command` (DESPERATION com o comando do Ryo: ↓↘→↘↓↙← + C) | [SPEC-028](../src/backend/specs/SPEC-028-desperation-ryo-command.md) |

## Hooks compartilhados

Um patch de personagem tem uma responsabilidade só, mesmo quando o ponto do motor que ele altera também é usado por outros personagens. Esses pontos ficam em [tools/charlib.py](../tools/charlib.py) (`KICK_SELECT`, `MOVE_RECORD`, `ATTACK_WINDOW`, `ATTACK_STATE`): cada patch declara `shared_hook(<endereço>, "<bloco>")`, começa o bloco com `only(<personagem>, <endereço>)` e termina com `JmpNext(<endereço>)`. O build grava um único `jmp` no jogo e liga os blocos em sequência (ordem do manifest), terminando no código original deslocado.

## Criar um patch

1. Escolha a categoria e crie `patches/global/<id>/patch.py` ou `patches/characters/<personagem>/<id>/patch.py`, exportando `PATCH` (o `id` é igual ao nome da pasta).
2. Escreva a spec em `src/backend/specs/`.
3. Adicione o id em `manifest.json`: em `"global"`, ou em `"characters": {"<personagem>": [...]}`.
4. Rode o build.

- Ryo: `kohou-three-buttons` — SPEC-062; custo global dos fortes com dois botões — SPEC-063.

- Ryo: `hien-three-buttons-break` — dois chutes para forte, break LP+LK no segundo hit, flip vertical e relançamento (SPEC-064).

- Global: `juggle-air-hurtbox` — preserva caixa de dano enquanto o alvo sobe/cai em juggle de Kohou/Hien (SPEC-065).
