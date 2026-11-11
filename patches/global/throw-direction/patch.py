"""Arremesso para o lado do direcional — SPEC-087.

O arremesso ($1DB10) joga o oponente por cima do ombro, para TRÁS do atacante
(sem trocar de lugar). Só perto das paredes o jogo troca os lugares dos dois
($1DB5C: troca X e a direção) para o oponente não ser jogado contra a parede.

Nova regra no meio da tela ($A0 <= X < $260): o lado vem do direcional no
instante do agarrão ($68, o mesmo teste do $1DABE):
- segurando para trás: sem troca, o oponente cai atrás (o padrão do jogo);
- para frente ou neutro: troca de lugar, e o oponente cai à frente.
Perto das paredes continua a proteção original.

O lado "frente" vem de $5E(a4) bit 0 (1 = olhando para a direita): a frente é
o bit 3 ($08) de $68 quando é 1, o bit 2 ($04) quando é 0 (como no dash,
$1BBF0); "trás" é o outro.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

TARGET_BACK, TARGET_SWAP = 0x1DB82, 0x1DB5C   # sem troca / com troca
WALL_LEFT, WALL_RIGHT = 0x1DB3C, 0x1DB4A      # caminhos originais perto das paredes

throw_side = [
    Ins("0c6e00a00010", "cmpi.w #$a0, $10(a6)"),
    Branch("bcs", "wall_left"),
    Ins("0c6e02600010", "cmpi.w #$260, $10(a6)"),
    Branch("bcc", "wall_right"),
    Ins("48e7c000", "movem.l d0-d1, -(a7)"),
    Ins("700c", "moveq #$c, d0"),
    Ins("c02e0068", "and.b $68(a6), d0"),
    Ins("7204", "moveq #$4, d1"),                        # trás quando olha para a direita
    Ins("082c0000005e", "btst.b #$0, $5e(a4)"),
    Branch("bne", "mask"),
    Ins("7208", "moveq #$8, d1"),
    Label("mask"),
    Ins("c001", "and.b d1, d0"),
    Branch("bne", "back"),
    Ins("4cdf0003", "movem.l (a7)+, d0-d1"),
    JmpAbs(TARGET_SWAP),
    Label("back"),
    Ins("4cdf0003", "movem.l (a7)+, d0-d1"),
    JmpAbs(TARGET_BACK),
    Label("wall_left"),
    JmpAbs(WALL_LEFT),
    Label("wall_right"),
    JmpAbs(WALL_RIGHT),
]

PATCH = Patch(
    id="throw-direction",
    title="Arremesso para o lado do direcional (neutro = frente)",
    spec="src/backend/specs/SPEC-087-throw-direction.md",
    blocks=[Block("throw_side", throw_side)],
    hooks=[Hook(0x1DB32, "0c6e00a00010", to_block="throw_side")],
)
