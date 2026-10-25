# SPEC-053: Ryo — balanceamento do dano do Kou'ouken

- Patch: `characters/ryo/kououken-damage`.
- Status: implementado; calibração em jogo pendente.

Após medir forte 29/6, médio 14–16/3 e fraco 8/2 (acerto/defesa),
o usuário escolheu reduzir o forte para 16. Referência de balanceamento:
forte 16/4, médio 12/2, fraco 8/2.

Esse balanceamento foi aprovado junto ao Kohou: forte 9 por hit (18 total),
defesa 2 por hit; fraco 8/2. O Kohou é controlado separadamente pela
[SPEC-054](SPEC-054-ryo-kohou-damage.md), sem alterar outros personagens.

O jogo aplica escala nativa por vida/dificuldade e outros modificadores.
Os valores medidos correspondem aproximadamente a fator 0,8; portanto
as bases usadas são:

| Versão | Golpe | Acerto (antes → depois) | Defesa (antes → depois) |
|---|---|---|---|
| Forte | $011 | 36 → 20 | 9 → 5 |
| Médio | $012 | 20 → 15 | 5 → 3 |
| Fraco | $013 | 10 (inalterado) | 3 (inalterado) |

São alterados somente bytes 0–3 dos registros forte e médio (ambas as
colunas do motor). Mantém escala original; 16/12/8 são referência na
condição medida, não dano fixo em todos os adversários/níveis de vida.
Não altera comandos, força por botão, startup, cancel, alcance, queda,
custo ou dados do fraco. Sem hooks e sem RAM nova.

Validar build completo/isolado e comparar as três versões contra o mesmo
adversário com a mesma vida/configuração. Confirmar defesa e cancels.
