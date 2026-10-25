# SPEC-059: Ryo — pressão após cross com chute fraco aéreo

- Patch isolado: `characters/ryo/jump-lk-pressure`.
- Status: implementado; calibração de distância/combo no emulador pendente.
- Golpe: comando $3A, registro $00F, animação $136.

## Problemas e comportamento

O usuário relata recuo maior em Robert do que Takuma e impossibilidade
de soco fraco ao aterrissar depois de um cross. A animação $136 segura
o quadro aéreo e tem sequência de aterrissagem com durações 13+3+3;
o personagem pode tocar o chão e continuar em estado de ataque.
As reações dos defensores também usam dados próprios de movimento,
além de corpos/caixas e separação física diferentes.

Quando o chute fraco aéreo do Ryo conecta, ao tocar o chão encerra a
recuperação de aterrissagem e passa pela saída nativa do ataque. Uma nova
entrada de soco pode sair no chão sem aguardar a sequência de poses.
Para acerto contra alvo no chão, normaliza o componente horizontal de
movimento da reação em 1 px por aplicação, mantendo o sinal pelo lado.
Não teleporta os personagens nem iguala suas caixas de corpo.

## Implementação

Hook $1C234: é alcançado com $60 bit 4 limpo depois da física. Filtra
Ryo, comando $3A, contato $21B=0 e vida positiva; limpa $240 e a trava de
ataques $60 bit 7 e segue $1C2EA, saída nativa para neutro/agachado e
processamento de entrada. Fora disso, repõe `$58(sprite)=1` e segue $1C23A.
Acerto e defesa conectados liberam a aterrissagem; whiff não muda.

Hook $1CBB0: conserva leitura/conversão do componente de movimento do
filho da animação, preserva d1/a1 e filtra último contato $A6A=$3A,
atacante Ryo, defensor no chão em reação 6/7 e contato não defendido.
Substitui d0 por $10000 (16.16), segue $1CBB8 e mantém espelhamento,
congelamento do hitstop e aplicação de movimento originais. Não altera
as animações compartilhadas de Robert/Takuma ou de qualquer defensor.
Defesa, ar e outros golpes mantêm recuo nativo.

O ganho é de consistência do componente de recuo. A distância final ainda
pode variar por largura/caixas, ponto do contato, canto e colisão entre
corpos. Não promete distância final idêntica nem combo após cross alto:
o hitstun precisa durar até o ataque no chão. Não adiciona hitstun para
forçar combos e não modifica dano, controles, altura/velocidade do salto,
buffer ou outros ataques/personagens. Sem RAM nova.

## Validação

Atualização global: [SPEC-060](SPEC-060-crossup-close-pressure.md) controla
crosses para todo o elenco. Os hooks $1C234/$1CBB0 deste patch agora usam
LANDING_ATTACK/REACTION_PUSH compartilhados; o original é deslocado pelo
build. O recuo zero do global é aplicado no ponto comum $1CBB8, depois
do ajuste específico de 1 px, portanto a regra global prevalece no cross.

Build completo/isolado e hooks. Em jogo: cross fundo em Robert/Takuma e
todo elenco, ambos os lados/P1/P2, centro/canto; soco fraco novo no contato
com o chão e contador de combo. Conferir que ataques altos não ganham
combo garantido, whiff mantém recuperação, defesa mantém recuo e que
outros aéreos/cancels/dash de aterrissagem continuam funcionando.
