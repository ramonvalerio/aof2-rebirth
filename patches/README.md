# Patches

Cada pasta é uma alteração isolada da P-ROM. As regras estão em [SPEC-001](../src/backend/specs/SPEC-001-rom-build-and-patches.md) e as decisões em [ADR-0001](../src/backend/adr/ADR-0001-modular-patch-architecture.md) e [ADR-0005](../src/backend/adr/ADR-0005-global-vs-character-patches.md).

```
python tools/build_rom.py         # gera rom/aof2r.zip
python tools/build_rom.py --list  # lista patches ativos por categoria
```

## Categorias

```
patches/
  manifest.json                           # ordem: "global" e depois "characters"
  global/<id>/patch.py                    # regra que vale para TODOS os personagens
  characters/<personagem>/<id>/patch.py   # alteração de UM personagem
```

- **Global**: botões, controles e mecânicas do jogo (barra, força dos especiais, custo etc.). A regra é a mesma para o elenco inteiro, mesmo que o patch altere dados de vários personagens.
- **Personagem**: muda um personagem específico (dano, frames, comandos ou golpes de um lutador), sem efeito nos outros.

Os globais são aplicados antes dos de personagem.

## Globais

| Patch | Spec |
|---|---|
| `controls-4button-layout` (C/D fortes, A+B arremesso, A+D uppercut, B+D chute baixo, START provoca) | [SPEC-002](../src/backend/specs/SPEC-002-controls-4button-layout.md) |
| `free-special-moves` (especiais não gastam barra; SUPER e DESPERATION mantêm o custo) | [SPEC-003](../src/backend/specs/SPEC-003-free-special-moves.md) |
| `special-strength-by-button` (A/B = especial fraco, C/D = especial forte, independente da barra) | [SPEC-004](../src/backend/specs/SPEC-004-special-strength-by-button.md) |
| `spirit-charge-abc` (carregar a barra exige A+B+C juntos) | [SPEC-005](../src/backend/specs/SPEC-005-spirit-charge-abc.md) |

## Personagens

Nenhum ainda.

## Criar um patch

1. Escolha a categoria e crie `patches/global/<id>/patch.py` ou `patches/characters/<personagem>/<id>/patch.py`, exportando `PATCH` (o `id` é igual ao nome da pasta).
2. Escreva a spec em `src/backend/specs/`.
3. Adicione o id em `manifest.json`: em `"global"`, ou em `"characters": {"<personagem>": [...]}`.
4. Rode o build.
