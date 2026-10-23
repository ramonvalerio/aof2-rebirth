# ADR-0003: Especiais grátis via tabela de atributos (patch de dados)

- **Status:** Aceita
- **Data:** 2026-10-23
- **Spec:** [SPEC-003](../specs/SPEC-003-free-special-moves.md)

## Contexto

Os especiais devem parar de gastar barra, mas o SUPER e o DESPERATION precisam manter o custo. Todo desconto passa por uma rotina comum (`$1D7DE`), que não sabe qual handler originou o golpe; ela só recebe o custo em `$241(a6)`.

Opções avaliadas:

1. **Hook em `$1D7DE`** com uma lista de ids protegidos: exige código novo e uma busca em lista a cada golpe.
2. **Hook em cada handler de especial** (`$1D4DC`, `$1D504`, `$1D644`...): muitos pontos de entrada, com alto risco de esquecer algum.
3. **Zerar o custo na tabela de atributos `$23BA4`**: o custo só é lido na cópia de atributos e na checagem do SUPER. É um dado por golpe, sem código novo.

## Decisão

Opção 3. Para isso, o contrato de patches ganha o tipo `Data(addr, expect, new)` (`tools/patchlib.py`), aplicado pelo build com a mesma conferência de bytes originais e de conflitos dos hooks (SPEC-001).

A lista de golpes fica explícita no patch, com o custo original de cada um, e não é recalculada no build. Assim ela pode ser revisada e cada linha pode ser removida para reativar o custo de um golpe específico.

## Consequências

- (+) Nenhum código novo; o patch não usa o espaço livre da ROM.
- (+) Desligar o patch no manifest restaura todos os custos.
- (+) Se a ROM base mudar, o `expect` de cada byte acusa a divergência.
- (−) A classificação depende de qual handler está mapeado para cada comando. Golpes fora da faixa `$40–$47` não entram (ver pendências na SPEC-003).
