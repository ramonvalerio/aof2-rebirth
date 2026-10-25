# SPEC-045: King — Moushuukyaku com três combinações de chutes

- **Status:** Implementado; teste no emulador pendente.
- **Patch:** `characters/king/moushuukyaku-three-buttons`.
- **Depende de:** `global/special-strength-by-button` para capturar os botões.

| Botões após o movimento | Golpe | Nível |
|---|---|---|
| Chute fraco (A físico no layout atual) | $0DB, fraco | 1 |
| Chute forte (B físico) | $0DA, médio | 2 |
| Ambos os chutes (A+B físicos) | $0D9, forte | 3 |

O detector global guarda os dois chutes no bit 11 de $218, usando os
bits 5 e 7 do input funcional $68. O marcador acompanha o comando pendente
mesmo depois de soltar os botões. O tradutor atual resolve o par de chutes
como chute, portanto o passo final original `f0 20` do Moushuukyaku continua
válido; não precisa relaxar a máscara do leitor de comandos.

No hook compartilhado SPECIAL_CHOSEN ($1D676), filtra King, comando de
jogador (bit 9) e golpes $D9–$DB; escolhe golpe em $10(a5), nível em
$5C(a4) e barra equivalente em $23F. Prioridade: par (bit 11), botão forte
(bit 8), fraco. IA segue a barra original. Não altera outros especiais.

O patch `knockdown-finishes` continua redirecionando só o final de $D9:
com ambos ativos, somente dois chutes produzem o Moushuukyaku que derruba.
Média e fraca mantêm as sequências originais. Nenhum campo novo de RAM.

Validar em jogo: três entradas, comando guardado durante hitstop, força
independente da barra, sete hits e queda apenas na forte, demais especiais.
