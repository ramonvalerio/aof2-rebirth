# SPEC-050: Eiji — chute forte agachado derruba

- Patch: `characters/eiji/crouching-heavy-kick-knockdown`.
- Status: implementado; teste de jogabilidade pendente.

Baixo + chute forte do Eiji mantém os dois hits de perto e derruba
somente no segundo acerto. O primeiro contato mantém a reação original.
Dano, comandos, duração e demais golpes/personagens não são alterados.

Eiji é personagem 3. Comando $39 mapeia para golpe $05A, animação $235.
O registro original, incluindo efeito $00 e hits extras $01, é preservado.
Hook compartilhado HIT_SOUND ($224BE), depois da cópia de atributos:
filtra atacante Eiji, comando $39 e hits extras $247 = 0, então define
o efeito copiado no defensor ($24B) como $15 (queda de rasteira).
O primeiro contato tem $247 = 1 e não recebe a queda. A rotina $21338
decrementa o contador depois da reação; q4 da animação $235 também
executa DE em $552D6 para encerrar os extras antes da última caixa.
Assim, se apenas a última caixa alcançar um alvo distante, ela também
derruba. Nenhuma dependência de contador visual ou animação nova.
Compatível com `no-knockdown-normals`, que não remove esse efeito contra
alvos no chão. Defesa e KO seguem as regras originais. Sem RAM nova.

Validar build completo/isolado; no emulador, acertos contra alvo em pé e
agachado, defesa, P1/P2 e ambos os lados. De perto: dois hits, queda só no
segundo. De longe: se apenas a última caixa conectar, ela deve derrubar.
