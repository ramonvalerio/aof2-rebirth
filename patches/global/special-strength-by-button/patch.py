"""special-strength-by-button — SPEC-004.

A versão do especial passa a depender do botão, não da barra de espírito:
  botão fraco (A/B)  -> versão "barra vermelha" (nível 1, id+2); se essa for a
                        versão de falha (golpe não sai), usa a média (nível 2, id+1)
  botão forte (C/D)  -> versão "barra cheia"    (nível 3, id+0)

Original ($1D53E): nível pela barra ($224) com limites em $22AF0
($40 -> nível 3, $20 -> nível 2, abaixo -> nível 1); o nível vai para
$5C(a4) e a variante do golpe é $10(a5) + 0/1/2.

Como o especial detectado fica até 60 frames em $218(a6) antes de executar,
a força é registrada na detecção ($1E102), nos bits altos de $218:
  bit 9 = comando vindo do leitor de comandos do jogador (força pelo botão)
  bit 8 = botão forte ($271 bit 4/5 no frame da detecção)
$1D41E já descarta esses bits (andi.w #$7f). Comandos sem o bit 9 (IA)
seguem a regra original da barra.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

AFTER_DETECT = 0x1E10C   # moveq #0,d0 / rts do detector
LEVEL_DONE = 0x1D676     # continuação comum após escolher o nível
GAUGE_CONT = 0x1D554     # bcc.w do teste original de barra

# Substitui: move.w d0,$218(a6) / move.b #$3c,$a77(a6)
tag_command = [
    Ins("00400200", "ori.w #$200, d0"),
    Ins("082e00040271", "btst.b #$4, $271(a6)"),
    Branch("bne", "strong"),
    Ins("082e00050271", "btst.b #$5, $271(a6)"),
    Branch("beq", "store"),
    Label("strong"),
    Ins("00400100", "ori.w #$100, d0"),
    Label("store"),
    Ins("3d400218", "move.w d0, $218(a6)"),
    Ins("1d7c003c0a77", "move.b #$3c, $a77(a6)"),
    JmpAbs(AFTER_DETECT),
]

# Substitui: lea $22af0(pc),a1 / move.b $224(a6),d0 / cmp.b 1(a1),d0
pick_level = [
    Ins("082e00010218", "btst.b #$1, $218(a6)"),
    Branch("beq", "by_gauge"),
    Ins("082e00000218", "btst.b #$0, $218(a6)"),
    Branch("bne", "full"),
    # botão fraco: versão de barra vermelha (id+2), a menos que ela seja a
    # versão de "falha" (custo com bit 7 na tabela $23BA4) -> usa a média (id+1)
    Ins("302d0010", "move.w $10(a5), d0"),
    Ins("5440", "addq.w #$2, d0"),
    Ins("e948", "lsl.w #$4, d0"),
    Ins("43f900023ba4", "lea.l $23ba4.l, a1"),
    Ins("083100070004", "btst.b #$7, $4(a1, d0.w)"),
    Branch("beq", "red"),
    Ins("197c0002005c", "move.b #$2, $5c(a4)"),
    Ins("526d0010", "addq.w #$1, $10(a5)"),
    Branch("bra", "full"),
    Label("red"),
    Ins("197c0001005c", "move.b #$1, $5c(a4)"),
    Ins("546d0010", "addq.w #$2, $10(a5)"),
    Label("full"),
    # botão forte: nível 3 / id+0 já definidos em $1D542
    JmpAbs(LEVEL_DONE),
    Label("by_gauge"),
    # regra original (comandos da IA)
    Ins("43f900022af0", "lea.l $22af0.l, a1"),
    Ins("102e0224", "move.b $224(a6), d0"),
    Ins("b0290001", "cmp.b $1(a1), d0"),
    JmpAbs(GAUGE_CONT),
]

PATCH = Patch(
    id="special-strength-by-button",
    title="Força do especial pelo botão (fraco = barra vermelha, forte = barra cheia)",
    spec="src/backend/specs/SPEC-004-special-strength-by-button.md",
    blocks=[Block("tag_command", tag_command), Block("pick_level", pick_level)],
    hooks=[
        Hook(addr=0x1E102, expect="3d4002181d7c003c0a77", to_block="tag_command"),
        Hook(addr=0x1D548, expect="43fa55a6102e0224b0290001", to_block="pick_level"),
    ],
)
