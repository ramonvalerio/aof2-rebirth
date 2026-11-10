# SPEC-071: Robert — EX de dois toques + dois chutes, sequência automática de dois hits

## Regra vigente

Um único comando frente, frente + dois chutes executa o golpe completo:
primeiro a rasteira, depois o chute forte longe (animação do trás+HK).
Não exige apertar trás ou HK novamente. O primeiro contato tem reação
normal, sem derrubar/lançar; o chute forte é o segundo contato e lança
em juggle. Quando ambos alcançam o adversário, totaliza 2 HIT COMBO.
Custo único de 20% de Spirit ao iniciar o EX; segunda etapa sem novo custo.
A rasteira de HK sozinho continua derrubando como antes.

A segunda etapa também sai após defesa ou erro da primeira, como parte
do comando completo. Sem contato, espera o fim da fase ativa da rasteira
(q3 da $1B9) antes do HK. Não cria acerto artificial nem amplia caixas:
o total de hits depende dos dois ataques alcançarem o alvo. Defesa e KO
não são convertidos em juggle. O dano de cada movimento permanece nativo.

## Estágios e seleção

$3BE=1: EX iniciou, movimento $3D com registro próprio de efeito $00.
ATTACK_WINDOW inicia automaticamente o HK quando $21B=0 (contato) ou
quando q>=3 (fim da primeira fase sem contato). Consome buffers e marca
$3BE=2 antes de chamar $1D41E com comando $31.

KICK_SELECT reconhece apenas esse estágio transitório 2 para não remapear
$31 em HK neutro por causa do direcional ainda segurado para frente.
MOVE_RECORD consome 2 → 3, usando cópia do registro do HK longe $032,
animação $1B2 e custo zero. Estágio 3 só permite a reação de juggle no
segundo golpe; qualquer registro posterior limpa a marca, inclusive um
novo trás+HK normal. ATTACK_WINDOW só começa a sequência no estágio 1,
portanto não repete o segundo golpe em loop.

SPEC-043 exige Robert/$31/$3BE=3 para a reação aérea de poses de queda,
8 px/frame, gravidade -0,25 e recuo zero. Não há mais juggle no $3D.
A SPEC-065 mantém o corpo atingível no alto para outras continuações.

Os patches continuam isolados: dash-kick-juggle escolhe os registros e
cobra Spirit; dash-ex-back-hk-chain dispara a segunda etapa; kick-remap
somente reconhece a seleção automática transitória. Demais comandos,
custos e remapeamentos do Robert preservados.

## Verificação

Build completo com 65 patches, assembler e hook_check aprovados. 96
cenários simulados verificam personagem, comando, dois chutes e estágios,
incluindo limpeza da marca após o HK. Verificados primeiro registro com
efeito normal, HK nativo/custo zero, ausência de leitura de input extra,
reação condicionada ao segundo golpe e build determinístico.

Validar no emulador: comando único com 2 hits; adversário sobe só no HK;
sem segunda entrada de botão; defesa/erro; Spirit desconta uma vez;
trás+HK posterior não herda juggle; ambos os lados, centro/canto e elenco.

Prioridade de entrada SPEC-072: frente, frente + dois chutes limpa Geneikyaku pendente apenas no contexto desse EX, evitando disparo acidental do especial. A sequência e o custo permanecem iguais.
