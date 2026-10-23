# SPEC-001: Build da ROM e arquitetura de patches

- **Status:** Ativa
- **Decisão relacionada:** [ADR-0001](../adr/ADR-0001-modular-patch-architecture.md)

## Objetivo

Gerar o rom hack `rom/aof2r.zip` (Art of Fighting 2 Rebirth) de forma reproduzível, a partir da ROM original `rom/aof2.zip` e de um conjunto de patches modulares e isolados.

## Entradas e saídas

| Item | Caminho | Observação |
|---|---|---|
| ROM base | `rom/aof2.zip` | Set MAME/FBNeo `aof2` (NGM-056). Nunca é alterada. |
| Manifest | `patches/manifest.json` | Lista ordenada dos patches ativos. |
| Patches | `patches/<id>/patch.py` | Um diretório por alteração. |
| Saída | `rom/aof2r.zip` | Recriada do zero a cada build. Mesmos nomes de arquivo do set `aof2`. |

Comando: `python tools/build_rom.py` (`--list` lista os patches ativos).

Dependência: Python 3.10+ e `capstone` (`pip install capstone`).

## Fatos de hardware usados

- A P-ROM `056-p1.p1` (1 MiB) fica armazenada em *word-swap*. O build troca os bytes de cada palavra antes de aplicar os patches e destroca no final. Todos os endereços nos patches são endereços 68000 (big-endian).
- Espaço livre: a região `$0FDDA0–$0FFF00` está zerada na ROM original. O build aloca blocos novos em `$0FE000–$0FFE00`.
- O SHA-1 do `056-p1.p1` original (`ee42f3ca…cd71`) é conferido antes de qualquer patch.

## Contrato de um patch

Cada `patches/<id>/patch.py` exporta `PATCH = Patch(...)` (`tools/patchlib.py`):

- `id`: igual ao nome da pasta, em kebab-case.
- `title`: o que o patch faz.
- `spec`: caminho da spec que define o comportamento.
- `blocks`: rotinas novas. O build escolhe o endereço; o patch não fixa endereço de código novo.
- `hooks`: sobrescritas de código na ROM original. Cada hook declara `expect`, os bytes originais naquele endereço. O espaço que sobrar é preenchido com `NOP`.
- `data`: alterações de tabelas, sem código (`Data(addr, expect, new)`). Também declaram os bytes originais e não podem mudar de tamanho.

Assembly: cada instrução é escrita como encoding hex + texto de desmontagem esperado (`tools/asm68k.py`). Os desvios curtos e o `JMP` absoluto usam rótulos.

## Regras que o build garante (falha = build abortado)

1. O SHA-1 da P-ROM base é o esperado.
2. Os bytes `expect` de cada hook e de cada `data` conferem com a ROM original.
3. Nenhum byte é escrito por dois patches (conflito entre patches).
4. Blocos novos só ocupam espaço livre (zerado) e cabem na região reservada.
5. O código gerado desmonta (capstone) exatamente no texto declarado.
6. A saída é determinística: mesmas entradas geram o mesmo zip.

## Regras de modularidade

- Um patch = uma alteração de comportamento, com sua própria spec.
- Um patch não depende do endereço de bloco de outro patch. Se dois patches precisarem cooperar, a dependência deve ser explícita em uma spec/ADR.
- Desativar um patch = removê-lo do `manifest.json`; o restante continua funcionando.
- Variáveis de RAM reaproveitadas ou novas devem ser listadas na spec do patch.

## Distribuição

ROMs e BIOS são propriedade da SNK e não entram no git (`.gitignore`). O repositório contém apenas código, patches e documentação.
