# Auditoria dos danos do Ryo — ROM com patches ativos

Gerado por `python tools/damage_audit.py`. Fonte: `rom/aof2r.zip`.
SHA-256 da P-ROM em ordem 68k: `2545939f95c61469d78ce1d663f3676ce4608c467cd878f19d3d8d1b28e1fc91`.

**Valores base dos registros, antes das escalas do motor. Nao sao HP medidos.**
As duas colunas de cada par sao mostradas se diferentes.
Extras da tabela nao provam o total de hits: hooks, caixas e animacoes tambem contam.

| Grupo | Golpe | ID | Base acerto | Base defesa | Extras (tabela) |
|---|---|---|---:|---:|---:|
| Normal | Soco fraco em pe (perto/longe) | $000 | 8 | 0 | 0 |
| Normal | Soco forte longe | $002 | 20 | 0 | 0 |
| Normal | Soco forte perto | $007 | 20 | 0 | 0 |
| Normal | Uppercut (dois socos) | $001 | 12 | 0 | 0 |
| Normal | Soco fraco agachado | $003 | 8 | 0 | 0 |
| Normal | Soco forte agachado | $004 | 12 | 0 | 0 |
| Normal | Soco fraco aereo | $005 | 8 | 0 | 0 |
| Normal | Soco forte aereo | $006 | 12 | 0 | 0 |
| Arremesso | Arremesso: registro nativo (medir total) | $008 | 38 | 9 | 0 |
| Normal | Chute fraco em pe (perto/longe) | $009 | 12 | 0 | 0 |
| Normal | Chute forte neutro (registro proprio) | $3F hook | 18 | 0 | 0 |
| Normal | Overhead (frente + chute fraco) | $00A | 12 | 0 | 0 |
| Normal | Chute forte longe (tras + chute forte) | $00B | 28 | 0 | 0 |
| Normal | Chute baixo (soco forte + chute forte) | $00C | 12 | 0 | 0 |
| Normal | Chute fraco agachado | $00D | 10 | 0 | 0 |
| Normal | Chute forte agachado | $00E | 20 | 0 | 0 |
| Normal | Chute fraco aereo | $00F | 12 | 0 | 0 |
| Normal | Chute forte aereo | $010 | 22 | 0 | 0 |
| Kou'ouken | Terrestre forte | $011 | 20 | 5 | 0 |
| Kou'ouken | Terrestre medio | $012 | 15 | 3 | 0 |
| Kou'ouken | Terrestre fraco | $013 | 10 | 3 | 0 |
| Kou'ouken aereo P | Forte | $014 | 32 | 7 | 0 |
| Kou'ouken aereo P | Medio (sem botao dedicado) | $015 | 18 | 5 | 0 |
| Kou'ouken aereo P | Fraco | $016 | 8 | 3 | 0 |
| Kou'ouken aereo K | Forte | $017 | 32 | 7 | 0 |
| Kou'ouken aereo K | Medio (sem botao dedicado) | $018 | 18 | 5 | 0 |
| Kou'ouken aereo K | Fraco | $019 | 8 | 3 | 0 |
| SUPER | Haoh Shoukouken | $01A | 68 | 22 | 0 |
| Hien Shippuukyaku | Forte | $01B | 18 | 4 | 2 |
| Hien Shippuukyaku | Medio (sem botao dedicado) | $01C | 14 | 3 | 2 |
| Hien Shippuukyaku | Fraco | $01D | 20 | 5 | 0 |
| Zanretsuken | Forte | $01E | 2 | 1 | 18 |
| Zanretsuken | Medio (usado pelo botao fraco) | $01F | 2 | 1 | 18 |
| Falha | Zanretsuken: nao e versao fraca funcional | $020 | 8 | 0 | 0 |
| Renbuken | Sequencia (medir quatro contatos) | $021 | 12 | 0 | 3 |
| DESPERATION | Ryukou Ranbu | $022 | 100 | 25 | 0 |
| Kohou | Forte (dois hits) | $023 | 11 | 3 | 0 |
| Kohou | Fraco (um hit com SPEC-010) | $024 | 10 | 2 | 0 |
| Falha | Kohou: nao e terceira versao funcional | $025 | 9 | 3 | 0 |

## Patches considerados

- `global/controls-4button-layout`
- `global/free-special-moves`
- `global/special-strength-by-button`
- `global/spirit-charge-abc`
- `global/special-cancel-input-buffer`
- `global/dash-snappy`
- `global/no-knockdown-normals`
- `global/hit-counter`
- `global/persistent-bruises`
- `global/rush-specials-true-combo`
- `global/jump-instant`
- `global/projectile-ignores-attacks`
- `global/blockstun-command-buffer`
- `global/uppercut-juggle`
- `global/juggle-air-hurtbox`
- `global/low-health-super-guard-pain`
- `global/directional-only-special-buffer`
- `global/landing-dash`
- `global/crossup-close-pressure`
- `characters/ryo/air-fireball-forward-jump`
- `characters/ryo/kououken-weak-startup`
- `characters/ryo/kohou-weak-short`
- `characters/ryo/overhead-kick`
- `characters/ryo/renbuken-juggle`
- `characters/ryo/crouch-punch-advantage`
- `characters/ryo/haoh-easy-input`
- `characters/ryo/hien-weak-startup`
- `characters/ryo/hien-three-buttons-break`
- `characters/ryo/normal-chains`
- `characters/ryo/lp-hp-hk-target-combo`
- `characters/ryo/zanretsuken-19-hits`
- `characters/ryo/standing-lk-frames`
- `characters/ryo/jump-lk-pressure`
- `characters/ryo/kououken-three-buttons`
- `characters/ryo/kououken-damage`
- `characters/ryo/kohou-damage`
- `characters/ryo/kohou-three-buttons`
- `characters/ryo/kohou-dash-input`
- `characters/ryo/kohou-impact-sound`
- `characters/ryo/kououken-impact-sound`
- `characters/ryo/close-hp-kououken-target-combo`
- `characters/ryo/desperation-command`
- `characters/robert/ryuga-weak-short`
- `characters/robert/kick-remap`
- `characters/robert/close-hp-chain`
- `characters/robert/ryugekiken-three-buttons`
- `characters/robert/desperation-command`
- `characters/takuma/desperation-command`
- `characters/takuma/kououken-three-buttons`
- `characters/king/moushuukyaku-three-buttons`
- `characters/king/trap-shot-three-buttons`
- `characters/king/knockdown-finishes`
- `characters/mr-big/ground-blaster-three-buttons`
- `characters/mr-big/cross-diving-three-buttons`
- `characters/micky/crouching-heavy-kick-knockdown`
- `characters/eiji/crouching-heavy-kick-knockdown`
- `characters/yuri/kick-remap`
- `characters/yuri/hyakuretsu-binta-10-hits`
- `characters/yuri/desperation-ryo-command`
