# SPEC-058: Resposta do direcional ao andar e pular

- Escopo global: início de movimento e troca de direção.
- Alteração de ROM: extensão de `jump-instant` (SPEC-023).
- Status: análise estática e build verificados; medição ao vivo pendente.

O usuário usa controle arcade Hori/Sanwa e relata direcional reconhecido
antes de começar a andar/pular. Não foi atribuída falha ao hardware.

## Caminho de andar

$1BB84 lê $270, calcula imediatamente a velocidade em $1BBD2/$1BBF0 e
grava $20 em $1BB9A. Usa tabela por personagem/lado, sem rampa de aceleração
ou contador de espera nesse caminho. Trocar esquerda/direita seleciona a
velocidade correspondente na mesma atualização. Isso não comprova latência
zero até a imagem: polling, atualização de posição e apresentação de vídeo
são etapas separadas. Não foi alterada velocidade ou posição ao andar.

## Pausa restante do pulo

SPEC-023 já reduzia para 1 frame os 42 quadros parados das animações de
pulo. As flags $40 permaneciam, e a física $1C710 retorna quando $A69 bit 6
está ativo. Os mesmos 42 quadros passam de flags $40 para $00, retirando
essa trava remanescente. As listas D2 e todos os valores de velocidade,
gravidade, peças, duração e comandos continuam como antes deste ajuste.

Não modifica altura ou velocidade programadas do pulo, não implementa
hop/super pulo e não altera buffer, dash, cancels ou movimentos especiais.
O tempo efetivo de início/alcance deve ser conferido em jogo, já que retirar
quadros parados muda quando a física começa a agir.

## Medição controlada

`tools/lua/movement_response.lua` registra somente leituras, em
`build/lua/movement-response.csv`: direcional reconhecido ($68/$270),
posição/altura em ponto fixo, velocidades, estado, animação e flags.
Mostra frames entre mudança do direcional e primeiro deslocamento.

No FBNeo: Game > Lua Scripting > New Lua Script Window > Browse > Run.
Testar a partir do neutro, sem ataque/defesa/recovery: esquerda/direita,
inversão, cima neutro e diagonais. Repetir P1/P2 e com o mesmo personagem.
Tentativas em estado bloqueado aparecem no CSV para não confundir recovery
com atraso de input. O script não mede stick físico → polling nem atraso
do monitor. Ainda não foi executado ao vivo nesta revisão.

Não usar duração 0 no primeiro quadro: o motor pode congelar a animação.
Validar também pulo → dash, comandos com cima e trajetória após a mudança.
