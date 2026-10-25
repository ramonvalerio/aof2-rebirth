# SPEC-048: Mr. Big — Cross Diving abreviado e três versões

- Patch: `characters/mr-big/cross-diving-three-buttons`.
- Depende de `global/special-strength-by-button` e layout de quatro botões.
- Status: implementado; teste de jogabilidade pendente.

Comando abreviado: ↓↘→ + soco. Mantém a família de socos da imagem de
referência; Ground Blaster usa o mesmo movimento com chutes.

| Entrada | Golpe | Nível |
|---|---|---|
| Soco fraco | $141 | 1 |
| Soco forte | $140 | 2 |
| Dois socos | $13F | 3 |

Em SPECIAL_CHOSEN, filtra Mr. Big (9), entrada humana e golpes $13F–$141.
Prioridade: bit 10 de $218 (par de socos), bit 8 (forte), senão fraco.
Atualiza golpe, nível e barra equivalente. IA mantém força por barra.

O slot $43 na tabela $25D04 + 8*$20 + 3*2 muda de $0618 (←↙↓↘→)
para $01A0 (↓↘→). Não altera as listas compartilhadas de direcionais.
No hook CMD_STEP, somente para Mr. Big e passo final $1B8, retira o bit
6 da máscara para aceitar dois socos ($50) além de soco isolado ($10).
Sem movimento o uppercut continua resolvido pelo tradutor normal.

Não modifica dano, animações, custos ou efeitos. Três versões funcionais
originais. Não altera o Ground Blaster nem os outros personagens.
Como a lista de comandos é compartilhada com a IA, esta também passa a
usar o movimento abreviado; a força da IA continua determinada pela barra.

Validar: três entradas, ambos os lados, P1/P2, Ground Blaster com chutes,
uppercut sem movimento e demais especiais. Build e hooks devem passar.
