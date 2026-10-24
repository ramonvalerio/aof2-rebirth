# SPEC-016: Ryo: chute forte perto em frente + chute fraco, overhead

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/overhead-kick` (personagem)
- **Combina com:** SPEC-002 (botões), SPEC-007 (tabela de golpes)

## Comportamento desejado

| Entrada (em pé) | Golpe |
|---|---|
| Frente + B | Chute forte perto (`$00A`, anim `$0131`), de qualquer distância, **overhead**, 1 hit |
| Trás + D | Chute forte longe original (`$00B`, anim `$0132`) |
| D neutro | **Chute novo:** a animação do chute fraco com 11 frames ativos (eram 8), recuperação 6+5 (era 4+4), dano `$12` (fraco `$0C`) |
| B | Chute fraco, sem mudança |

## Histórico

- **v1:** saía com trás + B (direção invertida: com `$5E` bit 0 = 1 a frente é a **esquerda**). Também dava 2 hits perto: o 2º vinha no q4 da `$0131` (pé descendo, flags `$08`), combinando com a rasteira forte.
- **v3:** o lado vinha do `$5E` do jogador, que não acompanha a troca de lado. Passa a vir do `$5E` do **sprite**, como no dash (`$1BBF0`): bit 0 = 1 → frente é a direita.
- **v2:** direção "corrigida" (só valia de um lado), q4 da `$0131` com flags `$00`, trás + D e D neutro novo.

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| `$1DC9E` | Chute: `$1DCBC` (caso especial) → `$1DCD4` (base) → `$1DD28` (forte) → `+$10` → `jmp $1D41E` |
| `$1DCD4` | d4 = `$20` em pé (`$28`/`$2A` no ar; `$24` com C segurado), **+2 se perto** (`$41A(a5) < $20`) |
| `$1DD28` | +1 se `$271` bits 4/5 (forte) |
| d4 do chute em pé | `$30` fraco longe, `$31` forte longe, `$32` fraco perto, `$33` forte perto |
| `$270(a6)` | Direções seguradas: bit 1 baixo, 2 esquerda, 3 direita |
| `$5E` do sprite bit 0 | 1 = olhando para a direita (`$1BBF0`) |
| Golpe +8/+9 | Tipo de defesa: `$4F30` em pé (alto ou baixo), `$4710` baixo (só agachado), `$4B20` pulo (só em pé) |

| `$1D41E` | d4 → tabela de comandos do Ryo `$1EA88` → lista `$1E8C8` (8 bytes: handler + golpe). `$1D422` grava d4 em `$20(a5)` |
| `$1D75C` | Único ponto que lê o registro do golpe (`$23BA4 + id*16`) e copia os campos para o jogador |

## Implementação

- **Hook `$1DCAC`** (seleção do chute; só Ryo, d4 `$30`–`$33`, baixo solto):
  - fraco + frente → `$33`
  - forte + trás → `$31`
  - forte sem trás → `$3F` (d4 livre; a tabela de comandos ganha `$3F` → entrada 11)
- **Hook `$1D762`** (leitura do registro): com `$20(a5) = $3F` e Ryo, usa o registro próprio (cópia do `$009`, dano `$12`, anim `$17A`).
- **Animação `$17A`:** cópia da `$0130` num bloco de dados, com a lista de comandos do q0 (`$52FDC`) copiada junto.
- **Dados:** `$00A` bytes 8–9 `$4F30` → `$4B20`; `$0131` q4 flags `$08` → `$00`.

## Pendências

- O byte 9 (`$30`/`$10`/`$20`) também pode escolher a animação de reação (alta/baixa). Se a reação ficar estranha, testar `$4B30`.
- Andando para frente, B também sai como chute forte perto (é o comando).
- A flag `$08` do quadro foi deduzida (2º hit no q4 sem caixa de ataque na peça). Confirmar que o chute ficou com 1 hit.

## Critérios de aceite

- [ ] Frente + B longe e perto: chute forte perto
- [ ] Oponente agachado defendendo: leva o golpe
- [ ] Oponente em pé defendendo: defende
- [ ] Perto: 1 hit só
- [ ] Trás + D: chute forte longe; D neutro: chute novo; B parado: chute fraco normal
