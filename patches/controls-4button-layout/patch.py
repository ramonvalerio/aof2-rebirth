"""controls-4button-layout — SPEC-002.

A=soco fraco, B=chute fraco, C=soco forte, D=chute forte,
A+B=arremesso, A+D=uppercut, B+D=chute baixo, START=provocação.

Substitui a rotina original $1D87C, que traduz o input bruto do jogador
($68 seguro / $69 recém-pressionado) nos comandos de luta:
  $270 bit4/bit5 = dispara soco/chute     $271 bit4/bit5 = versão forte
  $270 bit6      = "C segurado": soco/chute viram uppercut/chute baixo
  $271 bit6      = C pressionado (tenta arremesso em $1DABE)
  $271 bit7      = D pressionado (provocação em $1DA28)
No original a força vinha de quanto tempo A/B ficavam segurados (8 frames).

Os bytes $272/$273 do jogador (antes, timers de A/B) passam a ser:
  $272 = botões pendentes (bits 4-7)   $273 = frames restantes da janela
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from asm68k import Branch, Ins, JmpAbs, Label  # noqa: E402
from patchlib import Block, Hook, Patch  # noqa: E402

# Frames extras de espera por um segundo botão (A+B / C+D) depois do primeiro.
PAIR_WINDOW = 2

# Cauda da rotina original: libera o estado de "C segurado" ($A6F/$A70).
ORIG_TAIL = 0x1D91C

translate_input = [
    # saída base: direções seguradas / recém-pressionadas, sem botões
    Ins("302e0068", "move.w $68(a6), d0"),
    Ins("02400f0f", "andi.w #$f0f, d0"),
    Ins("3d400270", "move.w d0, $270(a6)"),
    # START do controle deste jogador -> provocação
    # ($32B(a5) = START/SELECT recém-pressionados: bit0 P1, bit2 P2)
    Ins("7200", "moveq #$0, d1"),
    Ins("4a6efe62", "tst.w -$19e(a6)"),
    Branch("beq", "start_bit"),
    Ins("7202", "moveq #$2, d1"),
    Label("start_bit"),
    # (em memória o btst é sempre de byte; o capstone escreve ".l")
    Ins("032d032b", "btst.l d1, $32b(a5)"),
    Branch("beq", "buttons"),
    Ins("08ee00070271", "bset.b #$7, $271(a6)"),
    Label("buttons"),
    # acumula botões novos na fila de pendentes
    Ins("102e0069", "move.b $69(a6), d0"),
    Ins("020000f0", "andi.b #$f0, d0"),
    Branch("beq", "check"),
    Ins("4a2e0272", "tst.b $272(a6)"),
    Branch("bne", "merge"),
    Ins(f"1d7c{PAIR_WINDOW:04x}0273", f"move.b #${PAIR_WINDOW:x}, $273(a6)"),
    Label("merge"),
    Ins("812e0272", "or.b d0, $272(a6)"),
    Label("check"),
    Ins("102e0272", "move.b $272(a6), d0"),
    Branch("beq", "done"),
    # A+B -> arremesso
    Ins("7230", "moveq #$30, d1"),
    Ins("c200", "and.b d0, d1"),
    Ins("0c010030", "cmpi.b #$30, d1"),
    Branch("beq", "throw"),
    # A+D -> uppercut (soco com "C segurado")
    Ins("7290", "moveq #$90, d1"),
    Ins("c200", "and.b d0, d1"),
    Ins("0c010090", "cmpi.b #$90, d1"),
    Branch("beq", "uppercut"),
    # B+D -> chute baixo (chute com "C segurado")
    Ins("72a0", "moveq #$a0, d1"),
    Ins("c200", "and.b d0, d1"),
    Ins("0c0100a0", "cmpi.b #$a0, d1"),
    Branch("beq", "low_kick"),
    # sem par: espera a janela acabar
    Ins("532e0273", "subq.b #$1, $273(a6)"),
    Branch("bhi", "done"),
    # resolve botões isolados; d1 = bits de "forte"
    Ins("7200", "moveq #$0, d1"),
    Ins("08000006", "btst.b #$6, d0"),
    Branch("beq", "no_c"),
    Ins("00000010", "ori.b #$10, d0"),
    Ins("00010010", "ori.b #$10, d1"),
    Label("no_c"),
    Ins("08000007", "btst.b #$7, d0"),
    Branch("beq", "no_d"),
    Ins("00000020", "ori.b #$20, d0"),
    Ins("00010020", "ori.b #$20, d1"),
    Label("no_d"),
    Ins("02000030", "andi.b #$30, d0"),
    Ins("812e0270", "or.b d0, $270(a6)"),
    Ins("832e0271", "or.b d1, $271(a6)"),
    Branch("bra", "clear"),
    Label("throw"),
    Ins("08ee00060271", "bset.b #$6, $271(a6)"),
    Branch("bra", "clear"),
    Label("uppercut"),
    Ins("002e00500270", "ori.b #$50, $270(a6)"),
    Branch("bra", "clear"),
    Label("low_kick"),
    Ins("002e00600270", "ori.b #$60, $270(a6)"),
    Label("clear"),
    Ins("422e0272", "clr.b $272(a6)"),
    Label("done"),
    JmpAbs(ORIG_TAIL),
]

PATCH = Patch(
    id="controls-4button-layout",
    title="Controles: C/D fortes, A+B arremesso, A+D uppercut, B+D chute baixo, START provoca",
    spec="src/backend/specs/SPEC-002-controls-4button-layout.md",
    blocks=[Block("translate_input", translate_input)],
    hooks=[
        # move.w $68(a6),d0 / andi.w #$cfcf,d0  ->  jmp translate_input
        Hook(addr=0x1D87C, expect="302e00680240cfcf", to_block="translate_input"),
    ],
)
