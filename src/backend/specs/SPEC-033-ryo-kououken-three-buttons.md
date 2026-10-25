# SPEC-033: Ryo: Kou'ouken com três versões pelo botão

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/kououken-three-buttons` (personagem; hook compartilhado `$1D676`, `charlib.SPECIAL_CHOSEN`)
- **Depende de:** SPEC-002 (botões: C = soco fraco, D = soco forte), SPEC-004 (marcas do botão em `$218`), SPEC-009 (fraco com startup 11)

## Comportamento desejado

| Comando | Versão | Golpe | Startup do projétil | Derruba |
|---|---|---|---|---|
| ↓↘→ + C + D (soco fraco + soco forte) | Fraco | `$013` (anim `$17F`) | 11 | **Sim** (para cancel e combos) |
| ↓↘→ + C (soco fraco) | Médio | `$012` (anim `$140`) | 23 | Não |
| ↓↘→ + D (soco forte) | Forte | `$011` (anim `$140`) | 23 | Não |

Antes: C = fraco (`$013`), D = forte (`$011`); o médio só saía pela CPU.

## Implementação

1. **`special-strength-by-button` (global):** na detecção do comando (`$1E102`) grava também o **bit 10** de `$218` quando `$270 & $50 = $50`, ou seja, quando o tradutor resolveu o par soco fraco + soco forte (SPEC-002). Só informação: a escolha de nível do patch global não muda (o par cai no fraco, como antes).
2. **`ryo/kououken-three-buttons`:** bloco no hook compartilhado `$1D676` (depois da escolha de versão; `$218` ainda tem as marcas). Ryo, comando do jogador (`$218` bit 9) e golpe `$011`–`$013`:
   - bit 10 → `$013`, nível 1, barra equivalente `$80` (projétil pequeno);
   - bit 8 → `$011`, nível 3, `$C0` (projétil grande);
   - senão → `$012`, nível 2, `$A0` (projétil médio).
3. **Queda:** byte 6 (efeito de acerto) do `$013`: `$00` → `$01`, o mesmo efeito da queda do Kohou forte (SPEC-010). O projétil leva o efeito do jogador (`$20A` → `$37` do projétil em `$22A3A`).

## Pendências / riscos

- **C+D também é o uppercut** (SPEC-002). Com o movimento ↓↘→ no histórico, o especial pendente (`$218`) deve ter prioridade em `$1D808`. Confirmar em jogo que não sai uppercut.
- **Queda pelo projétil:** o efeito `$01` foi validado em golpe corpo a corpo (Kohou). Confirmar que o acerto do projétil também derruba.
- **Kou'ouken aéreo:** usa outros golpes; não muda.

## Critérios de aceite

- [ ] ↓↘→ + C+D: Kou'ouken rápido (startup 11), projétil pequeno, derruba
- [ ] ↓↘→ + C: Kou'ouken médio (startup 23), projétil médio, não derruba
- [ ] ↓↘→ + D: Kou'ouken forte (startup 23), projétil grande, não derruba
- [ ] C+D sem o movimento continua sendo o uppercut
- [ ] Cancel de normal em ↓↘→ + C+D funciona (SPEC-008)
