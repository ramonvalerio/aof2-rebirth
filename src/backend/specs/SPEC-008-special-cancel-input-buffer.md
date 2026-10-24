# SPEC-008: Special cancel global e buffer de comandos (base "estilo KOF")

- **Status:** Itens 1 e 2 implementados, aguardando teste em emulador. Item 3 (pushback) pendente
- **Patch:** `patches/global/special-cancel-input-buffer` (global)
- **Combina com:** SPEC-002 (comandos vêm do tradutor de input), SPEC-004 (força pelo botão), SPEC-007 (frame data)

## Comportamento desejado

1. **Special cancel:** um golpe normal que conecta (hit ou block) pode ser cancelado em qualquer especial, pulando o resto da animação e a recuperação.
2. **Buffer:** os comandos de especial aceitam até **12 frames** entre um direcional e o próximo. O comando também pode ser feito durante o hitstop do normal.
3. **Pushback:** reduzir em 40% o recuo horizontal quando houver special cancel.

## O que o motor original já faz (engenharia reversa)

### Janela de cancel: `$1C064` (estado de ataque, chamado de `$1C1E2`)

| Passo | Endereço | Regra |
|---|---|---|
| 1 | `$1C066`, `$1C06E` | Pulo iniciado (`$3F` bit 4) ou no ar (`$60` bit 4) → sem cancel. **Removido pelo patch** (os dois `bne` viram `nop`) |
| 2 | `$1C076` | Golpe atual já é especial (`$230 ≥ $40`) → sem cancel |
| 3 | `$1C07E` | `$21B ≠ 0` → o golpe **ainda não conectou**. `$21B = 1` no início do golpe (`$1D6B2`); zerado no contato (`$1D0C4`) |
| 4 | `$1C084` | Há especial pendente em `$218` |
| 5 | `$1C0FA` | Lista de **especiais proibidos** do personagem (`$1C126 + char*2`, bit = comando − `$40`) e de **normais não canceláveis** (`$1C160 + char*4`, bit = comando do normal − `$20`) |
| 6 | `$1C0B4` | `jsr $1D808`: executa o especial na hora. A animação e a recuperação do normal são abandonadas |

A janela abre no primeiro frame de contato e fica aberta até o fim do golpe (estado 3).

### Buffer e hitstop

- **Especial detectado** fica pendente em `$218` por **60 frames** (`$A77`, armado em `$1E106`).
- **Hitstop:** no contato, o atacante entra no subestado `$41 = 2` com o contador `$43` = byte 5 do golpe (`$10` no soco forte). O handler (`$1CA00`) **chama o leitor de comandos** (`jsr $1DF7E`) a cada frame de congelamento. Por isso o comando feito durante o hitstop já é aceito no original.
- **Prazo entre passos:** a tabela de comandos `$25D04` tem `$20` bytes por personagem, com os offsets dos comandos `$40–$4F`. Cada passo tem 6 bytes: `[máscara][valor][prazo][?][próximo (word)]`. O prazo é recarregado a cada passo e decrementado por frame (`$1E04E`); se zera, o comando é descartado.

## Implementação (itens 1 e 2: patch de dados)

| Alteração | Onde | Original | Novo |
|---|---|---|---|
| Especiais proibidos de cancelar | `$1C126`, 11 personagens | ex.: Ryo `$000F` (proibia Kou'ouken, Kou'ouken aéreo, Haoh Shoukouken e Hien) | `$0000` |
| Normais não canceláveis | `$1C160`, Jack e Temjin | `$0C000C00`, `$00000400` | `0` |
| Prazo entre passos de comando | 163 passos em `$25D04+` | 10 frames | **12 frames** |
| Cancel no ar | `$1C06C`, `$1C074` | `bne.b $1C08A` | `nop` |

Prazos já maiores (15, 18, 20, 30) e prazos `0` não mudam.

## Caixa de ataque "rearmada" no cancel (correção)

**Sintoma:** soco forte perto → Kohou fraco/forte cancelado: as caixas se sobrepõem e o golpe atravessa o oponente.

**Medição** (`frame_data.lua`, 7 repetições): a caixa de ataque do Kohou (frames 20–23 após o acerto) **sobrepõe** o corpo do oponente (`overlap = 1`) e a vida não cai. O recuo (6 px/frame, frames 17–30, vindo da animação de reação do oponente) **não é a causa**.

**Causa:**
- Colisão ataque × corpo (`$F6B48`): objetos de ataque em `$1000–$1FFF` contra objetos de corpo em `$2000–$2FFF`, com a classe `$6A & $6B`. Ao acertar, o objeto de ataque recebe `$70` bit 7 (`$F6BC6`) e deixa de ser testado (`$F6B78`).
- Cada caixa de ataque é um **objeto filho** do sprite (filhos 5 e 6). O jogo só limpa o bit 7 do **objeto do jogador** (`$1DF76` no início do golpe, `$1DEE8` no contato), nunca nos filhos.
- No cancel, o especial reaproveita o filho 5 que o normal acabou de usar, ainda marcado como "já acertou".

**Correção:** hook em `$1C0B4` (onde o cancel executa o especial, `jsr $1D808`): antes de executar, limpa `$70` bit 7 dos filhos 5 e 6 do atacante (`sprite = a5 + byte($3 do jogador) << 8`; `filho = a5 + id << 8`, id em `sprite + 2 + n`).

| Alteração | Onde | Original | Novo |
|---|---|---|---|
| Rearmar caixas no cancel | `$1C0B4` (+ bloco `rearm_and_cancel`) | `jsr $1D808(pc)` / `beq $1C0B2` | `jmp` bloco: `jsr $1D808`; **só se o especial começou** (d0 ≠ 0), limpa filhos 5/6 |

