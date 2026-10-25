# SPEC-065: Kohou/Hien — adversário atingível no alto durante juggle

Patch global isolado `juggle-air-hurtbox`. Escopo: reação aérea de juggle
com animações $791–$79F, compartilhadas pelos breaks de Kohou/Hien.
Não muda os golpes, trajetórias, duração da queda ou custo de Spirit.

## Caixa de dano

Hook $43FC, atualização nativa de limites de colisão, antes da consulta
entre caixas. Identifica o dono P1/P2 e exige vida positiva, altura >0,
reação 6/7 e animação de juggle. Só atua no primeiro filho de corpo do
sprite (offset $3); nunca rearma caixas de ataque (filhos 5/6).

A cada atualização de caixa, remove as marcas de invulnerabilidade de
queda no jogador/sprite e mantém o filho de corpo ativo ($70=1). Se a
pose já tem geometria de corpo, preserva suas dimensões. Se ela a deixou
vazia, fornece uma geometria de corpo de 32x48 ($72=$F8101818): o motor
calcula os limites usando a posição aérea nativa do objeto. Mantém $6B
(grupos de alvo) e exige grupo não zero, preservando os filtros nativos.

A normalização ocorre antes da colisão por frame, não a cada consulta:
a marca de contato usada pelo motor durante o frame continua funcionando.
Sem juggle, sem altura, derrotado ou em outro estado, reproduz o teste
original de caixa vazia e a continuação $4408. Outro hit troca a animação;
a aterrissagem elimina a condição de altura, cessando a intervenção.

Não escreve X/Y, altura, vida, velocidade, gravidade ou grupos de alvo.
Não aproxima lutadores nem muda alcance dos golpes. Ainda é necessário
o ataque alcançar fisicamente a caixa aérea para conectar.

## Verificação

Build completo com 59 patches e hook_check aprovados. 240 cenários
simulados dos filtros cobrem P1/P2, limites de animação, vida, altura,
estado e identificação do filho. Verificada ausência de escrita em
posição/vida/velocidade/grupos e build determinístico.

Confirmar na partida: atingir no alto após Hien break e Kohou break,
continuação do contador de combo, golpes físicos/projéteis conforme seu
alcance, terceiro hit do Kohou sem cancel e retorno normal após pouso.
Não houve execução no emulador nesta revisão.
