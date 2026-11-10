# SPEC-066: Grab errado mostra tentativa e deixa recuperação vulnerável

## Comportamento

Soco fraco + chute fraco continua tentando o grab nativo. Se ele conectar,
o arremesso funciona como antes. Se falhar no chão, o personagem mostra
uma tentativa vazia usando poses do seu próprio grab e fica exposto por
18 frames de animação (6 de tentativa +12 de recuperação, mais o término
nativo). Nesse intervalo não anda, defende, pula ou cancela em ataque.
Pode receber golpes normalmente. Depois volta ao controle nativo.

Regra para personagens jogáveis 1–13, incluindo Geese: neutro, caminhada
ou agachado; personagem vivo e no chão. Não inicia tentativa vazia em
ataque, defesa, reação, dash ou no ar. Não altera o grab aéreo existente.
A entrada LP+LK consumida como break de Kohou/Hien não vira tentativa de
grab. A mudança vale para o elenco, sem alterar a distância dos grabs.

## Implementação

Hook $1D836 substitui teste de botão/chamada de grab e respeita o destino
nativo $1D842. Wrapper chama $1DABE sem salvar registradores na pilha:
o sucesso nativo descarta esse retorno em $1DB06 e segue direto ao golpe;
somente a falha volta para iniciar o whiff. Sem botão ou fora do escopo,
retorna à leitura nativa $1D842. Não chama rotinas de troca de posição,
animação do defensor ou dano no caminho da tentativa vazia.

$3B6: 1 arma o registro de tentativa, 2 animação/recuperação em andamento.
MOVE_RECORD consome 1 e seleciona um registro exclusivo com dano/custo/
efeito/hits extras zero e máscara de ataque zero (grupo $0030). Uma
animação por personagem, com poses estáticas originais do grab; não
executa scripts nativos que puxam o adversário ou aplicam dano. Qualquer
novo registro normal limpa a marca 2. ATTACK_WINDOW bloqueia cancelamento
e limpa $218/$274 durante a recuperação, sem mudar a regra de outros
ataques ou os marcadores $3B4/$3B5 dos breaks.

A SPEC-065 também reconhece $3B6=2 em ataque com vida positiva para manter
a caixa de corpo vulnerável, inclusive nas poses de grab que a omitem.
Não altera X/Y, grupos de alvo, dano de terceiros ou caixas de ataque.
Ao terminar ou ser interrompido, a própria troca de estado/registro cessa
a condição. O estado nativo de ataque permite ser punido.

## Verificação

Build com 60 patches, assembler e hook_check aprovados (nenhum salto para
o meio do hook). 360 cenários simulados verificam botão, chão/ar, vida,
personagem e estado; 13 registros/animações verificam dano zero, máscara
de ataque zero, poses sem scripts e 18 frames de tentativa/recuperação.
Build determinístico. Validação no emulador pendente: grab perto acerta;
fora do alcance ou contra alvo não agarrável mostra tentativa punível;
LP+LK durante os breaks preserva Kohou/Hien; teste ambos os lados,
agachado, interrupção por golpe e todos os personagens jogáveis.
