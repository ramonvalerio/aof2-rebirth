"""normal-chains (Ryo) — SPEC-018 / SPEC-020.

Normais do Ryo que, ao conectar, cancelam no próximo golpe (chain), como o
special cancel (SPEC-008) faz com especiais:
  baixo B ($38)          -> chute (baixo B / baixo D)         SPEC-018
  soco forte perto ($23) -> B+D (chute baixo, d4 $34)          SPEC-020

Janela de ataque ($1C064, estado 3, a cada frame): o hook fica em $1C066,
depois do "bsr $1BFF4". Para o Ryo ($62 = 1), já conectado ($21B = 0,
zerado no contato em $1D0C4), com o botão pedido apertado agora ($270) ou
guardado ($274, que o hitstop acumula com "or" de $270, $1BFDE):
  $274 & $7070 -> $270 (como a aterrissagem em $1C39E, mais o bit 6, que
  no B+D marca "chute baixo"), zera $274, jsr $1D808 (consome $270:
  $1DC9E/$1DCD4 escolhem o chute). Se começou (flags da volta != Z, o
  mesmo teste do cancel original em $1C0B8; d0 não serve), rearma as
  caixas dos filhos 5/6 (o golpe novo reaproveita o filho já marcado) e
  sai como o cancel ($1C0BA: addq #4,a7 / rts).
Nos outros casos segue o original (btst #4,$3f(a6) e $1C06C).

Bits do byte alto de $270: 5 = chute, 6 = "C segurado" (B+D = chute baixo,
SPEC-002).

Hitstun do baixo B: byte 14 do golpe $00D, $01 -> $02. A SPEC-019 mostrou
que a reação é escolhida por postura/altura/dano ($21314), não por esse
byte; mantido por enquanto (sem efeito confirmado).
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Data, Hook, Patch

RYO = 1
CROUCH_LK = 0x38
CLOSE_HP = 0x23
KICK = 0x20                 # $270 bit 5
LOW_KICK = 0x60             # $270 bits 5 + 6 (B+D)
MOVE_TABLE = 0x023BA4
CROUCH_LK_MOVE = 0x00D
REACTION = 14

chain = [
    Branch("bra", "start"),
    Label("original"),                               # (no começo: desvios curtos)
    Ins("082e0004003f", "btst.b #$4, $3f(a6)"),
    JmpAbs(0x1C06C),
    Label("start"),
    Ins(f"0c6e{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a6)"),
    Branch("bne", "original"),
    Ins("4a2e021b", "tst.b $21b(a6)"),              # ainda não conectou
    Branch("bne", "original"),
    Ins("102e0270", "move.b $270(a6), d0"),         # apertado agora
    Ins("802e0274", "or.b $274(a6), d0"),           # ou guardado
    Ins(f"0c6e{CROUCH_LK:04x}0230", f"cmpi.w #${CROUCH_LK:x}, $230(a6)"),
    Branch("bne", "close_hp"),
    Ins("08000005", "btst.b #$5, d0"),              # baixo B -> chute
    Branch("bne", "go"),
    Branch("bra", "original"),
    Label("close_hp"),
    Ins(f"0c6e{CLOSE_HP:04x}0230", f"cmpi.w #${CLOSE_HP:x}, $230(a6)"),
    Branch("bne", "original"),
    Ins(f"020000{LOW_KICK:02x}", f"andi.b #${LOW_KICK:x}, d0"),   # soco forte perto -> B+D
    Ins(f"0c0000{LOW_KICK:02x}", f"cmpi.b #${LOW_KICK:x}, d0"),
    Branch("bne", "original"),
    Label("go"),
    Ins("302e0274", "move.w $274(a6), d0"),
    Ins("02407070", "andi.w #$7070, d0"),
    Ins("816e0270", "or.w d0, $270(a6)"),
    Ins("426e0274", "clr.w $274(a6)"),
    Ins("4eb90001d808", "jsr $1d808.l"),
    Branch("beq", "none"),                           # flags da volta, como $1C0B8
    Ins("48e780c0", "movem.l d0/a0-a1, -(a7)"),     # como o rearm do SPEC-008
    Ins("7000", "moveq #$0, d0"),
    Ins("102e0003", "move.b $3(a6), d0"),            # sprite do jogador
    Ins("e148", "lsl.w #$8, d0"),
    Ins("41f50000", "lea.l (a5, d0.w), a0"),
    Ins("7000", "moveq #$0, d0"),
    Ins("10280007", "move.b $7(a0), d0"),            # filho 5
    Ins("e148", "lsl.w #$8, d0"),
    Ins("08b500070070", "bclr.b #$7, $70(a5, d0.w)"),
    Ins("7000", "moveq #$0, d0"),
    Ins("10280008", "move.b $8(a0), d0"),            # filho 6
    Ins("e148", "lsl.w #$8, d0"),
    Ins("08b500070070", "bclr.b #$7, $70(a5, d0.w)"),
    Ins("4cdf0301", "movem.l (a7)+, d0/a0-a1"),
    JmpAbs(0x1C0BA),                                 # cancel feito
    Label("none"),
    Ins("4e75", "rts"),
]

PATCH = Patch(
    id="normal-chains",
    title="Ryo: chains ao conectar (baixo B -> chute, soco forte perto -> B+D)",
    spec="src/backend/specs/SPEC-020-ryo-normal-chains.md",
    blocks=[Block("normal_chain", chain)],
    hooks=[
        # $1C066: btst.b #4,$3f(a6)  (segue no bne de $1C06C)
        Hook(addr=0x1C066, expect="082e0004003f", to_block="normal_chain"),
    ],
    data=[
        Data(MOVE_TABLE + CROUCH_LK_MOVE * 16 + REACTION, "01", "02"),
    ],
)
