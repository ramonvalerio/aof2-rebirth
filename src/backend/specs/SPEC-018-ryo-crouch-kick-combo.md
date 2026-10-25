# SPEC-018: Ryo: combo baixo B → baixo D e baixo B → baixo B → baixo D

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/normal-chains` (ver SPEC-020; hook compartilhado `$1C066`, `charlib.ATTACK_WINDOW`) + exceção do Ryo na máscara de buffer do `patches/global/special-cancel-input-buffer` (SPEC-008)

## Comportamento desejado

O chute fraco agachado do Ryo deixa vantagem para emendar:
- baixo B → baixo D (2 hits)
- baixo B → baixo B → baixo D (3 hits)

## Frame data (animações originais)

| Golpe | Comando | id | Anim | Startup | Ativos | Recuperação | Total |
|---|---|---|---|---|---|---|---|
| Baixo B | `$38` | `$00D` | `$0134` | 2 | 2 | 2 | 6 |
| Baixo D | `$39` | `$00E` | `$0135` | 4 | 2+6 | 22 | 34 |

O baixo B já é muito curto. O que atrapalhava era a **entrada**: o botão apertado durante o baixo B era descartado, e era preciso acertar o frame exato depois do fim.

## Causa e correção

O buffer de golpe (`$274`, máscara `$1C0BA + char*4`, bit = comando − `$20`) guarda o botão apertado durante o golpe e o executa no primeiro frame livre. O original marcava `$38` (baixo B) para todos; a SPEC-008 tirou os normais de chão da máscara para acabar com a "sujeira" de buffer.

**Correção:** só para o Ryo, a máscara volta a ter o `$38`: `$0C000C00` → **`$0D000C00`**. Um chute apertado durante o baixo B sai no frame seguinte ao fim dele (o filtro `$1C0A6` aceita chute depois de chute). Os outros personagens não mudam.

## v2: chain no contato

**Sintoma:** só com o buffer, o baixo D ainda não conectava depois do baixo B (o oponente sai da reação leve antes do baixo D chegar).

**Correção (`crouch-kick-chain`):** hook em `$1C066` (janela de ataque, estado 3, a cada frame). Para o Ryo, no baixo B (`$230 = $38`), **já conectado** (`$21B = 0`) e com chute apertado agora (`$270` bit 5) ou guardado (`$274` bit 5): `$274 & $3030` → `$270`, `jsr $1D808` (sai o chute agachado). Se começou, rearma as caixas dos filhos 5/6 e sai como o special cancel (`$1C0BA`). O baixo B é cancelado no próximo chute, que pega o oponente ainda na reação.

## v3: hitstun

**Causa (análise do usuário):** mesmo com o chain, sobrava um vão: o hitstun da reação **leve** do baixo B acaba antes do baixo D (startup 4, mais o tempo até o cancel) chegar, e o oponente defende.

**Correção:** golpe `$00D` (baixo B), byte 14 (tipo de reação, escolhe a animação de reação e com ela o hitstun, `$20604`): `$01` leve → **`$02` pesada**, a mesma do baixo D e do soco forte. O dano e o hitstop (byte 5) não mudam.

## v4: bug do chain (caixa não rearmada)

O bloco testava `tst.w d0` depois do `jsr $1D808`, mas o `$1D808` não devolve o resultado em d0. O cancel original (`$1C0B4`/`$1C0B8`) usa as **flags** da volta (`beq`). Com d0 lixo, o bloco às vezes ia para "não começou" e pulava o rearme: o baixo D saía com a caixa de ataque ainda marcada como "já acertou" e não acertava. O resultado era o vão. Corrigido: testa as flags e salva d0/a0/a1 como o rearme da SPEC-008.

## Conta de frames (com o chain)

| Passo | Frame |
|---|---|
| Baixo B acerta | t = 2 (3º frame) |
| Hitstop | 8 frames (byte 5 do `$00D`), os dois congelados; a janela de ataque não roda |
| Chain | 1º frame depois do hitstop: o baixo D começa |
| Baixo D acerta | 4 frames depois (startup 4) |

O baixo D precisa que o oponente continue na reação por **pelo menos 5 frames** depois do hitstop. A reação pesada (v3) dá folga para isso. Sem o chain (link puro), seriam mais 2 frames de recuperação do baixo B.

## v5: todos os personagens

O chain do baixo B passou para o patch global `normal-chains`, e vale para os 13 personagens:
- a máscara de buffer `$1C0BA` mantém o `$38` para todos (`$0D000C00`);
- o byte 14 do baixo B (`$01` → `$02`) ficou **só no Ryo**. Na v5 ele mudava para os 11 que tinham `$01`, e o baixo B do Robert ficou anormal; o efeito desse byte não está mapeado (a reação vem de `$21314`), então os outros voltaram ao original.

| Personagem | Golpe do baixo B |
|---|---|
| Ryo | `$00D` |
| Robert | `$034` |
| Eiji | `$059` |
| Jack | `$07B` |
| Lee | `$0A3` |
| King | `$0CB` |
| Micky | `$0E6` |
| John | `$10E` |
| Mr.Big | `$130` |
| Takuma | `$151` |
| Yuri | `$173` |
| Temjin | `$195` |
| Geese | `$1B3` |

## v6: desfeito para os outros personagens

A pedido, o chain do baixo B, a exceção na máscara de buffer e o byte 14 voltaram a valer **só para o Ryo**. Os outros personagens ficam com o original e serão ajustados um a um. O patch voltou para `characters/ryo/normal-chains`.

## Pendências

- **(v1)** Vantagem real: depende do hitstun da reação leve do oponente, que ainda não foi medido. Se o baixo D não conectar mesmo com o buffer, medir com `tools/lua/frame_data.lua` (coluna `advantage`) e aumentar o hitstun do baixo B (byte 14 do golpe `$00D`).
- O "baixo B + D" juntos (até 2 frames) é o chute baixo da SPEC-002 (B+D), não o baixo D. Na sequência, aperte o D separado do B.

## Critérios de aceite

- [ ] Baixo B → baixo D: 2 HIT COMBO, sem o oponente defender no meio
- [ ] Visual: a reação ao baixo B fica a pesada (mais longa)
- [ ] Baixo B → baixo B → baixo D: 3 HIT COMBO
- [ ] Outros personagens: baixo B → baixo D também emenda
