# SPEC-029: Robert: Ryuga fraco igual ao Kohou fraco do Ryo

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/robert/ryuga-weak-short` (personagem)
- **Referência:** SPEC-010 (Kohou fraco do Ryo), SPEC-004 (força pelo botão)

## Comportamento desejado

O Ryuga fraco (→ ↓ ↘ + A) tem as mesmas propriedades do Kohou fraco do Ryo: startup rápido, sobe pouco, **1 hit**, **derruba** e recupera rápido. O Ryuga forte não muda.

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Comando | `$47` (→ ↓ ↘ + soco) → handler `$1D4DC` → `$048` forte, `$049` fraco |
| Golpes | `$048`: dano `$10`, efeito `$0B`; `$049`: dano `$0A`, efeito `$0B`; os dois com anim `$1C5` |
| `$1C5` | q0–q2 hit no chão (peças `$1144`–`$1146`, t = 0–9); q3 lançamento (lista `$5476B`); q4/q5 no ar (`$0C1E`/`$0C1F`, 10 + 10); q6 segura até o chão; q7–q9 aterrissagem (lista `$54780`) |
| Lançamento `$5476B` | `c7 003E` (som), `eb`, `de`, `dd 01` (efeito → queda), `d2` [alinhamento] vy `$000CC000`, gravidade `$FF70`, vx `$0180`, atrito 0; peça `$0C1D` (só caixa de ataque = 2º hit) |

O Ryuga tem a mesma estrutura do Kohou do Ryo (`$145`): o 2º hit vem da peça do lançamento.

## Implementação (patch de dados)

| Alteração | Onde | Original | Novo |
|---|---|---|---|
| Animação nova `$2AA` (cópia da `$1C5`) | quadros em `$50BC0` (entradas vazias `$2F0`–`$2F9`); entrada `$50000 + $2AA × 4` | `0` | 10 quadros |
| Lançamento copiado | `$50BE9` (ímpar, como o original) | — | vy **`$00070000`** (7 px/frame, ~43 px), peça **`$0C1E`** (só corpo) |
| Efeito do Ryuga fraco | `$049` byte 6 | `$0B` | **`$01`** (derruba) |
| Animação do Ryuga fraco | `$049` bytes 10–11 | `$01C5` | **`$02AA`** |

## Critérios de aceite

- [ ] → ↓ ↘ + A: sobe pouco, 1 hit, o oponente cai
- [ ] Recuperação curta (aterrissa logo)
- [ ] → ↓ ↘ + C: Ryuga forte igual ao original
