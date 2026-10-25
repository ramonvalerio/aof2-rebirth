# SPEC-062: Ryo — Kohou com três versões e break no segundo hit

## Versões atuais

- Soco fraco: $024, animação curta $17E, 1 contato; referência 8/2 defesa.
- Soco forte: $025 funcional com animação $145; 2 contatos, base 9/hit,
  chip base 3/hit (referência aproximada 7/2 por contato).
- Dois socos: $023, animação original $145; 3 contatos, base 11/hit,
  chip base 3/hit (referência 9/2 por contato, 27 total). Custa 20% de
  Spirit conforme SPEC-063.

O forte completo tem três contatos. No segundo, LP+LK permite cancelar
opcionalmente o terceiro e preparar o Hien forte. A tentativa antiga de
rearmar no estado do jogador foi substituída por rearme no avanço real
da animação do sprite.

## Comando do Kohou

SPECIAL_CHOSEN escolhe $10, $5C, $23F com os bits de $218. O comando $47
permite par no passo final real $268 (máscara F0 → B0). Nas etapas
$258/$260, diagonal final com soco ($1A) ou par ($5A) conclui se a frente
já foi registrada. Sem movimento completo, dois socos mantêm o uppercut.
A seleção da CPU continua original. O médio $025 deixa de ser falha.

## Juggle e break

$3B4 inicia em 1 somente no forte humano; fraco/médio iniciam em zero.
HIT_SOUND conta contatos reais: 1 → 2 após primeiro, 2 → 3 após segundo.
Contato defendido zera a marca e não habilita break. Outro personagem ou
outro comando não participa.

A reação global existente de juggle (SPEC-043) aceita também Ryo $47 com
$3B4=3, inclusive na altura zero do segundo contato. Mantém filtros de
vida, defesa e personagem. Usa animações exclusivas $791–$79F com as três poses de queda nativas de
cada defensor (reação original $22), velocidade vertical 8 px/frame,
gravidade -0,5 e recuo horizontal zero. O uppercut global mantém suas
poses $781–$78F e velocidade 6, sem alterações. O oponente fica
atingível no ar; a aterrissagem já limpa as travas da SPEC-043.
O segundo contato forte abre juggle mesmo sem o jogador usar o break.

Durante o hitstop do segundo contato (estado $41=2), apertar soco fraco
+ chute fraco (C+A físicos) grava a solicitação $3B5. O tradutor consome
o par nessa janela, antes de criar arremesso. Fora dela, o arremesso segue
original. Não existe buffer antecipado desse botão durante o primeiro hit.
A solicitação específica dura até o fim do hitstop do segundo hit.

No próximo ATTACK_STATE, com comando $47 e estágio 3, o break consome
$3B4/$3B5 e limpa $274/$218. Ryo passa à animação $17C, composta apenas
por poses sem ataque da recuperação curta do Kohou, velocidade inicial
7 px/frame e gravidade -1. A altura é zerada no início dessa subida curta,
sem alterar X. A física aérea nativa $1C208 executa a subida/aterrissagem.
Não devolve controle instantaneamente no chão: o jogador executa o Hien
forte ao aterrissar; o adversário fica em juggle para essa continuação.
Não há Hien automático nem custo extra pelo break; Kohou continua 20%.

Sem break: animação exclusiva forte $17B em $51DBC, 12 quadros. O primeiro
ataque de chão dura 5 frames; um quadro próprio de 1 frame repete a pose
$1143. Ao carregar esse quadro (índice 3), o hook $4A84 rearma exatamente
uma vez os filhos 5/6. O lançamento original continua no quadro 4, gerando
o terceiro contato. No terceiro, a marca passa a 4 e o efeito $01 derruba
normalmente, sem reativar juggle ou break. Distância original preservada.
A animação curta $17C fica em $51C94, 6 quadros, sem peças de ataque.
Fraco $024/anim $17E e médio $025/anim $145 não usam o rearme adicional.

RAM livre: $3B4 = estágio de contatos; $3B5 = pedido de break. Não conflitam
com $3B2 do target e $3B3 do custo.

## Verificação

