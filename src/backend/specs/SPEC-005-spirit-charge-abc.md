# SPEC-005: Spirit com soco fraco + chute fraco + chute forte

Regra global: segurar LP+LK+HK juntos, sem direção, carrega Spirit.
No layout físico atual: C+A+B. O soco forte (D físico) não participa.
A carga começa no primeiro frame e termina ao soltar um dos botões,
pressionar direção ou adicionar HP. Taxa e máximo nativos preservados.
O nome interno do patch continua `spirit-charge-abc`.

## Condição correta após remapear botões

Funções em $68: LP=$10, LK=$20, HP=$40, HK=$80. Condição exata $68=$B0.
Antes se exigia $70, que era LP+LK+HP depois do remapeamento e não a
combinação física pretendida. Corrigida a rotina $1B9FE; limiar $1BA33
continua 1, sem novos temporizadores ou custo.

No tradutor de controles, a combinação B0 consome os eventos antes da
fila de ataque: limpa $270/$271 e pendentes $272 e segue a cauda nativa.
Assim não tenta grab, whiff de grab ou break LP+LK quando os três botões
são pressionados para carregar Spirit, inclusive perto do adversário.
LP+LK sozinho mantém grab e os cancelamentos específicos anteriores.
Demais combinações e golpes seguem a tradução anterior.

Build completo e hook_check aprovados. 256 valores de $68 testados no
bloco de condição: só B0 aceita a carga. Prioridade no tradutor conferida.
Validar em partida carga com os três botões, perto/longe, soltura/direção,
comando antigo desativado e LP+LK sozinho preservado. Sem teste em emulador.
