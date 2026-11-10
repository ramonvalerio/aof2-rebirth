"""Robert: dois chutes no dash priorizam o EX, nao Geneikyaku — SPEC-072."""
from asm68k import Ins,Branch,Label,JmpAbs
from charlib import forward_bit
from patchlib import Patch,Block,Hook

pending=[
 Ins("48e7c080","movem.l d0-d1/a0, -(a7)"),
 Ins("0c6e00020062","cmpi.w #$2, $62(a6)"),Branch("bne","out"),
 Ins("302e0218","move.w $218(a6), d0"),Ins("0240007f","andi.w #$7f, d0"),
 Ins("0c400044","cmpi.w #$44, d0"),Branch("bne","out"),
 Ins("102e0068","move.b $68(a6), d0"),Ins("020000a0","andi.b #$a0, d0"),
 Ins("0c0000a0","cmpi.b #$a0, d0"),Branch("bne","out"),
 # Dois chutes durante dash para frente: EX tem prioridade.
 Ins("0c2e00100040","cmpi.b #$10, $40(a6)"),Branch("beq","prefer_ex"),
 # Tambem cobre o frame do segundo toque, antes de entrar no estado 16.
 Ins("4a2e0212","tst.b $212(a6)"),Branch("beq","out"),
 Ins("4a6e0210","tst.w $210(a6)"),Branch("bmi","out"),
 *forward_bit("facing"),
 Ins("012e0213","btst.l d0, $213(a6)"),Branch("beq","out"),
 Ins("012e0069","btst.l d0, $69(a6)"),Branch("beq","out"),
 Ins("082e00000068","btst.b #$0, $68(a6)"),Branch("bne","out"),
 Ins("082e00010068","btst.b #$1, $68(a6)"),Branch("bne","out"),
 Label("prefer_ex"),Ins("426e0218","clr.w $218(a6)"),
 Label("out"),Ins("4cdf0103","movem.l (a7)+, d0-d1/a0"),
 # Reproduz o teste original do especial pendente; so esse conflito e limpo.
 Ins("382e0218","move.w $218(a6), d4"),Branch("beq","normal"),
 JmpAbs(0x1D41E),Label("normal"),JmpAbs(0x1D832),
]
PATCH=Patch(id="dash-ex-input-priority",title="Robert: dash com dois chutes prioriza EX sobre Geneikyaku",
 spec="src/backend/specs/SPEC-072-robert-dash-ex-input-priority.md",
 blocks=[Block("robert_dash_priority",pending)],
 hooks=[Hook(0x1D82A,"382e02186600fbee",to_block="robert_dash_priority")])
