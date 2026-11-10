# SPEC-070: Robert — chute fraco neutro com startup/recuperação do soco fraco

Startup passa de 4 para 2 frames; recuperação de 8 para 1 frame, iguais
aos do LP neutro $027/animação $1A0. Os 8 frames ativos, dano 12,
hitstop 12, alcance e ausência de custo de Spirit são preservados.
Tempo total passa de 20 para 11 frames. Não iguala os frames ativos ao
LP (4), pois o pedido se limita ao startup e recovery.

Patch isolado `characters/robert/standing-lk-frames`, antes de kick-remap.
MOVE_RECORD aceita somente Robert e comandos $30/$32; usa registro próprio
idêntico ao $030 com animação exclusiva $22C. A cópia tem 5 quadros:
1 frame de comando/preparação $0C22, 1 de $0C23, 8 ativos $0C24,
1 de recuperação $0C23, fim $0C22. Sons originais copiados juntos.

A animação $1B0 original não é alterada: o chute forte neutro customizado
$3F que a compartilha conserva seus tempos. Frente+LK é remapeado para
$33 antes da leitura do registro, portanto mantém overhead por fase e
os dois contatos próximos da SPEC-069. Chutes do dash/EX preservados.

Build completo com 64 patches e hook_check aprovados. ROM verificada:
startup 2, ativo 8, recovery 1; $1B0 e $1B1 originais preservadas;
comando de sons e caixa ativa nativa mantidos; build determinístico.
Teste na partida pendente: LK perto/longe, controles e continuidade,
frente+LK overhead e HK neutro inalterados.
