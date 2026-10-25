# SPEC-023: Pulo instantâneo, sem andar antes

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/global/jump-instant` (global)
- **Correção relacionada:** `characters/ryo/haoh-easy-input` (SPEC-021)

## Comportamento desejado

Para todos os personagens:
- o pulo (neutro, frente e trás) sai **na hora** em que o comando é dado;
- na diagonal para frente, o personagem **não anda** antes de pular.

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| `$1D862` | Em `$1D808`: borda de cima (`$271` bit 0) → pulo `$1DA66`, **só se `$A0E = 0`** |
| `$1DA66` | Escolhe o pulo: `d4 = $B` neutro, `9` frente, `$D` trás (pelo lado, `$5E` do sprite) |
| `$1E3B6` | Handler do pulo: estado 4, `$60` bit 4 (no ar); a animação é o id da lista (Ryo `$109` frente, `$10A` neutro, `$10B` trás) |
| q0 das animações de pulo | Quadro de comando com flag `$40` (parado), 2–3 frames. A lista toca o som e dá a velocidade (`$D2`, ex.: Ryo frente vy `$D0000`, gravidade `$FF70`, vx `$0480`); o personagem só decola depois dele |
| `$20(a6)` | Velocidade de andar (gravada em `$1BB9A`), não era zerada no pulo |
| `$A0E` | Bits de "comando em andamento com cima segurado" (`$1E0A6`); enquanto houver um, o pulo não sai |

## Implementação

- **Dados:** os 42 quadros `$40` das animações de pulo dos 13 personagens passam a durar **1 frame** (eram 2–3; Geese já tinha 1 no q0, e os q1/q2 dele também são `$40`).
- **Hook `$1E3B6`:** `clr.l $20(a6)` antes do original: o pulo começa sem a velocidade de andar.
- **Ryo (SPEC-021):** o 1º passo do Haoh fácil aceitava frente-cima (máscara `08`). Com isso, frente-cima ligava `$A0E` e bloqueava o pulo para frente do Ryo. Agora a máscara é `09`/`08`: frente sem cima.

## Pendências

**Atualização SPEC-058:** além de manter duração 1, os 42 quadros antes
marcados $40 agora usam flags $00, para a física não esperar o fim do
quadro parado. Ver [análise e medição de resposta](SPEC-058-movement-response.md).

- **Diagonal com borda tardia:** o pulo só sai na borda de cima. Se o controle registra a frente um frame antes da cima, há 1 frame de andar (limite do hardware/controle).
- **Outros comandos com cima:** um especial cujo 1º passo aceite cima (máscara sem o bit 0) também bloqueia o pulo por `$A0E`. Se algum personagem ainda andar antes de pular, procurar esse comando.

## Critérios de aceite

- [ ] Cima: pula na hora (todos)
- [ ] Frente-cima parado: pula para frente na hora, sem andar
- [ ] Andando para frente → frente-cima: pula sem deslizar antes
- [ ] Trás-cima idem
- [ ] Ryo: frente-cima pula (não fica preso pelo Haoh)
