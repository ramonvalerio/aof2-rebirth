"""Ryo: chute fraco aéreo conecta pressão no chão — SPEC-059."""
from asm68k import Branch, Ins, JmpAbs, JmpNext, Label
from charlib import LANDING_ATTACK, REACTION_PUSH, shared_hook
from patchlib import Block, Patch

landing = [
    Ins("0c6e00010062", "cmpi.w #$1, $62(a6)"),
    Branch("bne", "original"),
    Ins("0c6e003a0230", "cmpi.w #$3a, $230(a6)"),
    Branch("bne", "original"),
    Ins("4a2e021b", "tst.b $21b(a6)"),
    Branch("bne", "original"),
    Ins("4a6e006c", "tst.w $6c(a6)"),
    Branch("ble", "original"),
    # Este ponto só é alcançado depois de a física limpar a marca aérea.
    Ins("422e0240", "clr.b $240(a6)"),
    Ins("08ae00070060", "bclr.b #$7, $60(a6)"),
    # Saída nativa do ataque: neutro/agachado e execução de entrada atual.
    JmpAbs(0x1C2EA),
    Label("original"),
    JmpNext(LANDING_ATTACK),
]

pushback = [
    Ins("48e74040", "movem.l d1/a1, -(a7)"),
    Ins("0c6e003a0a6a", "cmpi.w #$3a, $a6a(a6)"),
    Branch("bne", "out"),
    Ins("226e0064", "movea.l $64(a6), a1"),
    Ins("0c6900010062", "cmpi.w #$1, $62(a1)"),
    Branch("bne", "out"),
    Ins("4aae0018", "tst.l $18(a6)"),
    Branch("bne", "out"),
    Ins("0c2e00060040", "cmpi.b #$6, $40(a6)"),
    Branch("beq", "reaction"),
    Ins("0c2e00070040", "cmpi.b #$7, $40(a6)"),
    Branch("bne", "out"),
    Label("reaction"),
    Ins("720f", "moveq #$f, d1"),
    Ins("c22e007c", "and.b $7c(a6), d1"),
    Ins("0c010003", "cmpi.b #$3, d1"),
    Branch("beq", "out"),
    # 1 px por aplicação de movimento da reação, com sinal nativo por lado.
    Ins("203c00010000", "move.l #$10000, d0"),
    Label("out"),
    Ins("4cdf0202", "movem.l (a7)+, d1/a1"),
    JmpNext(REACTION_PUSH),
]

PATCH = Patch(
    id="jump-lk-pressure",
    title="Ryo: chute fraco aéreo com recuo uniforme e aterrissagem livre ao conectar",
    spec="src/backend/specs/SPEC-059-ryo-jump-lk-pressure.md",
    blocks=[Block("ryo_jump_lk_landing", landing), Block("ryo_jump_lk_pushback", pushback)],
    hooks=[
        shared_hook(LANDING_ATTACK, "ryo_jump_lk_landing"),
        shared_hook(REACTION_PUSH, "ryo_jump_lk_pushback"),
    ],
)
