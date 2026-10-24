# SPEC-013: Contador de combo na tela

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/global/hit-counter` (global)

## Comportamento desejado

Como no Super Street Fighter II Turbo, a partir do 2º acerto seguido aparece "**2 HIT COMBO**", "**3 HIT COMBO**"... do lado de quem faz o combo, com a **fonte do HUD do próprio jogo** (a do "BEAT BY 0"). O texto some cerca de 1,5 s (90 frames) depois do último acerto.

## Regras do combo

| Situação | Efeito |
|---|---|
| Vida do oponente cai e não foi defesa | +1 (ou começa em 1, sem combo ativo) |
| Defesa (`$7C & $F == 3`, o mesmo teste de `$21872`) | não conta |
| Reação do oponente chega ao quadro final (`$A69` bit 7) | combo acaba |
| Contador ≥ 2 | mostra "`NN` HIT COMBO" (máx. 99) |

## Mapa de engenharia reversa: texto na tela

| Endereço | O que é |
|---|---|
| `$41BE` | "Imprime o texto nº d0": pega o ponteiro em `($C0).w` (`$FC000`) e enfileira |
| `-$5F8(a5)` / `-$5F4(a5)` | Fila de tarefas do VBlank (em `$107B00`) e trava |
| `$0FD8` | Executor da fila (VBlank): ponteiro positivo = registro de texto |
| `$1034` | Interpretador: pares `[parâmetro][comando]`, comandos `< $19` |

Comandos usados:

| Cmd | Efeito |
|---|---|
| 0 | fim |
| 2 | `REG_VRAMMOD` = parâmetro (`$20` = próxima coluna) |
| 3 | `REG_VRAMADDR` = word (`$7000 + coluna*$20 + linha`) |
| 8 | string em 2 linhas: topo = tile `(param << 8) \| char`; base = linha seguinte, tile + `$100`; termina em `$FF` |
| `$10` | número BCD da RAM em 2 linhas: param `$C1` = 2 dígitos, zero à esquerda em branco; words: endereço, offset em `a5`, base do tile |

Fonte do HUD: parâmetro `$2D` = paleta 2, tiles `$D00 + c` (topo) e `$E00 + c` (base). É o registro do "BEAT BY" (`$FC57A`: `20 02 | C1 10 7182 14DA 2D00 | 00 03 7082 | 2D 08 "BEAT BY " FF`).

## Implementação

- **Hook** em `$1B6A0` (atualização do jogador, todo frame, os dois jogadores): `jsr $22074` / `bsr $1B7F2` → `jmp tick`. O bloco executa as duas chamadas originais e depois o contador.
- **RAM:** 8 bytes **no registro de cada jogador**, offset `$3A0` (P1 `$109620`, P2 `$109720`). Nenhuma instrução real usa os offsets `$39B–$3DE` do registro (varredura com bases deslocadas, descontando ruído de dados), e eles nunca mudaram numa sessão completa medida com `tools/lua/ram_scan.lua`. Campos: `+0` contador BCD, `+1` combo ativo, `+2` timer, `+4` vida anterior. O cmd `$10` lê o contador em `a5 + $1620` (P1) e `a5 + $1720` (P2).
- **Registros** (no próprio bloco):

| Registro | Posição | Conteúdo |
|---|---|---|
| P1 mostrar | número `$7048` (col. 2, lin. 8), texto `$7088` (col. 4) | `NN` + " HIT COMBO" (colunas 2–13) |
| P2 mostrar | número `$7348` (col. 26, lin. 8), texto `$7388` (col. 28) | `NN` + " HIT COMBO" (colunas 26–37) |
| Apagar | mesma posição | 12 espaços |

O cmd 8 realinha o registro para endereço par depois do `$FF` (`$11D6`). Strings de tamanho ímpar (com o `$FF`) levam 1 byte de enchimento antes do `00 00` final (`string2()` no patch).

## Correção (2026-10-24): reinício ao apertar start na tela de título

**Sintoma:** com o patch ativo, o jogo reiniciava ao apertar start na tela de título.

**Causa provável:** o tick roda em toda atualização de jogador (`$1B676`), inclusive na demo e na montagem da luta. Nessa hora `$64(a6)` (ponteiro do oponente) ainda pode conter lixo. Com um endereço ímpar, `move.w $6C(a0)` gera erro de endereço no 68000, e a BIOS reinicia o jogo.

**1ª correção (insuficiente):** o tick só roda se `a6` e `$64(a6)` forem os dois jogadores (`$109280` × `$109380`, em qualquer ordem). Caso contrário, sai direto pela continuação original. A escolha do lado (P1/P2) passou a usar o próprio endereço de `a6`. **O reinício continuou.**

**Causa real:** a RAM escolhida (`$10EF80`, fim da área de slots de objetos). Na demo da tela de título os dois jogadores são reais, então o contador gravava lá, e a área é usada na transição para a tela de seleção. A medição não detectou isso porque foi feita sem o patch, quando ninguém gravava ali antes da transição.

**2ª correção:** a RAM passou para o registro de cada jogador (offset `$3A0`, ver Implementação). A validação dos ponteiros foi mantida.

## Ferramentas

- `tools/asm68k.py` ganhou `Raw` (dados no bloco, fora da verificação do capstone) e `LeaPc` (`lea rótulo(pc),An`). A verificação passou a ser feita instrução por instrução.

## Pendências / riscos

- **RAM:** os offsets `$3A0–$3A7` do registro do jogador não são usados por nenhum código conhecido e não mudaram na medição. O contador só escreve com a luta montada (os dois ponteiros validados).
- **Defesa com dano:** golpes que tiram vida na defesa não contam (teste de defesa), mas também não quebram um combo ativo.
- **Posição:** linha 8, logo abaixo do "BEAT BY"; P2 alinhado para terminar na coluna 37. Ajustável em `POS`/`ROW`, e o texto em `LABEL`.

## Critérios de aceite

- [ ] Combo de 2+ acertos: aparece "2 HIT COMBO", "3 HIT COMBO"... do lado de quem atacou, na fonte do HUD
- [ ] Acerto isolado: nada aparece
- [ ] O texto some ~1,5 s depois do último acerto
- [ ] Combo do P2 aparece do lado direito
- [ ] Golpes defendidos não contam
- [ ] Apertar start na tela de título não reinicia o jogo
