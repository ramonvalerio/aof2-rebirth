# ADR-0005: Separação entre patches globais e de personagem

- **Status:** Aceita
- **Data:** 2026-10-23
- **Atualiza:** [ADR-0001](ADR-0001-modular-patch-architecture.md), [SPEC-001](../specs/SPEC-001-rom-build-and-patches.md)

## Contexto

Os primeiros patches (controles, custo de barra, força dos especiais, carga da barra) mudam regras que valem para o elenco inteiro. As próximas alterações devem incluir ajustes de personagens específicos. Na pasta plana `patches/<id>`, não dava para saber o alcance de um patch sem ler o código.

## Decisão

- `patches/global/<id>`: botões, controles e mecânicas. A regra vale para todos os personagens. Um patch que altera dados de vários personagens com **a mesma regra** (ex.: `free-special-moves`) é global.
- `patches/characters/<personagem>/<id>`: alterações que afetam um único personagem.
- `manifest.json` separa `"global"` (lista) de `"characters"` (mapa personagem → lista). O build aplica os globais primeiro, depois os de personagem.
- O launcher mostra as duas seções separadas.
- Os patches não ajustam mais o `sys.path` com uma profundidade fixa de pasta. O build e o launcher já colocam `tools/` no path antes de carregar os patches.

## Consequências

- (+) O alcance de cada alteração fica explícito na pasta e no manifest.
- (+) Um patch de personagem pode partir das regras globais já aplicadas.
- (+) As garantias do build (bytes originais, conflitos, espaço livre) valem igualmente para as duas categorias.
- (−) Se um patch de personagem precisar mudar um byte que um global já altera, o build acusa conflito. A solução é ajustar o global (ex.: excluir aquele golpe da lista) e documentar na spec.
