"""Modelo de dados dos patches (ver SPEC-001 e ADR-0001).

Cada patch em patches/<id>/patch.py exporta `PATCH = Patch(...)` contendo:
  - blocks: rotinas novas, alocadas pelo build no espaço livre da P-ROM;
  - hooks:  sobrescritas em endereços da ROM original, sempre com os bytes
            originais esperados (o build aborta se eles não baterem);
  - data:   alterações de tabelas (sem código), também com bytes esperados.

Um hook pode saltar para um bloco do próprio patch: `JmpAbs` com o endereço
resolvido pelo build via `Hook.to_block`.

Hook encadeado (`chain`): vários patches (ex.: um por personagem) podem
enganchar no mesmo endereço. O build grava um único jmp no jogo e liga os
blocos em sequência, na ordem do manifest; cada bloco termina com
`JmpNext(addr)` quando não é a vez dele. `original` é o código deslocado
(relocável: sem desvios relativos ao PC), executado pelo build:
  chain="before": jogo -> bloco 1 -> ... -> bloco N -> original -> addr+len
  chain="after":  jogo -> original -> bloco 1 -> ... -> bloco N -> addr+len
Todos os patches do mesmo endereço declaram o mesmo expect, chain e original.
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
    chain: str = None     # "before" / "after": hook encadeado (ver acima)
    original: list = None  # hook encadeado: código deslocado, relocável

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
class DataBlock:
    """Dados novos (tabelas, animações) alocados pelo build no espaço livre.

    `build(org)` devolve os bytes já ajustados para o endereço `org`
    (para dados com offsets relativos). Não passa pela verificação de
    desmontagem, que vale só para código.
    """
    name: str
    size: int
    build: object  # callable(org) -> bytes


@dataclass
class Data:
    addr: int     # endereço 68k
    expect: str   # bytes originais em hex
    new: object   # bytes novos em hex (mesmo tamanho), ou callable(block_addrs) -> hex


@dataclass
class Patch:
    id: str
    title: str
    spec: str
    blocks: list = field(default_factory=list)
    hooks: list = field(default_factory=list)
    data: list = field(default_factory=list)

    def block_sizes(self):
        return {b.name: (b.size if isinstance(b, DataBlock) else size_of(b.program))
                for b in self.blocks}
