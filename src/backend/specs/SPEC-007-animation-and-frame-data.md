# SPEC-007: Formato de animação e frame data

- **Status:** Referência (engenharia reversa). Startup, ativos e recuperação decodificados da ROM; hit/block stun a medir
- **Ferramentas:** `tools/anim_dump.py` (estático, lê `rom/aof2.zip`) e `tools/lua/frame_data.lua` (medição em jogo)

## 1. Estrutura de animação

### Do golpe até a animação

| Passo | Onde | O quê |
|---|---|---|
| Atributos do golpe | `$23BA4 + id*16` | `+0` dano, `+4` custo, `+5` hitstop (provável), `+10` id da animação, `+14` tipo de reação (`1` leve, `2` pesado, `$10` projétil) |
| Início | `$1D73A` | id da animação → `$6E(jogador)`; `$42(sprite) = 1` (reinicia) |
| Animador | `$22644` (por objeto de sprite) | se `$42`: `$4918` inicia a animação `$6E`; a cada frame `$4A00` avança |

### Tabela e quadros

- `$0000FC` aponta para a **tabela de animações** (`$050000`), com 1 long por id: o byte alto é o **nº de quadros** e os 24 bits baixos são o **endereço da lista de quadros**.
- **Cada quadro tem 4 bytes:** `[duração][flags][offset (word)]`.

| Campo | Significado |
|---|---|
| duração, bits 0–6 | **Frames de exibição do quadro** (vai para `$56`, decrementado por `$58` = `$100`/frame). `0` congela o quadro |
| duração, bit 7 | 1 = quadro simples: o offset é o índice da peça de sprite. 0 = lista de comandos em `quadro + 2 + offset`, terminada em `$80` (opcodes ≥ `$80` despachados pela tabela em `$200`), por exemplo para criar o projétil |
| flags | Copiadas para `$A69` do jogador (`$226C6`). `$10`/`$18` = golpe em execução, `$08` = fim da execução, `$00` = recuperação, bit 7 (`$80`) = **quadro final**: o estado devolve o controle |

### Peças de sprite e caixas

- Peças: `$0CE000 + índice*4`. Na word alta, `(hi & $70) >> 4` é o tipo e os 4 bits baixos fazem parte do ponteiro de dados (`+ $0D4004`).
- **Tipo 3:** os bits 15..8 dizem quais dos **8 filhos** do sprite (ids nos bytes `$2–$9` do objeto) recebem caixa. A caixa vai para `$72` do filho: X, largura, Y e altura assinados, em meias-unidades. `$43FC` converte em retângulo `$76–$7C` e liga `$70` bit 0.
- **Filhos 2, 3 e 4** têm caixa em todos os quadros, inclusive na animação parada: são o **corpo** (hurtbox). **Filhos 5 e 6** só aparecem nos quadros de golpe: são a **caixa de ataque**.

### Como ler as fases

- **Startup:** soma das durações dos quadros antes do primeiro quadro com filho 5/6.
- **Ativos:** soma das durações dos quadros com filho 5/6.
- **Recuperação:** do fim do último quadro ativo até o quadro com flag `$80`.
- **Total:** início do quadro `$80`.
- **Projéteis:** o "startup" é o quadro com o comando que cria o projétil (`$22A5C`). Os ativos são do objeto do projétil.

**Validação:** o quadro de criação do Kou'ouken começa em t = 23, igual ao medido em jogo (23 frames, `frame_data.lua`).

## 2. Frame data do Ryo (`$62` = 1)

Contagem em frames de 60 Hz. "Startup" = frames antes da caixa de ataque; o primeiro frame ativo é o startup + 1.

| Golpe | Comando | id | Anim | Startup | Ativos | Recuperação | Total | Dano | Byte 5 | Reação |
|---|---|---|---|---|---|---|---|---|---|---|
| Soco forte longe | `$21` | `$002` | `$0122` | 4 | 6 | 16 | 26 | `$14` | `$10` | pesada |
| Soco forte perto | `$23` | `$007` | `$0127` | 3 | 9 | 6 | 18 | `$14` | `$10` | pesada |
| Chute forte longe | `$31` | `$00B` | `$0132` | 5 | 8 | 20 | 33 | `$1C` | `$14` | pesada |
| Chute forte perto | `$33` | `$00A` | `$0131` | 6 | 8 | 20 | 34 | `$0C` | `$10` | leve |
| Kou'ouken fraco | QCF + A | `$013` | `$0140` | 23 (projétil criado) | — (projétil) | 38 após a criação | 61 | `$0A` | `$00` | projétil |
| Kou'ouken forte | QCF + C | `$011` | `$0140` | 23 (projétil criado) | — (projétil) | 38 após a criação | 61 | `$24` | `$00` | projétil |

Observações:
- O Kou'ouken fraco e o forte usam **a mesma animação**: mesmo startup e mesma recuperação. Mudam dano e tamanho do projétil (SPEC-004).
- O chute forte perto tem dano menor (`$0C`) e reação leve, segundo a tabela original.

## 3. Hit stun / block stun (pendente)

- **Byte 5** do golpe → `$209` → `$249` do defensor (`$224A0`) → `$43` com `$41 = 2` (`$1D0C8`). É um contador regressivo, provavelmente o **hitstop** (congelamento no impacto).
- O **hitstun/blockstun** é a duração da **animação de reação** do defensor, escolhida pelo tipo de reação (`+14`) via `$20604` (tabela por personagem em `$20662`). O mapeamento tipo → animação ainda não foi rastreado.
- **Medição:** `tools/lua/frame_data.lua` registra `p2_free` (quando a reação do P2 chega ao quadro final) e `advantage = p2_free - total`, separados para hit e para block.
