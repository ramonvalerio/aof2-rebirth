# SPEC-012: Golpe normal não derruba

- **Status:** Implementada, aguardando teste em emulador
- **Patch:** `patches/global/no-knockdown-normals` (global)
- **Relacionada:** SPEC-008 (o bug do 2º acerto no cancel, já corrigido, era outra causa de queda)

## Comportamento desejado

O oponente só cai com golpe normal se estiver **tonto (dizzy)**. Especiais que derrubam por definição continuam derrubando.

| Situação | Original | Novo |
|---|---|---|
| Golpe normal no oponente no chão | não derruba | não derruba |
| Golpe normal no oponente tonto | derruba | derruba |
| Golpe normal no oponente **fora do chão** (pulo, decolagem, aterrissagem, saltinho) | **derruba** | **não derruba** (cai de pé, "air reset") |
| Especial no oponente fora do chão | derruba | derruba |

## Mapa de engenharia reversa

A reação do defensor é montada em `$21314` (`a0` = atacante) e aplicada via tabela `$212B4` → `$20604`.

| Endereço | O que é |
|---|---|
| `$1CE9C` | Contato: `$3F` bit 2 do defensor (tontura, ligado em `$1E5C8`) → `$1CEAE` liga `$3F` bit 7 (**queda**); senão, reação comum (comando `$15` → `$2059C`) |
| `$21BBE` | Altura `$18` do defensor > 0 → `$21BD4`: liga `$3F` bit 7 (**queda**) e usa o grupo aéreo (`d1 = $20` → reações `$10–$13`). Agachado (`$60` bit 5) → grupo `$10` |
| `$21C3C` / `$221D0` | Golpe forte com condições especiais (ex.: medidor de tontura `$27E ≥ $3C`) → +2 no índice: reação maior |
| `$212B4` | Índice → reação: `$00–$1F` reações de pé/agachado; `$20–$2F` → `$10–$13` (no ar) |
| `$3F` bit 7 | Marca de queda, consultada em `$1CE02` |

**Causa da queda "sem motivo":** qualquer golpe que pegasse o oponente com altura maior que zero ligava a marca de queda. Isso inclui os primeiros frames do pulo, os últimos antes de tocar o chão e saltinhos de golpes e reações.

## Implementação

Hook em `$21BD4` (`bset #7,$3F(a6)` / `moveq #$20,d1` / `rts`):

```
cmpi.w #$40,$230(a0)   ; golpe do atacante é especial?
bcs    normal          ; normal (< $40): sem marca de queda
bset   #7,$3F(a6)      ; especial: queda (original)
normal:
moveq  #$20,d1         ; reação aérea
rts
```

## Pendências / riscos

- **Reação aérea sem queda:** o oponente faz a animação de golpe no ar e aterrissa pelo fluxo normal, sem o estado de caído. Confirmar em jogo que ele cai de pé e se recupera.
- **Reações aéreas grandes** (`$12`/`$13`, escolhidas pelo +2 de `$221D0`) podem ter visual de queda mesmo sem a marca. Observar.
- **Golpes aéreos do atacante** (`$2A/$2B/$3A/$3B`) também são normais e também não derrubam mais o oponente no ar.

## Critérios de aceite

- [ ] Normal forte em oponente no início do pulo: ele não cai deitado
- [ ] Normal em oponente tonto: cai
- [ ] Kohou/Zanretsuken em oponente no ar: cai
- [ ] Anti-aéreo com normal: oponente cai de pé e pode agir

## Specs relacionadas

Exceções por personagem usam efeito explícito de queda: rasteiras de
King (SPEC-044), Micky (SPEC-049), Eiji no segundo hit (SPEC-050) e chute
forte do dash de Robert (SPEC-030). A regra global não apaga esses efeitos
contra alvo no chão. Ver [índice por personagem](README.md).