Build completo (57 patches), assembler, bytes esperados e destinos dos
hooks aprovados. 64 cenários simulados dos blocos de contato e solicitação
confirmam exclusão de defesa, primeiro hit, outros golpes/personagens e
fora do hitstop. Testes em emulador pendentes: segundo hit → LP+LK → Hien
forte; confirmar contador contínuo, ambos os lados, centro/canto, dano,
Spirit, retorno ao controle e arremesso original fora da janela.

Verificação desta revisão: build completo e hooks aprovados, 48 cenários
simulados do filtro de rearme, 45 poses de queda comparadas às originais,
atributos de animação fraco/médio/forte e build determinístico.
Emulador ainda pendente: três hits sem break; segundo hit → break com
subida curta → Hien forte em combo; adversário sobe reto com poses de
queda; confirmar KO, guarda, centro/canto e retorno ao controle.

## Subida conjunta até o terceiro contato

A trajetória vigente do defensor no segundo contato é 12 px/frame com
gravidade -0,5. O Ryo sem break usa lançamento exclusivo em $51DED:
velocidade 12,75, gravidade -0,5625, velocidade X zero e peça $0AE9 sem
ataque. A animação aguarda 22 frames de subida sem caixa de ataque antes
de ativar $0AE8 por 4 frames para o terceiro contato, perto do ápice.
O restante da recuperação continua original. Não há correção de posições
nem teleporte; ambos sobem por física. A distância horizontal inicial é
preservada, portanto é necessário o golpe alcançar o adversário.

No modelo de integração com gravidade antes da posição, após 22 frames
Ryo está a 138,19 px e defensor a 137,5 px: trajetórias próximas na região
alta da tela. Altura exata em pixels na tela e acerto real do terceiro
precisam ser conferidos no emulador. A câmera e o hitstop podem alterar
quando essa pose aparece, sem alterar o objetivo da subida conjunta.

O break no segundo permanece opcional, com subida curta do Ryo. As poses
de queda do defensor e o custo de 20% permanecem. Fraco e médio mantêm
animações anteriores. Build, hooks, atributos e sequência de caixas
verificados; modelo de trajetórias aprovado. Jogo em execução pendente.

## Recuperação completa no cancel e queda lenta

Regra vigente do break: Ryo preserva a altura atual (sem zerar Y), sobe
com velocidade 7 e gravidade -0,5625, iguais à trajetória curta do fraco.
A animação exclusiva $17C mostra $0AE9, $0AEC, $0AEA por 6 frames cada
(18 ao todo), depois $0AEB até a aterrissagem nativa. Nenhuma dessas
poses tem ataque. Assim a volta aparece antes de tocar o chão, sem
encerrar a animação antecipadamente.

Somente ao consumir o break, o defensor recebe velocidade 8 e gravidade
-0,25 via seu registro de jogador. A próxima física nativa sincroniza
$28 do sprite. Mantém as poses de queda, a subida reta e a reação de
juggle até acertar outro golpe ou aterrissar. Sem break, permanece a
trajetória alta 12/-0,5 que acompanha o terceiro hit do Kohou completo.
O custo de Spirit e as versões fraca/média não mudam.

Verificado: build, hooks, poses e durações na ROM, ausência de escrita
em altura no break, trajeto sem cancel preservado. Modelo da física
(incluindo a pausa do sprite para |v|<3) estima Ryo 24 frames de voo e
defensor 64 a partir da altura zero, abrindo cerca de 40 frames após o
pouso do Ryo. Trata-se de estimativa, não de medição em partida.
Confirmar no emulador animação completa e encaixe real do Hien forte.

Os blocos de contagem e pedido agora também atendem o Hien forte $43. O caminho do Kohou $47 permanece próprio; a animação e relançamento específicos do Hien seguem SPEC-064. A guarda de vida do adversário impede o consumo do break contra KO.

Caixa de dano durante o juggle alto: SPEC-065 mantém o corpo atingível sem mudar trajetória ou alcance dos golpes.

Regra atual do Hien (SPEC-064): retorno vertical automático, sem LP+LK, inclusive ao defender/errar. O compartilhamento do bloco não altera o cancelamento manual LP+LK do Kohou. Relançamento Hien só em acerto com alvo vivo.

Restauração solicitada: Hien voltou ao cancel manual LP+LK no segundo acerto, como o Kohou. Removidos retorno e juggle automáticos; regra vigente em SPEC-064.
