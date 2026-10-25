# SPEC-035: Ryo: som de impacto no Kou'ouken fraco

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/kououken-impact-sound` (personagem; hook compartilhado `$224EA`, `charlib.PROJ_HIT_SOUND`)
- **Relacionadas:** SPEC-033 (Kou'ouken fraco = C+D), SPEC-034 (som de impacto no Kohou)

## Comportamento desejado

O acerto do Kou'ouken fraco (↓↘→ + C+D) toca o som de acerto "pesado" do Hien Shippuukyaku (`$0140`). Médio, forte e defesa continuam com o som original.

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| `$229C0` | Cria o projétil: `$44` = comando do dono (`$230`; Kou'ouken = `$40`), `$3C` = nível do tamanho (0/1/2 pela barra `$23F`), `$30` = som de acerto (0 = sorteado; opcode `$E8` das listas do objeto grava) |
| `$224C6`–`$224F0` | Contato de projétil (a6 = defensor, a5 + d4 = projétil): copia efeito, dano e o som `$30` → `$A5E` (`$224EA`) |
| `$21E34` | Toca `$A5E` ou sorteia (SPEC-034) |

## Implementação

Bloco depois da cópia em `$224EA`: projétil com `$44 = $40`, `$3C = 0` (fraco: barra equivalente `$80` do `kououken-three-buttons`), dono Ryo (`$64` do defensor, `$62 = 1`) e sem defesa (`$7C & $F ≠ 3`) → `$A5E(defensor) = $0140`.

## Pendências / riscos

- A versão fraca da CPU (barra baixa) também tem nível 0 e toca o som novo.

## Critérios de aceite

- [ ] Kou'ouken fraco (C+D) acertando: som do Hien
- [ ] Kou'ouken médio (C) e forte (D): som original
- [ ] Kou'ouken fraco defendido: som de defesa original
- [ ] Projéteis dos outros personagens: sem mudança
