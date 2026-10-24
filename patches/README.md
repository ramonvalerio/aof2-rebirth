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

## Personagens

| Personagem | Patch | Spec |
|---|---|---|
| Ryo | `air-fireball-forward-jump` (Kou'ouken aéreo também no pulo para frente) | [SPEC-006](../src/backend/specs/SPEC-006-ryo-air-fireball-forward-jump.md) |
| Ryo | `kououken-weak-startup` (Kou'ouken fraco com startup de 11 frames) | [SPEC-009](../src/backend/specs/SPEC-009-ryo-kououken-weak-startup.md) |
| Ryo | `kohou-weak-short` (Kohou fraco: sobe pouco, 1 hit, derruba) | [SPEC-010](../src/backend/specs/SPEC-010-ryo-kohou-weak-short.md) |
| Ryo | `overhead-kick` (overhead em frente + B, chute forte longe em trás + D, D neutro novo) | [SPEC-016](../src/backend/specs/SPEC-016-ryo-overhead-kick.md) |
| Ryo | `renbuken-juggle` (Renbuken gasta 20% e recupera rápido depois do 4º hit; juggle pendente) | [SPEC-017](../src/backend/specs/SPEC-017-ryo-renbuken-juggle.md) |
| Ryo | `normal-chains` (ao conectar: baixo B cancela em chute; soco forte perto cancela em B+D; buffer do baixo B fica no `special-cancel-input-buffer`) | [SPEC-018](../src/backend/specs/SPEC-018-ryo-crouch-kick-combo.md), [SPEC-020](../src/backend/specs/SPEC-020-ryo-normal-chains.md) |
| Ryo | `jump-punch-hitstun` (pulo com soco forte: +12 frames de hitstun no oponente, aterrissagem 20 → 7 frames) | [SPEC-019](../src/backend/specs/SPEC-019-ryo-jump-punch-hitstun.md) |

## Criar um patch

1. Escolha a categoria e crie `patches/global/<id>/patch.py` ou `patches/characters/<personagem>/<id>/patch.py`, exportando `PATCH` (o `id` é igual ao nome da pasta).
2. Escreva a spec em `src/backend/specs/`.
3. Adicione o id em `manifest.json`: em `"global"`, ou em `"characters": {"<personagem>": [...]}`.
4. Rode o build.
