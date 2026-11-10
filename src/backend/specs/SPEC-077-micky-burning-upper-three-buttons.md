# SPEC-077: Micky — Burning Upper em três versões, EX com juggle

## Comandos

Mantém o movimento QCF (baixo, diagonal para frente, frente):

- Soco fraco: fraco $0F5, nível 1, snapshot $80.
- Soco forte: médio $0F4, nível 2, snapshot $A0.
- Dois socos: forte EX $0F3, nível 3, snapshot $C0, lança em juggle.

Micky é o personagem 7, conferido na tabela NAMES do projeto. A versão
EX custa 20% de Spirit pela regra global SPEC-063 (24 de máximo 120).
Fraco/médio mantêm os custos atuais. Dano/animações dos registros nativos
não são alterados. Fraco usa $441, médio e EX usam $440, com potência e
tamanho de projétil pela variante/nível selecionados. CPU preservada.

## Seleção e conflito de dois socos

Patch isolado `characters/micky/burning-upper-three-buttons`, faixa
$F3–$F5 no SPECIAL_CHOSEN e entrada humana. Par de socos (bit 10 de $218)
tem prioridade sobre soco forte (bit 8). Só EX arma $3C1. Cada nova
seleção do Micky limpa a marca.
CMD_STEP aceita o par no terminal $1B8 somente do comando $40 de Micky,
retirando bit 6 da máscara F0 (B0). Evita executar uppercut LP+HP quando
o movimento do Burning Upper foi completado. Dois socos sem movimento
continuam uppercut normal.

## Juggle do projétil EX

Burning Upper gera um projétil. No PROJ_SPAWN_X, se Micky/$40/$3C1,
marca o bit 7 de $37 do próprio projétil (efeito nativo é $00). O impacto
copia isso para $24B do defensor. Assim não depende de Micky ainda estar
executando o especial ou de sua marca atual quando o projétil atingir.

Despacho da SPEC-043 exige dono Micky, último comando da fonte $A6A=$40
e bit 7 de $24B. Reutiliza filtros de defesa, vida e personagem. Acerto
real EX usa poses de queda $791–$79F, impulso 8, gravidade -0,25 e recuo
zero, com corpo atingível conforme SPEC-065. Origem/posições e vida não
são alteradas. Em defesa/KO, o fluxo original remove o bit 7 antes do
despacho de efeito, conservando o efeito nativo $00. Não usa efeito fora
da tabela. As rotinas anteriores ao despacho não usam esse byte.

Seleção de poses/gravidade também exige fonte Micky/$40/bit7, preservando
uppercut, John EX e Robert EX. O projétil normal não é marcado; seu
acerto e as versões fraca/média mantêm a reação anterior.

RAM livre $3C1: apenas a marca de EX antes de criar o projétil. Não
conflita com HP+HK aéreo ($3C0), John EX ($3BF) ou Robert EX ($3BE).

## Verificação

Build completo com 71 patches, assembler, hook_check e determinismo
aprovados. 75 cenários simulados verificam personagem/faixa/entrada/
força, marca EX e níveis. Nome/ID conferidos no projeto; terminal QCF com
par verificado; dano/atributos dos registros preservados exceto custos
já definidos anteriormente pelo global. Confirmar no emulador três
versões, tamanho/dano, Spirit 20%, projétil EX lançando mesmo depois da
recuperação do Micky, defesa/KO e continuação contra todos os personagens.
Sem execução na partida nesta revisão.
