# SPEC-067: DESPERATION pode ser fintado com LP+LK

## Regra global

Todos os personagens que possuem DESPERATION podem apertar soco fraco +
chute fraco durante a preparação para cancelar o golpe como ameaça.
A finta é aceita no chão, antes da primeira caixa de ataque ativa, contato
ou criação de projétil. Cancela a preparação e restitui o Spirit gasto
pelo início, voltando ao controle nativo. Não executa grab ou whiff de grab.

Depois de começar a atacar, atingir/ser defendido ou criar projétil, a
finta é desarmada e o custo normal é mantido. Não concede ataque gratuito
que já tenha saído. Condições nativas de vida/Spirit para iniciar um
DESPERATION continuam vigentes; não modifica SUPER ou especiais comuns.
Os breaks de Kohou/Hien permanecem com seus próprios marcadores/condições.

## Identificação e custo

SPECIAL_CHOSEN identifica a entrada do jogador (bit 9 de $218), personagem
1–12 e seu movimento DESPERATION: $22/$47/$6A/$8D/$B5/$D8/$100/$117/
$142/$162/$185/$1A0, conferidos contra handlers $1D460/$1D576 originais.
Geese não possui DESPERATION nessa tabela; não inventa um movimento novo.
Toda seleção limpa o estado anterior. Somente esses IDs armam a finta.
Antes do desconto em $1D7DE, salva $224 e o comando escolhido $20(a5).

O tradutor consome LP+LK durante o estado de ataque do comando armado e
registra o pedido. ATTACK_STATE confirma comando atual, personagem vivo,
chão, ausência de contato ($21B!=0) e ausência de caixas ativas nos filhos
5/6. Projetil criado (PROJ_SPAWN_X) ou contato (HIT_SOUND) desarma também.
Assim não depende de detectar dano posteriormente para cobrar Spirit.

Quando aceita, restitui exatamente a word de Spirit anterior, uma vez.
Limpa marcadores, pedido, $A6E, buffers e hits extras; para velocidades e
usa a saída nativa $1C2EA. Não altera vida ou posição. Para DESPERATION
que prepara vínculo de grab, limpa os flags do vínculo e retorna o
adversário ao estado neutro via handler nativo antes de encerrar a finta.
Esse caminho precisa de validação específica em jogo para Jack.

RAM livre: $3B7 armado; $3B8 word Spirit anterior; $3BA pedido;
$3BC word comando. Não conflita com whiff de grab $3B6 ou breaks $3B4/$3B5.
Patch isolado `global/desperation-feint`, quatro hooks compartilhados.

## Verificação

Build completo com 61 patches, assembler, bytes esperados, hook_check e
determinismo aprovados. 256 cenários simulados cobrem pedido, armado,
chão/ar, vida, comando, contato e os dois filhos de ataque. Os doze IDs
foram comparados aos handlers nativos de DESPERATION. Refund localizado
em um único caminho posterior aos filtros; não muda custos nas tabelas.

Validar no emulador todos os personagens: iniciar → LP+LK antes do ataque
→ Spirit retorna; sem finta cobra normalmente; contato/defesa/projétil
já criado não permite refund; interrupção por golpe; transição e controle
após cancelar. Conferir especialmente liberação do grab de Jack e que
Kohou/Hien/whiff de grab continuam funcionando. Não houve teste em partida.
