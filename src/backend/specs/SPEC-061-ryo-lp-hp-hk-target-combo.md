# SPEC-061: Ryo — LP/baixo LP → HP perto → trás + HK

- Patch isolado: `characters/ryo/lp-hp-hk-target-combo`.
- Status: implementado; validação de jogabilidade em todo o elenco pendente.

## Sequências solicitadas

1. Soco fraco em pé → soco forte perto → trás + chute forte.
2. Soco fraco agachado → soco forte perto → trás + chute forte.

São três entradas sucessivas, não botões simultâneos. No layout atual:
C → D → trás+B; ou baixo+C → D → trás+B. O segundo golpe é forçado
para a versão de perto ($23), mesmo se o primeiro causar recuo. O último
é o chute forte longe ($31) usado em trás+chute forte no remapeamento do Ryo.

## Regras de confirmação e garantia dos links

O próximo golpe só é aceito após hit real: $21B=0, adversário vivo no chão,
em reação 6/7 e último contato não defendido. Whiff, defesa e adversário
já recuperado não ativam o target. O jogador precisa pressionar cada
botão dentro do período em que a reação ainda está ativa.

O primeiro elo parte de $20/$22/$28 e exige soco forte. O segundo parte
de $23, exige estágio 1 do target e trás+chute forte. Não transforma
qualquer soco forte avulso em novo chain para chute forte.

Cada elo seleciona diretamente o comando nativo via $1D41E, consome o
buffer do ataque usado e rearma as caixas de ataque como os chains atuais.
Reinicia a reação já selecionada do defensor (sprite $42=1, $56=0 e
$A69 limpo), dando tempo para os startups de HP (3 frames) e HK (5 frames)
sem deixar o adversário defender entre os hits aceitos do target.

Somente nos golpes 2/3 marcados, a consulta de colisão da caixa ativa
dos filhos 5/6 usa alcance de confirmação: X atual do adversário ±256
e intervalo vertical completo. Isso cobre diferenças de tamanho/postura
sem mover os personagens. Mantém os filtros nativos de lado, grupo e
caixa já usada; não cria contato em frames sem caixa ativa. O alcance
normal do HP/HK avulso continua original.

Não escreve posição ou vida, não aplica teleporte/ancoragem e não muda
os registros de dano. Bases: 8+20+28=56 para ambas as entradas, antes
da escala do motor. A soma real precisa ser medida; não é dano fixo.
O target é hit-confirmado, não uma sequência garantida contra defesa.

## Hooks e RAM

- ATTACK_WINDOW compartilhado: um bloco com os dois links, na cadeia de
  cancelamentos existentes. Falhas seguem a cadeia; sucesso usa saída $1C0BA.
- MOVE_RECORD compartilhado: qualquer novo ataque do Ryo limpa o estágio;
  o elo do target define o novo estágio depois do handler retornar. Evita
  transferir confirmação de alcance para um HP/HK iniciado depois.
- $F6B78: respeita caixa já usada, preserva d0/d1/a0/a1, identifica o dono
  P1/P2 Ryo e confirma filho 5/6, estágio e comando antes de ajustar apenas
  os registradores de consulta d3–d6. Sem target, repõe o fluxo original.
- $3B2 do Ryo: byte de estágio (0 nenhum, 1 HP do target, 2 HK do target),
  na faixa livre documentada. Não conflita com cross ($3AF/$3B0), dash
  ($3AB–$3AE), Zanretsuken ($3AA), som/target anterior ($3A8/$3A9).

Compatível com cancels de Kou'ouken e chains existentes: se a entrada
não corresponde ao target ou há especial reconhecido em $218, passa para
os demais blocos do motor. Especiais reconhecidos mantêm prioridade.

## Espaço de código

O conjunto anterior já ocupava quase toda a reserva antiga. O build passa
a usar a região completa comprovadamente zerada $FDDA0–$FFEFF. Todos os
blocos continuam sujeitos a SHA, bytes esperados, limites, conflitos e
verificação do assembler. O logger de input passa a ler o destino real
do hook em vez de presumir $FE000. Ver SPEC-001.

## Validação

Verificado: build completo com 56 patches, assembler e bytes esperados;
nenhum desvio externo para o meio dos hooks; build determinístico; reserva
expandida zerada na ROM original; bloco de colisão sem escrita em memória
de posição/vida. Filtros de entrada, estágio e hit estão implementados;
a confirmação funcional em jogo permanece pendente.

Em jogo: ambas as entradas, todos os defensores em pé/agachados, P1/P2,
centro/canto, confirmação 3 HIT COMBO; HP perto obrigatório; trás+HK só
após esse HP; rejeição ao errar/defender, inputs fora da janela, novos
ataques sem alcance ampliado e cancels anteriores em Kou'ouken.
