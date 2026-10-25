# SPEC-049: Micky — chute forte agachado derruba

- Patch: `characters/micky/crouching-heavy-kick-knockdown`.
- Status: implementado; teste de jogabilidade pendente.

Baixo + chute forte do Micky derruba o adversário atingido no chão.
Não altera dano, comandos, duração ou outros golpes/personagens.

Micky é personagem 7. Comando $39 mapeia para golpe $0E9, animação $42B.
O byte de efeito em $24A3A ($23BA4 + $0E9*16 + 6) muda de $00 para $15,
efeito original de rasteira. Compatível com `no-knockdown-normals`, que
não remove efeitos explícitos de queda contra alvos no chão.
Defesa e KO seguem o tratamento original. Sem hooks ou RAM nova.

Validar build completo/isolado e, no emulador, acerto contra alvo em pé e
agachado, defesa, P1/P2 e ambos os lados.
