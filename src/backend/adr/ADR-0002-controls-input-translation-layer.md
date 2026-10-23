# ADR-0002: Novo layout de controles no tradutor de input ($1D87C)

- **Status:** Aceita
- **Data:** 2026-10-23
- **Spec:** [SPEC-002](../specs/SPEC-002-controls-4button-layout.md)

## Contexto

O layout novo (A/B fracos, C/D fortes, A+B arremesso, A+D uppercut, B+D chute baixo, START provocação) não pode ser feito só remapeando botões: no original, a força vem do tempo que A/B ficam segurados. "Soco forte" não corresponde a nenhum botão físico.

Pontos de intervenção avaliados:

1. **Leitura do joystick (`$9262`)**: trocaria só bits. Não expressa força nem combinações.
2. **Consumidores dos comandos (`$1D808` e afins)**: muitos pontos espalhados por estado (em pé, agachado, ar...), com alto risco de regressão.
3. **Tradutor de input (`$1D87C`)**: uma única rotina por jogador e por frame, que já produz a interface usada pelo resto do jogo (`$270` dispara, `$271` força / arremesso / provocação).

## Decisão

Fazer o hook no tradutor de input (`$1D87C`) e reescrevê-lo em um bloco novo, mantendo o mesmo formato de saída. O jogo inteiro continua consumindo `$270/$271` sem saber que o input mudou. Combinações usam uma janela curta (`PAIR_WINDOW` = 2 frames) para que apertos "quase simultâneos" de A+B / A+D / B+D funcionem sem disparar o golpe fraco antes.

## Consequências

- (+) Um único hook de 8 bytes. A rotina antiga (timers de A/B) fica sem uso.
- (+) A IA e as regras de golpe continuam intactas.
- (−) Todo golpe isolado ganha 2 frames de espera fixos (o original tinha mais).
- (+) Uppercut e chute baixo são produzidos ligando o bit "C segurado" (`$270` bit 6) que o jogo original já entende, sem tocar nas tabelas de golpes.
- (+) A provocação no START reaproveita o mesmo sinal da provocação original (`$271` bit 7).
- (−) Outras funções do C original (repetir o último ataque, walljump) ficam sem comando.
- (−) Lógicas que leem o input bruto (`$68/$69`), como especiais e o modo demo, não passam pelo tradutor. São pendências listadas na SPEC-002.

## Revisão (2026-10-23)

C+D como provocação foi substituído por START, porque as combinações A+C / B+C do original (uppercut / chute baixo) precisavam ser preservadas e foram movidas para A+D / B+D.
