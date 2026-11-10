# SPEC-068: Robert — rasteira do dash com dois chutes lança em juggle

## Comandos

- Dois toques para frente + chute forte: rasteira anterior, derruba e não
  recebe o custo EX.
- Dois toques para frente + dois chutes: variante EX da mesma rasteira,
  lança o adversário em juggle e custa 20% da capacidade máxima de Spirit.
  Com máximo 120, desconto de 24 unidades. Custo cobrado ao executar,
  inclusive no erro ou defesa; comportamento de Spirit insuficiente é o
  mesmo piso nativo já usado pelos demais EX, sem bloquear a execução.

Mesmo dano, animação $1B9, alcance e propriedades baixas da rasteira do
dash; apenas a variante EX converte o acerto em lançamento. Não modifica
chute fraco do dash nem chutes fortes parados. Na defesa não há juggle;
contra KO permanece a resolução nativa.

## Implementação

Patch isolado `characters/robert/dash-kick-juggle`, antes de `kick-remap`
no manifest. MOVE_RECORD exige Robert, comando em execução $3D e os dois
chutes segurados ($68 & $A0=$A0), seleciona registro próprio e marca $3BE.
Cada novo registro do Robert limpa a marca, evitando herança em golpes
posteriores. Chute forte sozinho segue ao registro anterior de queda.

Hook $1D7B8 repõe o carregamento original de hitstop e calcula o custo
max/5 em $241 apenas quando Robert/$3D/$3BE estão corretos. Preserva d0/d1.
Não conflita com o hook de custo do Renbuken no endereço anterior.
O snapshot/desconto nativos descontam uma vez; não usa uma dedução extra.

A reação compartilhada da SPEC-043 identifica Robert/$3D/$3BE, mantém
os filtros de vida/defesa e inicia juggle com poses de queda $791–$79F,
velocidade 8 px/frame, gravidade -0,25 e recuo horizontal zero. Não move
posições. A SPEC-065 mantém o corpo atingível no alto. A rasteira normal
continua com efeito $15 e sem essa marca, portanto derruba como antes.
Uppercut global mantém poses/velocidade anteriores; breaks manuais de
Kohou/Hien permanecem sem alteração.

## Verificação

Build completo com 62 patches, assembler e hook_check aprovados. 36
cenários simulados cobrem personagem/comando/chutes; custo proporcional
60→12, 100→20, 120→24, ordem dos hooks e build determinístico verificados.
Validar em partida: frente, frente+HK derruba; frente, frente+LK+HK lança,
contador de combo contínuo na continuação, Spirit 20%, defesa/erro/KO,
ambos os lados e canto. Não houve teste em emulador nesta revisão.

Continuação SPEC-071: após acerto, trás+HK cancela a recuperação da rasteira EX em HK longe nativo, completando dois hits. Mantém 20% somente no EX inicial.

Regra vigente SPEC-071: frente, frente + dois chutes é uma sequência automática de rasteira normal + HK. O lançamento em juggle foi transferido para o segundo golpe ($31, estágio 3), com custo único de 20% no início. HK sozinho no dash mantém a queda anterior.
