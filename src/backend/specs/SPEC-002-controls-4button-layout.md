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
| A + C | Arremesso (throw), se estiver perto. Sem direção: em pé (neutro) ou agachado |
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

`a5 = $108000`. `a6` aponta para o jogador: P1 `$109280`, P2 `$109380`. O objeto de input fica em `$109080`/`$109180` e é copiado para o jogador em `$1A976`.

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

## Arremesso sem direção

O original só arremessava segurando ← ou →: `$1DABE` testa o input bruto (`$68 & $0C`) e sai em `$1DAD4` (`beq.b $1DAF2`) sem direção. O lado do arremesso é decidido pela **posição** dos jogadores (`$1DB10`), não pela direção, e o alcance pelo `$A68` bit 0. O patch troca esse `beq` por `nop`: A+C perto arremessa no neutro.

**Agachado:** o alcance (`$A68` bit 0) é ligado em `$21F7E`, mas só se `$60 & $F0` do arremessador for zero (`$21F66`). O bit 5 de `$60` é "agachado", então agachado nunca ficava no alcance. A máscara passa para `$D0` (byte `$21F69`), e o arremesso sai agachado também. Os bits 4 (no ar), 6 e 7 continuam bloqueando.

## Algoritmo novo

Variáveis do jogador reaproveitadas (antes eram os timers de A/B; zeradas no início do round em `$1B1C0`):

- `$272`: botões pendentes (bits 4–7)
- `$273`: frames restantes da janela de combinação

A cada frame:

1. `$270/$271` recebem só as direções de `$68/$69`. C e D brutos deixam de chegar à lógica de luta.
2. Se o START do controle deste jogador foi recém-pressionado, liga `$271` bit 7 (provocação). O controle vem de `-$19E(a6)` (0 = P1, 1 = P2); o START, de `a5+$32B` (bit 0 = P1, bit 2 = P2, lido de `$380000` em `$922E`).
3. Botões recém-pressionados entram em `$272`. No primeiro botão, a janela vale `PAIR_WINDOW` (2).
4. Pares, nesta ordem de prioridade (o par é consumido e a fila é limpa):
   - A+C → `$271` bit 6 (arremesso)
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
- **A+C longe do oponente:** não faz nada, como o C original longe do oponente.
- **CPU:** a IA não passa por `$68` na luta (a confirmar em jogo).
- **Modo demo:** reproduz input bruto gravado no layout antigo e pode ficar diferente.

## Critérios de aceite (teste manual no FBNeo)

- [ ] A / B tocados geram soco / chute fraco, em pé e agachado
- [ ] C / D geram soco / chute forte
- [ ] A+C perto do oponente arremessa
- [ ] A+D faz o uppercut e B+D faz o chute baixo
- [ ] START provoca e drena o espírito do oponente, para o P1 e para o P2
- [ ] Especiais com A/B continuam saindo
- [ ] CPU luta normalmente

## Revisão (2026-10-23): arremesso em A+C

O arremesso passou de A+B para A+C. A+B deixa de ser combinação e sai como botões isolados (o soco tem prioridade sobre o chute). Note que A+C era o uppercut no jogo original; aqui o uppercut continua em A+D.

## Correção (2026-10-23): soco fraco "fantasma" ao usar o C

**Sintoma:** apertando só o C, às vezes saía soco fraco, sobretudo ao segurar o C do pulo até a aterrissagem.

**Causa:** a função original "C repete o último ataque" (`$1D896`, chamada no neutro por `$1D842`). Ela conta quanto tempo o C (bruto, `$68` bit 6) fica segurado e, ao soltar, faz `or.b $235,$270` (`$1D8E2`): injeta o tipo do último ataque (`$235`, ex.: `$10` = soco) **sem** a marca de forte em `$271`. O resultado é um soco fraco.

**Correção:** `$1D8E2` (`or.b d1,$270(a6)`) vira 2× `nop`. O C continua sendo só o soco forte, pelo tradutor.
