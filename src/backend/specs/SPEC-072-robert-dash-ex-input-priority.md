# SPEC-072: Robert — prioridade de dois chutes no dash sobre Geneikyaku

## Regra

Frente, frente + dois chutes deve escolher o EX automático da SPEC-071,
sem executar acidentalmente Geneikyaku ($44) por um comando pendente.
Geneikyaku com um chute, em outro contexto, e outros especiais continuam
com a leitura e prioridade anteriores. Não muda a sequência de dois
hits, o lançamento no segundo hit ou o custo de 20% do EX.

## Filtro

Hook $1D82A, antes da execução do especial pendente em $1D808. Preserva
d0/d1/a0 e exige Robert, $218 & $7F=$44 e dois chutes segurados ($68 &
$A0=$A0). Só limpa esse pendente se:

- já está no dash para frente ($40=$10); ou
- é o frame do segundo toque: detector $212 armado, $210 não expirado,
  toque anterior $213 na frente relativa ao sprite, novo aperto $69
  para a mesma frente, sem cima/baixo segurado.

Depois repõe exatamente o teste original: move.w $218,d4; se existe
especial, segue a $1D41E; se não existe, segue a leitura normal $1D832,
que mantém o fluxo de dash/chute. Não cria outro golpe, não escreve em
posições/vida/Spirit e não limpa outras entradas pendentes ou histórico.
A ordem de execução nativa não tenta o especial $44 antes de reconhecer
os dois chutes de um dash nessa situação.

## Verificação

Build completo com 66 patches, assembler, hook_check e determinismo
aprovados. 2.304 cenários simulados do bloco verificam personagem,
pendente, par/chutes isolados, estado, detector/prazo, toque anterior,
novo toque, diagonal e os dois lados. O pendente só é limpo no conflito.

Validar no emulador: repetir frente, frente + dois chutes, inclusive após
outros movimentos direcionais; deve sair EX de dois hits. Geneikyaku com
um chute e outros especiais devem continuar disponíveis. Conferir os
dois lados, início do dash e dash já em andamento. Sem teste em partida.
