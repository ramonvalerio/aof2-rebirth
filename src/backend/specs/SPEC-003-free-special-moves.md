# SPEC-003: Especiais sem custo de barra

- **Status:** Implementada, aguardando teste em emulador
- **Patch:** `patches/global/free-special-moves` (global)
- **Decisão relacionada:** [ADR-0003](../adr/ADR-0003-free-special-moves-via-move-table.md)
- **Combina com:** SPEC-002 (os dois patches não tocam os mesmos bytes; o build garante isso)

## Comportamento desejado

| Tipo de golpe | Custo de barra (espírito) |
|---|---|
| Especiais de comando (bola de fogo, chutes especiais etc.) | **Nenhum** |
| SUPER (precisa ter sido aprendido no bônus) | Original (`$60`) |
| DESPERATION (vida piscando, ≤ 20%) | Original (`$60`) |

A barra continua existindo e continua sendo drenada pela provocação do oponente. Requisitos que dependem do nível da barra continuam valendo; só o **desconto ao executar** um especial deixa de existir.

## Mapa de engenharia reversa

`a6` = jogador; barra de espírito = `$224(a6)` (byte).

| Endereço | O que é |
|---|---|
| `$1E848` / `$1E888` | Por personagem: lista de golpes (8 bytes: handler, id) e mapa comando → entrada |
| `$1D41E` | Despacha o comando (`$40–$47` = especiais) para o handler da entrada |
| `$23BA4` | Tabela de atributos, 16 bytes por id de golpe. Byte 4 = custo de barra |
| `$1D762` | Copia os atributos do golpe; o custo vai para `$241(a6)` |
| `$1D7DE` | Desconta `$241` de `$224` (mínimo 1). Bit 7 em `$241` = sem custo |
| `$1D5A8` | Handler do SUPER: exige o golpe aprendido (`$448`) e barra ≥ custo (`$1D5DC`) |
| `$1D460` / `$1D576` | Handlers do DESPERATION: exigem vida ≤ `$20` e barra ≥ `$60` |
| `$1D52A` / `$1D4A6` | Handlers que escolhem uma variante (`addq.l #8,a0`) pela barra ou distância |

## Implementação

O patch é só de dados: zera o byte de custo (`$23BA4 + id*16 + 4`) dos golpes cujo comando é `$40–$47` e cujo handler **não** é de SUPER/DESPERATION. As variantes sem comando próprio, escolhidas pelos handlers acima, também entram.

Cada especial que passa por `$1D53E` tem três versões consecutivas: id+0 (forte), id+1 (média) e id+2 (fraca). As três também ficam com custo 0 (lista `TIER_VARIANTS`). Isso não vale para o handler `$1D644`, que não usa níveis.

Resultado da análise (13 personagens; a entrada 0 das tabelas é uma cópia do Ryo, ver SPEC-006):
- 69 golpes base passam a custar 0 (66 diretos + 3 variantes escolhidas pelo handler)
- 109 versões média/fraca passam a custar 0
- 24 SUPER/DESPERATION mantêm o custo
- nenhum id é compartilhado entre os dois grupos

Histórico: a primeira versão zerava só a id+0. Com a SPEC-004, o botão fraco usa a id+2, e o Kou'ouken e o Hien Shippuukyaku com A/B voltaram a gastar barra. Corrigido com `TIER_VARIANTS`.

## Pendências / riscos

- **Golpe `$08E` do Jack (`$62` = 4, comando `$3F`, custo `$60`)**: fica fora da faixa `$40–$47`. Foi mantido com o custo original porque parece ser o DESPERATION desse personagem. Confirmar em jogo.
- **Geese (`$62` = 13, chefe)**: não tem SUPER/DESPERATION na faixa analisada; todos os especiais dele ficam grátis.
- **Força das bolas de fogo**: em alguns golpes o tamanho ainda depende do nível atual da barra (`$1D52A`), não do custo. Isso continua igual ao original.
- **IA**: se a CPU usa o custo para decidir quando soltar especiais, pode passar a soltar mais. Observar em jogo.

## Critérios de aceite (teste manual no FBNeo)

- [ ] Especial (ex.: bola de fogo do Ryo) não reduz a barra, nem com o botão fraco nem com o forte
- [ ] Kou'ouken (A e C) e Hien Shippuukyaku (B e D) do Ryo não reduzem a barra
- [ ] SUPER reduz a barra como no original
- [ ] DESPERATION (vida piscando) reduz a barra como no original
- [ ] Com os dois patches ativos, os controles da SPEC-002 continuam funcionando

Exceção global atual: versões fortes selecionadas com dois botões custam 20% de Spirit, conforme SPEC-063.
