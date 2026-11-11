# SPEC-087: Arremesso para o lado do direcional

- Patch global: `throw-direction`.
- Status: implementado e conferido no FBNeo (meio da tela: neutro, frente e
  trás); validação na MiSTer pendente.

O grab joga o oponente para o lado do direcional segurado no instante da
agarrada: **frente** ou **trás**. No neutro, **frente**.

## Como o jogo decide

`$1DABE` tenta o arremesso e, com o alcance confirmado, chama `$1DB10`, que
posiciona os dois antes da animação:

- **Sem troca** (padrão): o oponente é arremessado por cima do ombro e cai
  **atrás** do atacante.
- **Com troca** (`$1DB5C`): troca X e a direção ($5E bit 0) dos dois; a mesma
  animação passa a jogar o oponente para a **frente** original do atacante.

O original só trocava perto das paredes (X < $A0 ou X ≥ $260), para o oponente
não ser jogado contra elas: perto da parede esquerda, trocava se o atacante
olhasse para a direita; perto da direita, o contrário. Entre os dois limites,
não trocava nunca, e o arremesso era sempre para trás. Os casos especiais dos
personagens 7 e 4 (golpe $46), que saem antes, ficam como estavam.

## Implementação

Hook em `$1DB32` (`cmpi.w #$a0, $10(a6)`):

- X < $A0 ou X ≥ $260: segue o caminho original ($1DB3C / $1DB4A), com a
  proteção das paredes.
- Entre os dois: lê `$68 & $C` (o mesmo teste do `$1DABE`) e o bit de "trás"
  pelo lado que o atacante olha (`$5E(a4)` bit 0 = 1 → trás é `$04`; 0 → `$08`,
  como o dash em `$1BBF0`).
  - Segurando trás → `$1DB82` (sem troca): o oponente cai atrás.
  - Neutro ou frente → `$1DB5C` (troca): o oponente cai à frente.

Preserva d0 e d1. Não usa RAM nova.

## Limites

- Perto das paredes (X < $A0 ou ≥ $260) o lado é o original, escolhido para
  longe da parede, e não segue o direcional. É o mesmo que impedia o oponente de
  ser arremessado para fora da tela.
- O direcional lido é o bruto do jogador no frame do arremesso. Apertar o
  direcional no mesmo frame de A+C conta.

## Validação

FBNeo (Ryo contra a CPU, os dois colocados no meio da tela e A+C):

| Direcional | Atacante | Oponente |
|---|---|---|
| neutro | olhando para a direita | termina à direita (frente) |
| frente | olhando para a direita | termina à direita (frente) |
| trás | olhando para a direita | termina à esquerda (trás) |
| trás | olhando para a esquerda | termina à direita (trás) |

Testar na MiSTer: neutro, frente e trás com vários personagens e dos dois
lados da tela; perto das paredes, o arremesso sai para longe da parede.
