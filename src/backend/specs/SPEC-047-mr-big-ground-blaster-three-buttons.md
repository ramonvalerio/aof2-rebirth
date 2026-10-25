# SPEC-047: Mr. Big — Ground Blaster com três versões

- Patch: `characters/mr-big/ground-blaster-three-buttons`.
- Depende de `global/special-strength-by-button` para os marcadores do comando.
- Status: implementado; teste de jogabilidade pendente.

Mantém ↓↘→ + chute: chute fraco = fraco ($137, nível 1), chute forte =
médio ($136, nível 2), dois chutes = forte ($135, nível 3).

Hook compartilhado SPECIAL_CHOSEN ($1D676), personagem 9 e golpes $135–$137.
Filtra comando humano (bit 9 de $218); bit 11 tem prioridade para par de
chutes, depois bit 8 para forte, senão fraco. Atualiza $10(a5), $5C(a4)
e $23F. IA preserva a escolha por barra. As três variantes são funcionais
na ROM original; não muda dano, animações, efeitos ou custos.

Verificar build e, no emulador, três entradas, níveis de barra distintos,
P1/P2 e ausência de mudanças nos outros especiais.
