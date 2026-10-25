"""controls-4button-layout — SPEC-002.

Botões físicos: A=chute fraco, B=chute forte, C=soco fraco, D=soco forte,
A+C=arremesso, C+D=uppercut, B+D=chute baixo, START=provocação.

Troca dos botões ($9D24, cópia do joystick para o objeto de input do
jogador, $109080/$109180): os bits 4-7 de $68/$69/$6A são permutados para
a FUNÇÃO de cada botão, e o resto do jogo (tradutor abaixo, leitor de
comandos, ataques no ar) passa a ver:
  bit 4 = soco fraco   <- C      bit 5 = chute fraco <- A
  bit 6 = soco forte   <- D      bit 7 = chute forte <- B
Os menus leem o joystick bruto ($31C/$322(a5)) e não mudam. Daqui para
baixo, "A/B/C/D" = função (soco fraco / chute fraco / soco forte / chute forte).

Substitui a rotina original $1D87C, que traduz o input bruto do jogador
($68 seguro / $69 recém-pressionado) nos comandos de luta:
  $270 bit4/bit5 = dispara soco/chute     $271 bit4/bit5 = versão forte
  $270 bit6      = "C segurado": soco/chute viram uppercut/chute baixo
  $271 bit6      = C pressionado (tenta arremesso em $1DABE)
  $271 bit7      = D pressionado (provocação em $1DA28)
No original a força vinha de quanto tempo A/B ficavam segurados (8 frames).

C original "repete o último ataque" ($1D896): ao soltar o C, $1D8E2 fazia
or.b $235,$270 (soco/chute sem marca de forte). No layout novo isso virava
um soco fraco espontâneo; o "or" vira NOP.

Os bytes $272/$273 do jogador (antes, timers de A/B) passam a ser:
  $272 = botões pendentes (bits 4-7)   $273 = frames restantes da janela
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Data, Hook, Patch

# bit físico -> bit da função
BUTTON_MAP = {4: 5, 5: 7, 6: 4, 7: 6}


def permute(off):
    out = [
        Ins(f"1029{off:04x}", f"move.b ${off:x}(a1), d0"),
        Ins("1200", "move.b d0, d1"),
        Ins("0201000f", "andi.b #$f, d1"),          # direções
    ]
    for src, dst in BUTTON_MAP.items():
        out += [
            Ins(f"0800000{src}", f"btst.b #${src}, d0"),
            Branch("beq", f"b{off}_{src}"),
            Ins(f"08c1000{dst}", f"bset.b #${dst}, d1"),
            Label(f"b{off}_{src}"),
        ]
    out.append(Ins(f"1341{off:04x}", f"move.b d1, ${off:x}(a1)"))
    return out


# Substitui a sub-rotina inteira de $9D24 (a0 = joystick, a1 = objeto de input).
remap_buttons = [
    Ins("336800020068", "move.w $2(a0), $68(a1)"),   # original
    Ins("10280001", "move.b $1(a0), d0"),
    Ins("4600", "not.b d0"),
    Ins("12280002", "move.b $2(a0), d1"),
    Ins("4601", "not.b d1"),
    Ins("b300", "eor.b d1, d0"),
    Ins("c001", "and.b d1, d0"),
    Ins("1340006a", "move.b d0, $6a(a1)"),
    *permute(0x68), *permute(0x69), *permute(0x6A),
    Ins("4e75", "rts"),
]

# Frames extras de espera por um segundo botão (físico A+C / C+D / A+B) depois do primeiro.
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
    # soco fraco + chute fraco (físico A+C) -> arremesso
    Ins("7230", "moveq #$30, d1"),
    Ins("c200", "and.b d0, d1"),
    Ins("0c010030", "cmpi.b #$30, d1"),
    Branch("beq", "throw"),
    # soco fraco + soco forte (físico C+D) -> uppercut (soco com "C segurado")
    Ins("7250", "moveq #$50, d1"),
    Ins("c200", "and.b d0, d1"),
    Ins("0c010050", "cmpi.b #$50, d1"),
    Branch("beq", "uppercut"),
    # soco forte + chute forte (físico D+B) -> chute baixo (chute com "C segurado")
    Ins("72c0", "moveq #$c0, d1"),
    Ins("c200", "and.b d0, d1"),
    Ins("0c0100c0", "cmpi.b #$c0, d1"),
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
    Branch("bsr", "kohou_break"), Branch("bne", "clear"),
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
    Label("kohou_break"),
    Ins("0c6e00010062", "cmpi.w #$1, $62(a6)"), Branch("bne", "not_break"),
    Ins("0c6e00470230", "cmpi.w #$47, $230(a6)"), Branch("beq", "break_move"),
    Ins("0c6e00430230", "cmpi.w #$43, $230(a6)"), Branch("bne", "not_break"),
    Label("break_move"),
    Ins("0c2e000303b4", "cmpi.b #$3, $3b4(a6)"), Branch("bne", "not_break"),
    Ins("0c2e00020041", "cmpi.b #$2, $41(a6)"), Branch("bne", "not_break"),
    Ins("1d7c000103b5", "move.b #$1, $3b5(a6)"),
    Ins("7001", "moveq #$1, d0"), Ins("4e75", "rts"),
    Label("not_break"), Ins("7000", "moveq #$0, d0"), Ins("4e75", "rts"),
]

PATCH = Patch(
    id="controls-4button-layout",
    title="Controles: A/B chutes, C/D socos, A+C arremesso, C+D uppercut, B+D chute baixo, START provoca",
    spec="src/backend/specs/SPEC-002-controls-4button-layout.md",
    blocks=[Block("translate_input", translate_input), Block("remap_buttons", remap_buttons)],
    hooks=[
        # $9D24: move.w $2(a0),$68(a1)  (início da sub-rotina; o resto não é mais alcançado)
        Hook(addr=0x9D24, expect="336800020068", to_block="remap_buttons"),
        # move.w $68(a6),d0 / andi.w #$cfcf,d0  ->  jmp translate_input
        Hook(addr=0x1D87C, expect="302e00680240cfcf", to_block="translate_input"),
        # $1D8E2: or.b d1,$270(a6) — ao soltar o C, o original repetia o último
        # ataque ($235, sem marca de forte) = soco fraco "fantasma". Anulado.
        Hook(addr=0x1D8E2, expect="832e0270",
             program=[Ins("4e71", "nop"), Ins("4e71", "nop")]),
        # $1DAD4: beq.b $1daf2 — o arremesso ($1DABE) exigia <- ou -> no
        # input bruto ($68 & $0C). O lado do arremesso vem da posição
        # ($1DB10), não da direção: A+C (físico) perto basta, em pé ou agachado.
        Hook(addr=0x1DAD4, expect="671c", program=[Ins("4e71", "nop")]),
    ],
    data=[
        # $21F66: move.b #$f0,d0 / and.b $60(a2),d0 / bne — o alcance de
        # arremesso ($A68 bit 0) só liga com os bits 4-7 de $60 zerados; o
        # bit 5 é "agachado". Máscara $D0: arremessa agachado também.
        Data(0x21F69, "f0", "d0"),
    ],
)
