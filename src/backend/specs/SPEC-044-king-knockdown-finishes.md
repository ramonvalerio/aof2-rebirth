# SPEC-044: King — rasteira e final do Moushuukyaku derrubam

- **Status:** Correção implementada; teste de jogabilidade pendente.
- **Patch:** `characters/king/knockdown-finishes`.

## Comportamento

- Baixo + chute forte derruba o adversário atingido no chão.
- Moushuukyaku forte: último acerto da sequência completa derruba. Os acertos
  anteriores mantêm seus efeitos; dano, comandos e tempos são preservados.

## Implementação

King é personagem 6. Rasteira: comando $39, golpe $0CA, animação $3B5.
Efeito em $23BA4 + $0CA*16 + 6: $00 → $15 (queda de rasteira).

Moushuukyaku: comando $42, golpes $0D9/$0DA/$0DB, sequências
$803F/$8040/$8041. Apenas o último item da sequência forte ($803F),
em $236B2, passa para a cópia $790 da animação final $3CA. As sequências
média e fraca ($8040/$8041, finais em $236BC/$236C4) mantêm $3CA original
e não recebem o efeito de queda deste patch.

A cópia conserva nove quadros, incluindo startup e recuperação. Em q5,
a lista original `E7 0140 DE 0717` vira `E7 0140 DE DD 15 0717`: som,
encerrar hits extras, efeito de queda, peça final. O opcode DD ($1D3D6)
grava $20A do atacante antes da colisão; $224AC copia para $24B do defensor.
Não há hook de código nem RAM nova. A animação e as listas originais
compartilhadas não são alteradas.

Regiões livres com bytes esperados zerados:

| Região | Conteúdo |
|---|---|
| $51E40 (entrada $790) | Ponteiro para nove quadros |
| $51E80–$51EA3 (entradas $7A0–$7A8) | Quadros copiados |
| $51EB0–$51EB7 (entradas $7AC/$7AD) | Lista do último acerto |

q0 aponta para a lista original $583F1; q5 aponta para $51EB0. Ambos os
deslocamentos relativos cabem em 16 bits. Não altera globalmente o efeito
$2E nem depende do contador visual de combo.

## Histórico

A primeira versão tentou identificar o último contato no hook HIT_SOUND,
usando comando, $6E = $3CA e $247 = 0. O usuário relatou que não derrubava.
A correção remove essa condição de colisão e define o efeito no quadro
final do próprio golpe.

## Validação

Build completo/isolado, compatibilidade dos patches e comparação dos
quadros e comandos com a ROM base. Validação em jogo ainda necessária:
Moushuukyaku forte completo (7 hits e queda final), interrupção antes do
final, defesa, P1/P2, ambos os lados e rasteira sem regressão.
