# SPEC-020: Ryo: chains entre normais

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/normal-chains` (hook compartilhado `$1C066`, `charlib.ATTACK_WINDOW`; o Robert tem o próprio, SPEC-031)
- **Combina com:** SPEC-002 (B+D = chute baixo), SPEC-008 (special cancel e rearme das caixas)

## Comportamento desejado

| Golpe que conecta (hit ou defesa) | Cancela em |
|---|---|
| Baixo B (`$38`) | Chute: baixo B / baixo D (SPEC-018) |
| **Soco forte perto (`$23`)** | **B + D** (chute baixo, d4 `$34`) |

## Implementação

Um só hook em `$1C066` (janela de ataque, estado 3, a cada frame), com uma tabela de chains:

1. Ryo (`$62 = 1`) e o golpe já conectou (`$21B = 0`).
2. Botões: `$270` (agora) **ou** `$274` (guardado; o hitstop acumula `$270` com `or`, `$1BFDE`). Byte alto: bit 5 = chute, bit 6 = "C segurado" (no B+D marca chute baixo).
   - `$230 = $38`: precisa do bit 5.
   - `$230 = $23`: precisa dos bits 5 **e** 6 (B+D).
3. `$274 & $7070` → `$270`, zera `$274`, `jsr $1D808`. O chute baixo sai por `$1DCD4` (bit 6 → base `$24`, + `$10` = `$34`).
4. Se começou (flags da volta, como `$1C0B8`): rearma os filhos 5/6 e sai como o cancel (`$1C0BA`).

O special cancel (pendente `$218`) continua igual: o hook só age com os botões da tabela.

## Critérios de aceite

- [ ] Soco forte perto acerta → B+D sai na hora (2 HIT COMBO)
- [ ] Soco forte perto defendido → B+D também cancela
- [ ] Soco forte perto que não conecta não cancela
- [ ] Soco forte perto → especial (special cancel) continua funcionando
- [ ] Baixo B → baixo D continua (SPEC-018)
