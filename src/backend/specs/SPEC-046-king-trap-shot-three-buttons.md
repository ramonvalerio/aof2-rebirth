# SPEC-046: King — Trap Shot com três combinações de chutes

- **Status:** Implementado; teste no emulador pendente.
- **Patch:** `characters/king/trap-shot-three-buttons`.
- **Depende de:** `global/special-strength-by-button`, com marcador de dois
  chutes no bit 11 de $218. Custo da fraca alinhado aos especiais grátis.

| Entrada | Golpe | Nível |
|---|---|---|
| Chute fraco | $0D7 | 1 |
| Chute forte | $0D6 | 2 |
| Dois chutes | $0D5 | 3 |

Trap Shot é comando $44. No hook SPECIAL_CHOSEN, filtra King e golpes
$D5–$D7 vindos do jogador; escolhe golpe, nível em $5C(a4) e barra
equivalente $23F. Usa os mesmos marcadores guardados do Moushuukyaku.
O passo final de chute já aceita o par traduzido; não altera o leitor.

A terceira variante original $D7 é uma falha (custo $B3, animação $3B2).
O patch substitui seu registro por uma versão funcional usando a sequência
$8008 e efeito $0C da média. Dano 12 (média 20, forte 32); tontura 3
(média 5, forte 8). Nível 1. Custo zero, acompanhando os especiais grátis
usados no projeto. Tempos/animação da média; não cria animação exclusiva.
Média e forte mantêm os registros originais, inclusive suas reações.

Sem RAM nova; IA mantém escolha de nível por barra, mas a antiga variante
de falha também passa a ser funcional. Nenhum outro golpe é alterado.

Validar no emulador as três entradas, dano, sequência completa, comando
guardado e demais especiais. Build deve passar com todos os patches e
com apenas força pelo botão + este patch.
