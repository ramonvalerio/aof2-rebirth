# SPEC-054: Ryo — balanceamento do dano do Kohou

- Patch isolado: `characters/ryo/kohou-damage`.
- Status: implementado; calibração em jogo pendente.
- Combina com SPEC-010 (fraco curto, 1 hit) e SPEC-034 (som do forte).

## Balanceamento aprovado

| Versão | Acerto | Defesa |
|---|---|---|
| Forte | 9 por hit, 18 com os dois hits | 2 por hit, 4 total |
| Fraco | 8, único hit | 2 |

São referências para a mesma condição de teste do usuário, que mediu
13 por hit no forte antes do ajuste. O motor mantém escala por vida,
dificuldade e modificadores. Os números não são dano fixo universal.

## Dados alterados somente no Ryo

Forte: golpe $023, bytes 0–3 de $23BA4 + $023*16:
`10 10 04 04` → `0B 0B 03 03`. Base de acerto 16 → 11 e defesa 4 → 3.
Com escala medida de aproximadamente 0,8, a referência passa de 13 para
9 por hit e aproximadamente 2 na defesa. O motor controla o arredondamento.

Fraco: $024 mantém `0A 0A 02 02`, com referência 8/2. SPEC-010 já remove
o segundo hit e reduz a altura. Não altera a variante de falha $025.

Não muda startup, recuperação, trajetória, invulnerabilidade, queda,
comandos, custos ou quantidade de hits. Sem hooks e sem RAM nova.
Os golpes de Robert, Takuma e outros personagens não são alterados.

## Validação

Build completo e isolado; conferir que somente os quatro bytes do forte
mudaram, que o fraco ficou intacto e que o build combina com SPEC-010/034.
Em jogo: comparar forte 1º/2º hit, soma dos dois, defesa e fraco, sempre
com o mesmo adversário, vida e configuração. Conferir cancels e combos.

Atualização: soco forte agora seleciona a nova versão média; os dois socos selecionam a forte, conforme [SPEC-062](SPEC-062-ryo-kohou-three-buttons.md).

Atualização SPEC-062: o forte agora tem terceiro contato; base 11 por hit preservada, referência total passa a 27 quando os três acertam.

Regra atual (SPEC-062): retirada a tentativa de terceiro contato. Forte volta aos 2 contatos originais, referência total 18, com break LP+LK no segundo e juggle para continuação.

Regra vigente: SPEC-062 define forte completo com três contatos (referência 27) ou break opcional após o segundo (referência 18 antes da continuação). Dano por contato preservado.
