# SPEC-002: Layout de controles de 4 botões

- **Status:** Implementada, aguardando teste em emulador
- **Patch:** `patches/global/controls-4button-layout` (global)
- **Decisão relacionada:** [ADR-0002](../adr/ADR-0002-controls-input-translation-layer.md)

## Comportamento desejado

| Entrada | Ação |
|---|---|
| A | Soco fraco |
| B | Chute fraco |
| C | Soco forte |
| D | Chute forte |
| A + B | Arremesso (throw), se estiver perto |
| A + D | Uppercut (no original: A + C) |
| B + D | Chute baixo (no original: B + C) |
| START | Provocação (taunt) (no original: D) |

Histórico: a primeira versão usava C + D para a provocação. Isso foi revisto depois de comparar com a tabela de golpes básicos original: A+C e B+C já eram golpes (uppercut e chute baixo), que precisavam continuar com comando.

## Comportamento original (referência)

| Entrada | Ação original |
|---|---|
| A tocado / segurado ≥ 8 frames | Soco fraco / soco forte |
| B tocado / segurado ≥ 8 frames | Chute fraco / chute forte |
| A + C / B + C | Uppercut / chute baixo |
| C | Repete o último botão de ataque (A ou B) |
| C (no ar, na parede) | Pulo de parede (walljump) |
| C + direção, perto do oponente | Arremesso |
| D | Provocação (drena o espírito do oponente) |
| Segurar A, B ou C | Recupera o espírito |

## Mapa de engenharia reversa

`a5 = $108000`. `a6` aponta para o jogador (P1 `$109080`, P2 `$109180`).

| Endereço | O que é |
|---|---|
| `$9212` | Lê `$300000`/`$340000` (joystick bruto) para `a5+$31C` / `a5+$322` |
| `$9D10` | Copia o input para o jogador: `$68` = seguro, `$69` = recém-pressionado, `$6A` = solto |
| `$1D87C` | **Tradutor de input** (ponto do hook). Gera `$270`/`$271` a partir de `$68`/`$69` |
| `$1D934` / `$1D9AE` | Timers originais de A/B (força pelo tempo segurado). Deixam de ser chamados |
| `$1D808` | Consome `$270`/`$271` em pé/agachado: socos, chutes, arremesso, provocação |
| `$1DABE` | Tentativa de arremesso (disparada por `$271` bit 6) |
| `$1DA28` | Provocação (disparada por `$271` bit 7) |
| `$1DC88` / `$1DC9E` | Seleciona soco/chute. `$271` bit 4/5 = versão forte (+1 no id do golpe) |
| `$A85A` | Replay do modo demo: injeta input bruto gravado em `$68`/`$69`/`$6A` |

Bits de botão (byte de input): `0` cima, `1` baixo, `2` esquerda, `3` direita, `4` A, `5` B, `6` C, `7` D.

Saída do tradutor:

| Campo | Bit | Significado |
|---|---|---|
| `$270` | 0–3 | Direções seguradas |
| `$270` | 4 / 5 | Dispara soco / chute (evento de 1 frame) |
| `$270` | 6 | "C segurado": soco/chute viram uppercut/chute baixo (ids `$24` / `$34`, em `$1DCD4`) |
| `$271` | 0–3 | Direções recém-pressionadas |
| `$271` | 4 / 5 | O soco / chute é forte |
| `$271` | 6 | Pedido de arremesso |
| `$271` | 7 | Pedido de provocação |

## Algoritmo novo

Variáveis do jogador reaproveitadas (antes eram os timers de A/B; zeradas no início do round em `$1B1C0`):

- `$272`: botões pendentes (bits 4–7)
- `$273`: frames restantes da janela de combinação

A cada frame:

1. `$270/$271` recebem só as direções de `$68/$69`. C e D brutos deixam de chegar à lógica de luta.
2. Se o START do controle deste jogador foi recém-pressionado, liga `$271` bit 7 (provocação). O controle vem de `-$19E(a6)` (0 = P1, 1 = P2); o START, de `a5+$32B` (bit 0 = P1, bit 2 = P2, lido de `$380000` em `$922E`).
3. Botões recém-pressionados entram em `$272`. No primeiro botão, a janela vale `PAIR_WINDOW` (2).
4. Pares, nesta ordem de prioridade (o par é consumido e a fila é limpa):
   - A+B → `$271` bit 6 (arremesso)
   - A+D → `$270` bits 4+6 (uppercut)
   - B+D → `$270` bits 5+6 (chute baixo)
5. Se a janela não acabou, espera. Quando acaba, resolve os botões isolados:
   - A → `$270` bit 4
   - C → `$270` bit 4 + `$271` bit 4
   - B → `$270` bit 5
   - D → `$270` bit 5 + `$271` bit 5
6. Por fim, chama a cauda original `$1D91C`.

Latência: um golpe isolado sai 2 frames depois do aperto. No original, o golpe fraco só saía ao soltar o botão, e o forte depois de 8 frames.

## Efeitos colaterais conhecidos e pendências

- **Uppercut / chute baixo só na versão fraca:** o original permitia a versão forte (segurando A/B com C). Agora A+D / B+D sempre saem fracos.
- **Funções do C original perdidas:** "repetir o último ataque" e o walljump (C no ar) não têm mais comando. Recuperar espírito segurando C é tratado fora deste tradutor e precisa ser verificado.
- **C + D:** não é mais combinação. Sai como botões isolados, e o soco forte tem prioridade.
- **START em jogo:** no AES ou em modo de 2 jogadores, o START pode ter outros usos (pausa, entrada de desafiante). Verificar se há conflito.
- **Golpes especiais:** a detecção de comandos (`$27xxx–$29xxx`) lê o input bruto. Especiais com A/B continuam iguais; ainda não foi verificado se C/D contam como soco/chute nos especiais.
- **Ataques no ar e outros estados:** precisam ser verificados em jogo (`$1C49A` e `$1C5F6` leem `$69` bruto).
- **A+B longe do oponente:** não faz nada, como o C original longe do oponente.
- **CPU:** a IA não passa por `$68` na luta (a confirmar em jogo).
- **Modo demo:** reproduz input bruto gravado no layout antigo e pode ficar diferente.

## Critérios de aceite (teste manual no FBNeo)

- [ ] A / B tocados geram soco / chute fraco, em pé e agachado
- [ ] C / D geram soco / chute forte
- [ ] A+B perto do oponente arremessa
- [ ] A+D faz o uppercut e B+D faz o chute baixo
- [ ] START provoca e drena o espírito do oponente, para o P1 e para o P2
- [ ] Especiais com A/B continuam saindo
- [ ] CPU luta normalmente
