# Patches

Cada pasta é uma alteração isolada da P-ROM. As regras estão em [SPEC-001](../src/backend/specs/SPEC-001-rom-build-and-patches.md) e a decisão em [ADR-0001](../src/backend/adr/ADR-0001-modular-patch-architecture.md).

```
python tools/build_rom.py         # gera rom/aof2r.zip
python tools/build_rom.py --list  # lista patches ativos
```

| Patch | Spec |
|---|---|
| `controls-4button-layout` (C/D fortes, A+B arremesso, A+D uppercut, B+D chute baixo, START provoca) | [SPEC-002](../src/backend/specs/SPEC-002-controls-4button-layout.md) |
| `free-special-moves` (especiais não gastam barra; SUPER e DESPERATION mantêm o custo) | [SPEC-003](../src/backend/specs/SPEC-003-free-special-moves.md) |
| `special-strength-by-button` (A/B = especial fraco, C/D = especial forte, independente da barra) | [SPEC-004](../src/backend/specs/SPEC-004-special-strength-by-button.md) |
| `spirit-charge-abc` (carregar a barra exige A+B+C juntos) | [SPEC-005](../src/backend/specs/SPEC-005-spirit-charge-abc.md) |

Para criar um patch: crie `patches/<id>/patch.py` exportando `PATCH`, escreva a spec, adicione o id em `manifest.json` e rode o build.
