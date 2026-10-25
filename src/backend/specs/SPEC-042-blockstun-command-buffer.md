# SPEC-042: Leitura de direcionais durante blockstun

- Patch global: `blockstun-command-buffer`.
- Regra atual: SPEC-052, buffer apenas de direcionais, sem botão pendente.
- Status: implementado; teste de jogabilidade pendente.

O estado 15 ($1C604) originalmente não chama o leitor de comandos.
O hook chama $1DF7E para atualizar os slots direcionais $A10..$A4F,
apaga $218 antes e depois, repõe a limpeza de $253 e segue $1C60C.
Não executa especial durante a defesa nem altera sua duração.

Com `directional-only-special-buffer`, passos que exigem botão não
completam no blockstun. O jogador pode fazer as direções durante a defesa,
mas deve pressionar o botão ao poder executar o especial. Os slots
seguem a janela entre passos da SPEC-008 (12 frames com esse patch).

A versão anterior guardava o comando completo por 12 frames e podia
executá-lo sem novo botão. Essa retenção foi removida por solicitação
do usuário. Sem RAM nova. Testar junto à SPEC-052.
