# SPEC-001: Build da ROM e arquitetura de patches

- **Status:** Ativa
- **Decisão relacionada:** [ADR-0001](../adr/ADR-0001-modular-patch-architecture.md)

## Objetivo

Gerar o rom hack `rom/aof2r.zip` (Art of Fighting 2 Rebirth) de forma reproduzível, a partir da ROM original `rom/aof2.zip` e de um conjunto de patches modulares e isolados.

## Entradas e saídas

| Item | Caminho | Observação |
|---|---|---|
| ROM base | `rom/aof2.zip` | Set MAME/FBNeo `aof2` (NGM-056). Nunca é alterada. |
| Manifest | `patches/manifest.json` | Patches ativos: `"global"` (lista) e `"characters"` (personagem → lista). |
| Patches globais | `patches/global/<id>/patch.py` | Botões e mecânicas que valem para todos os personagens. |
| Patches de personagem | `patches/characters/<personagem>/<id>/patch.py` | Alterações de um personagem específico. |
| Saída | `rom/aof2r.zip` | Recriada do zero a cada build. Mesmos nomes de arquivo do set `aof2`. |

Comando: `python tools/build_rom.py` (`--list` lista os patches ativos).

Dependência: Python 3.10+ e `capstone` (`pip install capstone`).

## Fatos de hardware usados

- A P-ROM `056-p1.p1` (1 MiB) fica armazenada em *word-swap*. O build troca os bytes de cada palavra antes de aplicar os patches e destroca no final. Todos os endereços nos patches são endereços 68000 (big-endian).
- Espaço livre: a região `$0FDDA0–$0FFF00` está zerada na ROM original. O build aloca blocos novos em `$0FE000–$0FFE00`.
- O SHA-1 do `056-p1.p1` original (`ee42f3ca…cd71`) é conferido antes de qualquer patch.

## Contrato de um patch

Cada `patch.py` (global ou de personagem, ver [ADR-0005](../adr/ADR-0005-global-vs-character-patches.md)) exporta `PATCH = Patch(...)` (`tools/patchlib.py`):

- `id`: igual ao nome da pasta, em kebab-case.
- `title`: o que o patch faz.
- `spec`: caminho da spec que define o comportamento.
- `blocks`: rotinas novas. O build escolhe o endereço; o patch não fixa endereço de código novo.
- `hooks`: sobrescritas de código na ROM original. Cada hook declara `expect`, os bytes originais naquele endereço. O espaço que sobrar é preenchido com `NOP`.
- `data`: alterações de tabelas, sem código (`Data(addr, expect, new)`). Também declaram os bytes originais e não podem mudar de tamanho. `new` pode ser uma função dos endereços dos blocos (para ponteiros).
- `DataBlock(name, size, build)`: dados novos (ex.: animações) alocados no espaço livre; `build(org)` gera os bytes para o endereço escolhido.

Assembly: cada instrução é escrita como encoding hex + texto de desmontagem esperado (`tools/asm68k.py`), conferido instrução por instrução. Os desvios curtos, o `JMP` absoluto e o `LEA rótulo(PC)` usam rótulos. Dados dentro de um bloco (ex.: registros de texto) usam `Raw`.

## Regras que o build garante (falha = build abortado)

1. O SHA-1 da P-ROM base é o esperado.
2. Os bytes `expect` de cada hook e de cada `data` conferem com a ROM original.
3. Nenhum byte é escrito por dois patches (conflito entre patches). Exceção: hooks encadeados (`Hook.chain`, ver `tools/charlib.py`), em que vários patches de personagem declaram o mesmo endereço com os mesmos bytes originais e o build grava um único `jmp`, ligando os blocos em sequência na ordem do manifest e terminando no código original deslocado.
4. Blocos novos só ocupam espaço livre (zerado) e cabem na região reservada.
5. O código gerado desmonta (capstone) exatamente no texto declarado.
6. A saída é determinística: mesmas entradas geram o mesmo zip.

Verificação extra (manual, ~1 min): `python tools/hook_check.py` confirma que nenhum desvio do jogo (`bcc`/`bra`/`bsr`/`jmp`/`jsr`) aponta para o **meio** de um hook, o que faria o processador executar lixo. Rodar sempre que um hook novo for criado.

## Regras de modularidade

- Um patch = uma alteração de comportamento, com sua própria spec.
- Um patch não depende do endereço de bloco de outro patch. Se dois patches precisarem cooperar, a dependência deve ser explícita em uma spec/ADR.
- Ordem de aplicação: todos os globais (na ordem do manifest) e depois os de personagem.
- Desativar um patch = removê-lo do `manifest.json`; o restante continua funcionando.
- Variáveis de RAM reaproveitadas ou novas devem ser listadas na spec do patch.

## Distribuição

ROMs e BIOS são propriedade da SNK e não entram no git (`.gitignore`). O repositório contém apenas código, patches e documentação.
