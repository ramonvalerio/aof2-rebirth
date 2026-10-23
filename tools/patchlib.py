"""Modelo de dados dos patches (ver SPEC-001 e ADR-0001).

Cada patch em patches/<id>/patch.py exporta `PATCH = Patch(...)` contendo:
  - blocks: rotinas novas, alocadas pelo build no espaço livre da P-ROM;
  - hooks:  sobrescritas em endereços da ROM original, sempre com os bytes
            originais esperados (o build aborta se eles não baterem);
  - data:   alterações de tabelas (sem código), também com bytes esperados.

Um hook pode saltar para um bloco do próprio patch: `JmpAbs` com o endereço
resolvido pelo build via `Hook.to_block`.
"""
from dataclasses import dataclass, field

from asm68k import assemble, size_of, JmpAbs


@dataclass
class Block:
    name: str
    program: list


@dataclass
class Hook:
    addr: int          # endereço 68k (P-ROM em big-endian)
    expect: str        # bytes originais em hex
    program: list = None
    to_block: str = None  # atalho: grava "jmp <bloco>.l" e preenche o resto com NOP

    def build(self, block_addrs):
        program = self.program
        if self.to_block is not None:
            program = [JmpAbs(block_addrs[self.to_block])]
        code = assemble(program, self.addr)
        pad = len(bytes.fromhex(self.expect)) - len(code)
        if pad < 0 or pad % 2:
            raise ValueError(f"hook ${self.addr:x}: código ({len(code)} bytes) não cabe em expect")
        return code + bytes.fromhex("4e71") * (pad // 2)


@dataclass
class Data:
    addr: int     # endereço 68k
    expect: str   # bytes originais em hex
    new: str      # bytes novos em hex (mesmo tamanho)


@dataclass
class Patch:
    id: str
    title: str
    spec: str
    blocks: list = field(default_factory=list)
    hooks: list = field(default_factory=list)
    data: list = field(default_factory=list)

    def block_sizes(self):
        return {b.name: size_of(b.program) for b in self.blocks}
