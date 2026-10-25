# SPEC-052: Buffer direcional adicional, preservando todos os cancels

- Patch: `global/directional-only-special-buffer`.
- Status: correção de regressão implementada; validação no emulador pendente.
- Combina com SPEC-008 (cancels existentes e janela direcional de 12 frames)
  e SPEC-042 (chama o leitor durante blockstun).

Adianta direcionais durante defesa e recuperação de especiais, exigindo
novo botão quando o personagem puder agir. Não muda cancels de normais,
chains, buffer de hitstop, aterrissagem, prazos ou comandos existentes.

## Implementação atual

Único hook em $1DFA0, entrada do input no leitor $1DF7E. Repõe a leitura
$270 -> d1. Somente em blockstun ($40=15) ou ataque especial em execução
($40=3 e $230 >= $40), mascara a cópia d1 com $0F: leitor acompanha apenas
direcionais e não reconhece botão antecipado. O registro $270 não muda.
Repõe `move.w -$19E(a6),d0` e volta a $1DFA8 para espelhamento nativo.

Em todos os outros estados, especialmente normal $23/$39 no estado 3,
com ou sem hitstop/contato, d0/d1 e flags de saída são iguais ao trecho
original. Nenhum outro registrador é tocado. IA mantém seu caminho nativo.

Não engancha em CMD_STEP, $1B7F2, $1BFE4 ou $1C39E. Preserva as rotinas
existentes de leitura de passos, comando pendente $218 e buffer $274.
SPEC-042 descarta $218 durante blockstun; SPEC-008 já descarta pendentes
na recuperação de especiais. Mantém a janela do tradutor para pares.

## Histórico de regressões

A primeira versão removeu buffers existentes e bloqueou botões em todo
hitstop. A segunda retirou esses bloqueios, mas o usuário ainda relatou
perda de cancels. Esta revisão remove totalmente o filtro de CMD_STEP e
atua apenas sobre a cópia do input nas duas travas solicitadas.
Não declara a regressão resolvida em jogo sem testar no emulador.

## Validação

Build completo, destinos de hooks e comparação do caminho de normais:
$23/$39, hitstop ligado/desligado, contato ligado/desligado, todos os
botões e direções devem chegar inalterados ao leitor original.

No emulador: soco forte em pé e baixo forte do Ryo → Kou'ouken;
chains, especiais de todos os personagens; direção adiantada na defesa
ou recuperação + botão novo; ausência de golpe automático ao segurar botão;
Kou'ouken repetido. Nenhum parâmetro dos golpes foi modificado.
