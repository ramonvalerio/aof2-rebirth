"""Mantem corpo atingivel no juggle de Kohou/Hien — SPEC-065."""
from asm68k import Ins,Branch,Label,JmpAbs,LeaPc
from patchlib import Patch,Block,Hook

# Atualizacao nativa das caixas: antes da colisao, uma vez por objeto/frame.
# a6 e o objeto de caixa. Identifica apenas o primeiro filho de corpo.
update=[
 Ins("48e7c0c0","movem.l d0-d1/a0-a1, -(a7)"),
 Ins("41f900109280","lea.l $109280.l, a0"),
 Label("owner"),
 Ins("0c680791006e","cmpi.w #$791, $6e(a0)"),Branch("bcs","next"),
 Ins("0c68079f006e","cmpi.w #$79f, $6e(a0)"),Branch("bhi","next"),
 Ins("4a68006c","tst.w $6c(a0)"),Branch("ble","next"),
 Ins("4aa80018","tst.l $18(a0)"),Branch("ble","next"),
 Ins("0c2800060040","cmpi.b #$6, $40(a0)"),Branch("beq","sprite"),
 Ins("0c2800070040","cmpi.b #$7, $40(a0)"),Branch("bne","next"),
 Label("sprite"),
 Ins("7000","moveq #$0, d0"),Ins("10280003","move.b $3(a0), d0"),
 Ins("e148","lsl.w #$8, d0"),Ins("43f50000","lea.l (a5, d0.w), a1"),
 Ins("10290003","move.b $3(a1), d0"),Branch("beq","next"),
 Ins("b02e0002","cmp.b $2(a6), d0"),Branch("beq","body"),
 Label("next"),
 Ins("b1fc00109280","cmpa.l #$109280, a0"),Branch("bne","done"),
 Ins("41f900109380","lea.l $109380.l, a0"),
 LeaPc("owner",1),Ins("4ed1","jmp (a1)"),
 Label("done"),
 Ins("4cdf0303","movem.l (a7)+, d0-d1/a0-a1"),
 # Original: caixa vazia desliga bit 0; caixa existente segue intacta.
 Ins("4aae0072","tst.l $72(a6)"),Branch("bne","native_bounds"),
 Ins("08ae00000070","bclr.b #$0, $70(a6)"),
 Label("native_bounds"),JmpAbs(0x4408),
 Label("body"),
 # Nunca altera os grupos de alvo nativos nem posicoes/velocidades.
 Ins("4a2e006b","tst.b $6b(a6)"),Branch("beq","done"),
 Ins("0228007e0070","andi.b #$7e, $70(a0)"),
 Ins("08a80007003f","bclr.b #$7, $3f(a0)"),
 Ins("08a900070070","bclr.b #$7, $70(a1)"),
 Ins("1d7c00010070","move.b #$1, $70(a6)"),
 Ins("4aae0072","tst.l $72(a6)"),Branch("bne","done"),
 # Algumas poses de queda nao possuem caixa de corpo. Fornece uma caixa
 # minima 32x48 apenas nesse caso; o motor calcula seus limites no ar.
 Ins("2d7cf81018180072","move.l #$f8101818, $72(a6)"),
 Branch("bra","done"),
]
PATCH=Patch(id="juggle-air-hurtbox",title="Kohou/Hien: alvo em juggle permanece atingivel no alto",
 spec="src/backend/specs/SPEC-065-juggle-air-hurtbox.md",
 blocks=[Block("juggle_body",update)],
 hooks=[Hook(0x43FC,"4aae00726606",to_block="juggle_body")])
