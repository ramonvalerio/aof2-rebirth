# SPEC-069: Robert — frente + chute fraco com dois hits perto

## Regra

Frente + chute fraco mantém o chute alto remapeado da SPEC-030 ($33,
movimento $031, animação $1B1). A subida da perna tem acerto normal,
apenas se as caixas originais alcançarem o oponente de perto. A descida
é overhead, defendida em pé, e completa o segundo contato de perto.
De longe, quando a subida não alcança, fica somente o acerto da descida.
Sem custo novo de Spirit, alteração de dano, alcance, posição ou tempos.

## Fases originais preservadas

- q0: preparação, 3 frames; q1: subida visual, 3 frames, sem ataque.
- q2: perna subindo/alta, caixa nativa $0BEC (filho 5), 8 frames.
  Máscaras/propriedade normal $4F30.
- q3: descida $0BED, caixas nativas dos filhos 5/6, 6 frames.
  Overhead $4B20. Mantém flag $08 nativa que permite o segundo contato.
- q4–q7: recuperação/fim originais.

Não cria acerto artificial à distância nem rearma caixas continuamente.
As caixas nativas já têm a separação da subida e descida; preserva essa
estrutura e a flag do segundo hit. A janela entre contatos é a original.
Dano-base continua 12 por contato, antes das escalas do motor; total real
precisa ser medido em partida. O contador global registra contatos reais.

## Implementação

Patch isolado `characters/robert/rising-kick-overhead`. ANIM_FRAME
compartilhado em $4A84, após os comandos do novo quadro, identifica apenas
animação $1B1. Seleciona $4F30 para índice <3 e $4B20 para índice >=3 e
grava a propriedade nos filhos de ataque existentes (5/6, ignorando id 0).
Preserva d0/d1/a0. Não modifica outras animações.

O hook anterior privado do Kohou nesse endereço foi convertido ao mesmo
hook compartilhado, preservando seu rearme exclusivo $17B/quadro 3.
Original move.l a0,$50(a6) / bset 7,$5E(a6) executa uma única vez antes
dos blocos. Não altera os dados/tempos/cancelamento ou hits do Kohou.

## Verificação

Build completo com 63 patches e hook_check aprovados. 96 cenários
simulados conferem fase, exclusão de outras animações e filhos ausentes;
caixas $0BEC/$0BED e flags $18/$08 verificadas na ROM; build determinístico.

Validar no emulador: frente+LK perto dá 2 HIT COMBO; subida aceita defesa
normal; descida vence defesa agachada e aceita defesa em pé; longe apenas
a descida conforme alcance; ambos os lados, todos os defensores; garantir
rearme do Kohou EX preservado. Não houve execução na partida nesta revisão.
