# SPEC-074: John — Overdrive Kick EX lança em juggle no último contato

## Correção de identidade

John é o ID 8, conforme tabela NAMES do visualizador de hitboxes. ID 12
é Temjin. A versão anterior usava dados do Temjin; removidos esse filtro
e o alias de entrada que havia sido criado para o outro personagem.
A identificação correta do John também corrige SPEC-075.

## Regra e seleção

QCB + dois chutes, comando $46 nativo do John (lista $200, final $218
F0/20). Não precisa de alias de socos. SPECIAL_CHOSEN exige JOHN=8,
entrada humana, variantes $121–$123 e bit 11 (par de chutes). Seleciona
$121, nível 3 e $23F=$C0 para custo global 20%; marca $3BF. Toda nova
seleção do John limpa essa marca. Outras versões/comandos preservados.

Sequência forte $803C: $4C9, $4CA, $4CA, $4BC. No último contato, anim
$4BC e quadro de sprite >=6 (comando DE e peça $029F), o despacho da
SPEC-043 converte o efeito em juggle. Contatos anteriores seguem sua
reação original. Exige vida positiva, ausência de defesa e os demais
filtros nativos. A consulta de sprite preserva a1 antes de seguir o
original ou a rotina de lançamento.

Juggle usa poses de queda $791–$79F, velocidade 8, gravidade -0,25 e
recuo zero, com corpo atingível (SPEC-065). Não escreve posição ou vida.
Dano, caixas e dados da sequência nativa não mudam. Defesa/KO seguem
resolução original. Robert EX e uppercut mantêm seus filtros próprios.

## Verificação

Build completo e hooks aprovados. Conferida a identidade pela tabela
do projeto e a seleção/estrutura do Overdrive correto na ROM. Verificados
os registros/ponteiros originais de John e Temjin sem alterações.
Confirmar no emulador QCB+dois chutes e Spirit 20%, contatos anteriores
normais e último em juggle, continuação, defesa e versões anteriores.
