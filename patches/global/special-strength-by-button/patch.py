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
  bit 10 = soco fraco + soco forte juntos ($270 & $50 = $50); só informação:
           a escolha de nível aqui não muda (cai no fraco); usado por patches
           de personagem (ex.: ryo/kououken-three-buttons)
  bit 11 = chute fraco + chute forte juntos ($68 & $A0 = $A0), usado
           por king/moushuukyaku-three-buttons
$1D41E já descarta esses bits (andi.w #$7f). Comandos sem o bit 9 (IA)
seguem a regra original da barra.

O tamanho do projétil é decidido à parte, em $22A5C, pela cópia da barra
$23F feita em $1D7DE. Por isso a escolha também grava em $23F uma barra
equivalente ao nível do botão (snapshot_gauge preserva esse valor).
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

AFTER_DETECT = 0x1E10C   # moveq #0,d0 / rts do detector
LEVEL_DONE = 0x1D676     # continuação comum após escolher o nível
GAUGE_CONT = 0x1D554     # bcc.w do teste original de barra
AFTER_SNAPSHOT = 0x1D7E4 # depois da cópia da barra em $1D7DE

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
    # bit 10 = soco fraco + soco forte juntos ($270 bits 4 + 6, par do tradutor, SPEC-002)
    Ins("2f01", "move.l d1, -(a7)"),
    Ins("122e0270", "move.b $270(a6), d1"),
    Ins("02010050", "andi.b #$50, d1"),
    Ins("0c010050", "cmpi.b #$50, d1"),
    Branch("bne", "save"),
    Ins("00400400", "ori.w #$400, d0"),
    Label("save"),
    # bit 11: os dois chutes (funções bits 5/7), preservado no comando
    # para especiais com três versões mesmo depois de soltar os botões.
    Ins("122e0068", "move.b $68(a6), d1"),
    Ins("020100a0", "andi.b #$a0, d1"),
    Ins("0c0100a0", "cmpi.b #$a0, d1"),
    Branch("bne", "save_kicks"),
    Ins("00400800", "ori.w #$800, d0"),
    Label("save_kicks"),
    Ins("3200", "move.w d0, d1"),
    Ins("02410c00", "andi.w #$c00, d1"),
    Ins("56ee03b3", "sne.b $3b3(a6)"),
    Ins("221f", "move.l (a7)+, d1"),
    Ins("3d400218", "move.w d0, $218(a6)"),
    Ins("1d7c003c0a77", "move.b #$3c, $a77(a6)"),
    JmpAbs(AFTER_DETECT),
]

# Barra "equivalente" gravada em $23F para o tamanho do projétil ($22A5C usa
# $23F com os mesmos limites $20/$40). Bit 7 = valor definido pelo botão;
# a barra real vai no máximo até $78, então o bit 7 nunca aparece nela.
GAUGE_STRONG = 0xC0   # $40 | marca
GAUGE_MEDIUM = 0xA0   # $20 | marca
GAUGE_WEAK = 0x80     # $00 | marca

# Substitui: lea $22af0(pc),a1 / move.b $224(a6),d0 / cmp.b 1(a1),d0
pick_level = [
    Ins("082e00010218", "btst.b #$1, $218(a6)"),
    Branch("beq", "by_gauge"),
    Ins("082e00000218", "btst.b #$0, $218(a6)"),
    Branch("bne", "strong"),
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
    Ins(f"1d7c00{GAUGE_MEDIUM:02x}023f", f"move.b #${GAUGE_MEDIUM:x}, $23f(a6)"),
    Branch("bra", "done"),
    Label("red"),
    Ins("197c0001005c", "move.b #$1, $5c(a4)"),
    Ins("546d0010", "addq.w #$2, $10(a5)"),
    Ins(f"1d7c00{GAUGE_WEAK:02x}023f", f"move.b #${GAUGE_WEAK:x}, $23f(a6)"),
    Branch("bra", "done"),
    Label("strong"),
    # nível 3 / id+0 já definidos em $1D542
    Ins(f"1d7c00{GAUGE_STRONG:02x}023f", f"move.b #${GAUGE_STRONG:x}, $23f(a6)"),
    Label("done"),
    JmpAbs(LEVEL_DONE),
    Label("by_gauge"),
    # regra original (comandos da IA)
    Ins("43f900022af0", "lea.l $22af0.l, a1"),
    Ins("102e0224", "move.b $224(a6), d0"),
    Ins("b0290001", "cmp.b $1(a1), d0"),
    JmpAbs(GAUGE_CONT),
]

# Substitui: move.b $224(a6),$23f(a6) em $1D7DE (cópia da barra antes do custo).
# Se pick_level marcou $23F (bit 7), mantém o valor do botão; senão, original.
# Custo global somente para especiais fortes escolhidos com dois botoes.
# O maximo usa ponto fixo 8.8; dividir as unidades por cinco = 20%.
ex_cost = [
    Ins("0c6d00400020", "cmpi.w #$40, $20(a5)"), Branch("bcs", "cost_out"),
    Ins("0c6d00470020", "cmpi.w #$47, $20(a5)"), Branch("bhi", "cost_out"),
    Ins("0c2e00c0023f", "cmpi.b #$c0, $23f(a6)"), Branch("bne", "cost_out"),
    Ins("48e7c000", "movem.l d0-d1, -(a7)"),
    Ins("4a2e03b3", "tst.b $3b3(a6)"), Branch("beq", "cost_restore"),
    Ins("7000", "moveq #$0, d0"),
    Ins("102e0256", "move.b $256(a6), d0"),
    Ins("7205", "moveq #$5, d1"),
    Ins("80c1", "divu.w d1, d0"),
    Ins("1d400241", "move.b d0, $241(a6)"),
    Label("cost_restore"), Ins("4cdf0003", "movem.l (a7)+, d0-d1"),
    Label("cost_out"),
]
snapshot_gauge = [
    *ex_cost,
    Ins("082e0007023f", "btst.b #$7, $23f(a6)"),
    Branch("beq", "original"),
    Ins("022e007f023f", "andi.b #$7f, $23f(a6)"),
    JmpAbs(AFTER_SNAPSHOT),
    Label("original"),
    Ins("1d6e0224023f", "move.b $224(a6), $23f(a6)"),
    JmpAbs(AFTER_SNAPSHOT),
]

PATCH = Patch(
    id="special-strength-by-button",
    title="Força do especial pelo botão (fraco = barra vermelha, forte = barra cheia)",
    spec="src/backend/specs/SPEC-004-special-strength-by-button.md",
    blocks=[
        Block("tag_command", tag_command),
        Block("pick_level", pick_level),
        Block("snapshot_gauge", snapshot_gauge),
    ],
    hooks=[
        Hook(addr=0x1E102, expect="3d4002181d7c003c0a77", to_block="tag_command"),
        Hook(addr=0x1D548, expect="43fa55a6102e0224b0290001", to_block="pick_level"),
        Hook(addr=0x1D7DE, expect="1d6e0224023f", to_block="snapshot_gauge"),
    ],
)
