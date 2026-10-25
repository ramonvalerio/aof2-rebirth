# Specs de Ryo

**Referência do balanceamento do elenco:** [SPEC-055](../../SPEC-055-ryo-balance-reference.md).
[Auditoria de todos os danos na ROM](damage-audit.md), incluindo registros
customizados e pendências de medição dos demais especiais.

Estas alterações afetam somente este personagem. As regras do elenco ficam
no [índice global](../../global/README.md). Cada patch tem sua própria spec
e pode ser selecionado separadamente no app.

## Dano aprovado dos especiais

| Golpe | Acerto | Defesa |
|---|---|---|
| Kou’ouken forte | 16 | 4 |
| Kou’ouken médio | 12 | 2 |
| Kou’ouken fraco | 8 | 2 |
| Kohou forte | 9 por hit / 18 total | 2 por hit / 4 total |
| Kohou fraco | 8 / único hit | 2 |

Referências para as condições medidas; a escala nativa de dano permanece.
Os valores base, limites e validação estão nas SPEC-053/054 abaixo.
A implementação foi verificada no build; calibração final exige teste no
emulador com o mesmo adversário, vida e configuração.

## Alterações isoladas

| Patch | Comportamento e spec |
|---|---|
| `lp-hp-hk-target-combo` | [Target de 3 hits: LP/baixo LP → HP perto → trás+HK](../../SPEC-061-ryo-lp-hp-hk-target-combo.md) |
| `jump-lk-pressure` | [Cross com chute fraco: recuo e aterrissagem](../../SPEC-059-ryo-jump-lk-pressure.md) |
| `kohou-dash-input` | [Kohou facilitado durante o dash](../../SPEC-057-ryo-kohou-dash-input.md) |
| `air-fireball-forward-jump` | [Ryo: Kou'ouken aéreo também no pulo para frente](../../SPEC-006-ryo-air-fireball-forward-jump.md) |
| `kououken-weak-startup` | [Ryo: Kou'ouken fraco com startup de 11 frames (era 23)](../../SPEC-009-ryo-kououken-weak-startup.md) |
| `kohou-weak-short` | [Ryo: Kohou fraco curto (sobe pouco, 1 hit, derruba como o forte)](../../SPEC-010-ryo-kohou-weak-short.md) |
| `overhead-kick` | [Ryo: overhead em frente + B, chute forte em trás + D, D neutro novo](../../SPEC-016-ryo-overhead-kick.md) |
| `renbuken-juggle` | [Ryo: Renbuken gasta 20% e recupera rápido depois do 4º hit](../../SPEC-017-ryo-renbuken-juggle.md) |
| `crouch-punch-advantage` | [Ryo: soco forte agachado com a vantagem do soco forte perto](../../SPEC-024-ryo-crouch-punch-advantage.md) |
| `haoh-easy-input` | [Ryo: Haoh Shoukouken com comando fácil (frente, trás, baixo, frente + soco)](../../SPEC-021-ryo-haoh-easy-input.md) |
| `hien-weak-startup` | [Ryo: Hien Shippuukyaku fraco com startup instantâneo](../../SPEC-022-ryo-hien-weak-startup.md) |
| `normal-chains` | [Ryo: chains ao conectar: baixo B -> chute, soco forte perto -> B+D](../../SPEC-020-ryo-normal-chains.md) |
| `zanretsuken-19-hits` | [Ryo: Zanretsuken conta cada golpe: 19 hits](../../SPEC-025-ryo-zanretsuken-19-hits.md) |
| `standing-lk-frames` | [Ryo: chute fraco em pé com startup, ativo e recovery do soco fraco em pé](../../SPEC-032-ryo-standing-lk-frames.md) |
| `kououken-three-buttons` | [Ryo: Kou'ouken fraco = C+D (derruba), médio = C, forte = D](../../SPEC-033-ryo-kououken-three-buttons.md) |
| `kououken-damage` | [Ryo: Kou'ouken com dano reduzido (referência forte 16, médio 12, fraco 8)](../../SPEC-053-ryo-kououken-damage.md) |
| `kohou-damage` | [Ryo: Kohou forte 18 total (9 por hit), fraco 8 — referência](../../SPEC-054-ryo-kohou-damage.md) |
| `kohou-impact-sound` | [Ryo: Kohou com os 2 hits toca o som de impacto do Hien Shippuukyaku](../../SPEC-034-ryo-kohou-impact-sound.md) |
| `kououken-impact-sound` | [Ryo: Kou'ouken fraco (C+D) toca o som de impacto do Hien Shippuukyaku](../../SPEC-035-ryo-kououken-impact-sound.md) |
| `close-hp-kououken-target-combo` | [Ryo: target combo soco forte perto -> Kou'ouken fraco sempre acerta](../../SPEC-036-ryo-close-hp-kououken-target-combo.md) |
| `desperation-command` | [Ryo: DESPERATION Ryukou Ranbu com v v> -> v> v <v <- + C](../../SPEC-037-ryo-desperation-command.md) |

- [Kohou com três versões](../../SPEC-062-ryo-kohou-three-buttons.md)

- [Hien forte com dois chutes e break no segundo hit](../../SPEC-064-ryo-hien-strong-break.md)
