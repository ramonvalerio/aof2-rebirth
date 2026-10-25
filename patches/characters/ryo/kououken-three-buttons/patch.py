"""kououken-three-buttons (Ryo) — SPEC-033.

Versão do Kou'ouken (comando $40, golpes $011/$012/$013) pelo botão:
  v v> -> + soco fraco + soco forte (C+D) -> fraco $013 (startup 11, derruba;
                                             para cancel e combos)
  v v> -> + soco fraco (C)                -> médio $012 (não derruba)
  v v> -> + soco forte (D)                -> forte $011 (não derruba)

Hook compartilhado em $1D676 (charlib.SPECIAL_CHOSEN), depois da escolha
da versão pelo special-strength-by-button (SPEC-004): com o comando vindo do
jogador ($218 bit 9), troca $10(a5)/$5C(a4) e a barra equivalente $23F
(tamanho do projétil, $22A5C) pelas marcas do botão: bit 10 = C+D
(special-strength-by-button), bit 8 = forte. A CPU (sem bit 9) não muda.

Derrubar: byte 6 (efeito de acerto, $2135E) do $013, $00 -> $01, o efeito
da queda do Kohou forte (SPEC-010). O projétil leva o efeito do jogador
($20A -> $37 do projétil, $22A3A).
"""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import MOVE_TABLE, RYO, SPECIAL_CHOSEN, only, shared_hook
from patchlib import Block, Data, Patch

STRONG, MEDIUM, WEAK = 0x011, 0x012, 0x013
HIT_EFFECT = 6
KNOCKDOWN = 0x01
# barra equivalente com a marca do bit 7 (special-strength-by-button)
GAUGE = {STRONG: 0xC0, MEDIUM: 0xA0, WEAK: 0x80}
LEVEL = {STRONG: 3, MEDIUM: 2, WEAK: 1}


def pick(mid, last=False):
    return [
        Ins(f"3b7c{mid:04x}0010", f"move.w #${mid:x}, $10(a5)"),
        Ins(f"197c{LEVEL[mid]:04x}005c", f"move.b #${LEVEL[mid]:x}, $5c(a4)"),
        Ins(f"1d7c00{GAUGE[mid]:02x}023f", f"move.b #${GAUGE[mid]:x}, $23f(a6)"),
    ] + ([] if last else [Branch("bra", "out")])


choose = [
    *only(RYO, SPECIAL_CHOSEN),
    Ins("082e00010218", "btst.b #$1, $218(a6)"),      # bit 9: comando do jogador
    Branch("beq", "out"),
    Ins(f"0c6d{STRONG:04x}0010", f"cmpi.w #${STRONG:x}, $10(a5)"),
    Branch("bcs", "out"),
    Ins(f"0c6d{WEAK:04x}0010", f"cmpi.w #${WEAK:x}, $10(a5)"),
    Branch("bhi", "out"),
    Ins("082e00020218", "btst.b #$2, $218(a6)"),      # bit 10: C+D
    Branch("bne", "weak"),
    Ins("082e00000218", "btst.b #$0, $218(a6)"),      # bit 8: forte
    Branch("bne", "strong"),
    *pick(MEDIUM),
    Label("weak"),
    *pick(WEAK),
    Label("strong"),
    *pick(STRONG, last=True),
    Label("out"),
    JmpNext(SPECIAL_CHOSEN),
]

PATCH = Patch(
    id="kououken-three-buttons",
    title="Ryo: Kou'ouken fraco = C+D (derruba), médio = C, forte = D",
    spec="src/backend/specs/SPEC-033-ryo-kououken-three-buttons.md",
    blocks=[Block("kououken_buttons", choose)],
    hooks=[shared_hook(SPECIAL_CHOSEN, "kououken_buttons")],
    data=[Data(MOVE_TABLE + WEAK * 16 + HIT_EFFECT, "00", f"{KNOCKDOWN:02x}")],
)
