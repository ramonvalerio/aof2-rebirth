# SPEC-051: Vida baixa — animação de cheap KO ao defender SUPER, com dano letal normal

- Patch global: `low-health-super-guard-pain`.
- Status: implementado; validação no emulador pendente.

Com vida positiva até 32, defender um SUPER reproduz a animação original de
cheap KO de cada personagem se sobreviver ao dano na defesa. Ao fim da
animação retorna ao jogo. Se o dano zerar a vida, ocorre cheap KO real
e derrota normal do round; não existe proteção de vida mínima.

Preserva a marca de defesa ($7C & $F = 3); não converte o contato em hit
para dano completo ou contador de combo. Dano de defesa normal continua,
inclusive letal. Não concede invulnerabilidade aos acertos sem defesa.

## Implementação

SUPER é identificado por personagem do atacante e comando copiado no
defensor ($A6A). Tabela conferida pelos handlers $1D5A8 da ROM:
Ryo $42, Robert $41, Eiji $44, Jack $43, Lee $44, King $45, Micky $47,
John $41, Mr. Big $45, Takuma $41, Yuri $41, Temjin $42.
DESPERATION e especiais comuns não entram. Sem usar apenas a faixa $40+.

A subtração e as rotinas de KO são originais. O antigo hook $1CE50, que
limitava a vida mínima a 1, foi removido.

Hook $2059C: repõe chamadas $1D378/$21AA6. Para a regra elegível, pula
as rotinas de defesa e escolhe diretamente a reação $14 em $20604.
A tabela de derrota $212E4 mapeia as reações leves defendidas de pé ou
agachadas para $14 (por exemplo, animações $164 Ryo, $3E4 King, $564 Mr. Big).
Não passa pela tabela de reações de sobreviventes $212B4, que voltaria a
selecionar dor/defesa. Usa a animação nativa e mantém HP positivo, então
o encerramento da reação segue $1C520/$1C542 e volta ao neutro.
Agora são usadas cópias curtas das animações nativas, com 24 frames totais,
em $7B1–$7BD. Conservam poses, sons e flags; durações são reduzidas
proporcionalmente e ajustadas para somar 24. As animações originais de
derrota permanecem intactas.
Para os demais casos, segue $205A4. A vida é verificada novamente ao
escolher a reação; um chip que deixa a vida em 32 também recebe a animação.

Campos existentes lidos: $6C, $7C, $64, $62 do atacante, $A6A e $60.
Sem nova RAM. Este patch não escreve HP nem altera a subtração de dano.
Animação e flags de quadro usam os campos nativos $A69 e $58 do sprite.

## Validação

Build completo/isolado, destinos dos hooks e limites 1/31/32/33.
No emulador: cada SUPER (corpo a corpo e projéteis), defesa em pé e
agachada, vários contatos, ambos jogadores/lados; confirmar animação de cheap KO e retorno ao neutro,
cheap KO real com vida insuficiente e normais/especiais/DESPERATION originais.

## Janela de punição (24 frames)

Ao entrar na cópia curta, limpa $3F bit 7 e $70 bits 7/0 para permitir
novos contatos. Enquanto $6E está em $7B1–$7BD, o hook $223F6 remove
os bits baixos da classificação de um novo contato antes de gravar $7C.
O novo golpe recebe tratamento de acerto, inclusive dano completo e KO,
em vez de outra defesa. Isso também evita reiniciar a animação especial
por um SUPER que alcance o defensor nessa janela.
O hit original que disparou a animação continua defendido.

Outro acerto troca $6E e encerra a janela; sem acerto, o final da animação
retorna ao neutro. Os 24 frames são de animação, sujeitos ao congelamento
normal do motor (hitstop), e não garantem que todo SUPER recupere a tempo
para uma punição. O personagem permanece vivo ao entrar na animação,
mas um golpe de punição pode derrotá-lo.

Sem timer ou RAM nova. Dados novos são alocados por DataBlock; as entradas
$7B1–$7BD são verificadas como vazias pelo build. Validar no emulador a
punição com defesa segurada, retorno ao controle e SUPERs de múltiplos hits.