**Bug corrigido (2026-10-23):** a primeira versão limpava os filhos **antes** do `jsr $1D808`. Quando o especial pendente era recusado (`$1D808` devolve 0), o normal continuava com a caixa rearmada e acertava o oponente uma segunda vez durante a reação. Sintoma: um golpe normal forte às vezes derrubava o oponente.

**Regra original de queda por golpe normal:** no contato, `$1CE9C` testa `$3F` bit 2 do defensor. Esse bit só é ligado no estado de tontura (`$1E5C8`, junto com `$1E594`: estado `$18`, timer `$264 = $87`). Ligado → queda (`$1CEAE`); desligado → reação comum (comando `$15`). Ou seja, normal no chão só derruba oponente tonto (dizzy). Os patches não alteram essa regra.

## Buffer na aterrissagem para golpes aéreos

**Sintoma:** depois de um golpe aéreo, era difícil emendar o golpe seguinte ao cair. Era preciso acertar o frame exato após a aterrissagem.

**Mecanismo original:** durante um golpe, o que é apertado é acumulado em `$274` (`$1BFE4`, via `$1C0A2`) e liberado **no frame da aterrissagem** (`$1C39E`: `$274 & $3030` → `$270`, seguido de `jsr $1D808`). Mas só acumula para os golpes marcados na máscara `$1C0BA + char*4` (bit = comando − `$20`). O original marcava só `$20`, `$22`, `$28` e `$38`. Os golpes aéreos não entravam: o botão apertado no ar era descartado.

**Correção:** a máscara de todos os personagens ganha `$0C000C00` (comandos `$2A/$2B` socos aéreos e `$3A/$3B` chutes aéreos). Ex.: Ryo `$01000105` → `$0D000D05`.

**Limite (original):** depois do acúmulo, `$1C0A6` filtra pelo tipo do último ataque (`$235`): só soco depois de soco, ou chute depois de chute.

## Item 3: pushback (não implementado)

- O recuo ainda não foi mapeado: é preciso achar onde a velocidade horizontal de afastamento é aplicada no contato e como ela decai.
- **A premissa "Kou'ouken fraco conecta no frame 11" não vale no jogo:** pela SPEC-007 e pela medição, o projétil do Kou'ouken (fraco ou forte) só é criado no **frame 23**. Antes disso não existe caixa de ataque, então nenhuma redução de pushback faz o Kou'ouken acertar no frame 11. Para isso é preciso também reduzir o startup do Kou'ouken fraco (assunto já levantado na SPEC-007).
- **Medido:** o recuo é de 6 px/frame por ~14 frames depois do hitstop, aplicado pela animação de reação do oponente. Não impedia o Kohou de alcançar: a causa era a caixa não rearmada (seção anterior). Reavaliar o pushback só se, depois da correção, ainda faltar alcance.

## Pendências / riscos

- **Block:** o contato que abre a janela é despachado por `$24B` (tipo do golpe) em `$1CEDC`. Alguns tipos zeram `$21B` (`$1CF9C`) e outros não (`$1D022`). Precisa confirmar em jogo se os normais abrem a janela também na defesa.
- **Supers e desperations** também ficam canceláveis, porque as listas zeradas incluíam os comandos deles. Se não quiser, basta restaurar os bits de SUPER/DESPERATION nas máscaras de `$1C126`.
- **Golpes no ar** também cancelam. Todo golpe, inclusive o aéreo, usa o estado 3 (`$1D730`). Um especial aéreo (ex.: Kou'ouken aéreo) passa pelos testes de altura do próprio handler. Um especial só de chão feito no ar cai no soco aéreo do handler, que é recusado por `$240` ("um ataque por pulo", `$1D67E`/`$1DD04`). Nesse caso o cancel não acontece.
- **Equilíbrio:** com 12 frames, comandos ficam mais fáceis também por acidente (ex.: meia-lua saindo de andar + agachar).

## Critérios de aceite (teste manual no FBNeo)

- [ ] Ryo: soco forte perto → Kou'ouken cancela ao acertar
- [ ] Ryo: soco forte perto → Kou'ouken cancela também na defesa (ou registrar que não)
- [ ] Soco forte que não conecta não cancela
- [ ] Comando de Kou'ouken feito durante o hitstop do soco forte sai no cancel
- [ ] Meia-lua com até 12 frames entre direcionais é aceita
- [ ] Jack e Temjin: normais antes não canceláveis agora cancelam
- [ ] Normal aéreo que conecta cancela em Kou'ouken aéreo (Ryo)
- [ ] Soco forte perto → Kohou fraco (cancel) acerta (caixa rearmada)
- [ ] Pulo com C, apertando C de novo antes de cair: o soco forte sai no frame da aterrissagem
- [ ] Golpe normal forte não derruba (só com o oponente tonto/dizzy)

## Medição (2026-10-23, `frame_data.lua`, Ryo)

- Soco forte perto (`$0127`): startup 3, acerto no frame 4. **O cancel funcionou**: o Kou'ouken começou 20 frames após o soco, ou seja, 4 até o acerto + 16 de hitstop.
- Kou'ouken cancelado: projétil no frame 22 da animação. Em algumas repetições o P2 saiu da reação no frame 22 e o projétil acertou no 24. A janela fica **no limite (0 a 2 frames de folga)**: o combo depende da distância. Para garantir o combo, a alavanca é o startup do Kou'ouken (SPEC-007) ou o hitstun, não o pushback.
