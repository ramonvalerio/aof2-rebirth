"""SPEC-042: leitor de direcionais durante a defesa, sem guardar botões.

Usado com directional-only-special-buffer (SPEC-052), que impede completar
etapas de botão enquanto o jogador não pode executar o especial.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

WINDOW = 12     # frames de vida do especial reconhecido na defesa (= prazo entre passos, SPEC-008)

block_reader = [
    # Só acompanha os direcionais. Nenhum comando completo atravessa a defesa.
    Ins("426e0218", "clr.w $218(a6)"),
    Ins("4eb90001df7e", "jsr $1df7e.l"),
    Ins("426e0218", "clr.w $218(a6)"),
    Ins("422e0253", "clr.b $253(a6)"),
    JmpAbs(0x1C60C),
]

PATCH = Patch(
    id="blockstun-command-buffer",
    title="Direcionais de especial durante a defesa; botão somente ao executar",
    spec="src/backend/specs/SPEC-042-blockstun-command-buffer.md",
    blocks=[Block("block_reader", block_reader)],
    hooks=[
        # $1C604: clr.w $218(a6) / clr.b $253(a6)  (segue em $1C60C)
        Hook(addr=0x1C604, expect="426e0218422e0253", to_block="block_reader"),
    ],
)
