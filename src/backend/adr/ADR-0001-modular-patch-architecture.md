# ADR-0001: Arquitetura modular de patches da P-ROM

- **Status:** Aceita
- **Data:** 2026-10-23

## Contexto

O Rebirth vai acumular muitas alterações de gameplay na ROM do AOF2. Editar a ROM à mão ou manter um único IPS monolítico torna impossível saber qual byte pertence a qual mudança, desligar uma mudança isolada ou detectar duas mudanças sobrescrevendo a mesma área.

Não há assembler 68000 instalado no ambiente (Windows, sem gcc/vasm).

## Decisão

1. Cada alteração vive em `patches/<id>/patch.py`, com spec própria em `src/backend/specs/`.
2. `patches/manifest.json` define quais patches estão ativos e em que ordem.
3. `tools/build_rom.py` gera `rom/aof2r.zip` a partir da ROM original intacta, validando bytes originais, conflitos entre patches e espaço livre (ver SPEC-001).
4. Código novo vai em blocos realocáveis. O build escolhe o endereço na região livre; os hooks saltam para o bloco pelo nome.
5. O assembly é escrito como encoding hex + texto esperado, validado com o capstone no build (`tools/asm68k.py`).

## Consequências

- (+) Cada mudança é isolada, revisável e removível pelo manifest.
- (+) Um erro de digitação no encoding vira erro de build, não bug em jogo.
- (+) Não precisa de toolchain externa além de Python + capstone.
- (−) Escrever o encoding à mão é trabalhoso. Se as rotinas crescerem, reavaliar a adoção do vasm (`vasmm68k_mot`) mantendo o mesmo contrato de blocos/hooks.
- (−) Só há ~7,5 KiB de espaço livre na P-ROM. Expandir a ROM vai exigir outra ADR.
