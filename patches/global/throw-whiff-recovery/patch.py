"""Tentativa de grab vazia com recuperacao vulneravel — SPEC-066."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext,LeaPc,Raw
from charlib import MOVE_RECORD,ATTACK_WINDOW,shared_hook
from patchlib import Patch,Block,DataBlock,Data,Hook

# Poses iniciais nativas do grab, sem executar comandos de arremesso.
POSES=[(0x652,0x653),(0xb86,0xb87),(0x45d,0x45d),(0x491,0x491),
       (0xb07,0xb07),(0x70c,0x70d),(0x36a,0x36a),(0x2fe,0x2ff),
       (0xca9,0xcaa),(0x9b9,0x9ba),(0xa66,0xa66),(0x220,0x221),
       (0x5cf,0x5d0)]
ANIMS=[0x11f,0x12f,0x196,0x197,0x19a,0x19e,0x19f,
       0x1f4,0x1f5,0x21f,0x229,0x22a,0x22b]
FIELD=0x3B6  # 1 armando registro; 2 recuperacao da tentativa vazia.

attempt=[
 Ins("082e00060271","btst.b #$6, $271(a6)"),Branch("beq","native"),
 # Sucesso nativo descarta este retorno via $1DB06 e vai direto ao ataque;
 # somente a falha volta aqui. Nao empilha registradores antes da chamada.
 Ins("4eb90001dabe","jsr $1dabe.l"),
 Ins("082e00040060","btst.b #$4, $60(a6)"),Branch("bne","native"),
 Ins("4a6e006c","tst.w $6c(a6)"),Branch("ble","native"),
 Ins("0c6e00010062","cmpi.w #$1, $62(a6)"),Branch("bcs","native"),
 Ins("0c6e000d0062","cmpi.w #$d, $62(a6)"),Branch("bhi","native"),
 Ins("7000","moveq #$0, d0"),Ins("102e0040","move.b $40(a6), d0"),
 Ins("0c000002","cmpi.b #$2, d0"),Branch("bls","start"),
 Ins("0c00000d","cmpi.b #$d, d0"),Branch("beq","start"),
 Ins("0c00000e","cmpi.b #$e, d0"),Branch("beq","start"),
 Label("native"),JmpAbs(0x1D842),
 Label("start"),
 Ins("1d7c000103b6","move.b #$1, $3b6(a6)"),
 Ins("426e0270","clr.w $270(a6)"),Ins("426e0274","clr.w $274(a6)"),
 Ins("426e0218","clr.w $218(a6)"),
 Ins("7820","moveq #$20, d4"),Ins("4eb90001d41e","jsr $1d41e.l"),
 Branch("bne","started"),
 Ins("422e03b6","clr.b $3b6(a6)"),Branch("bra","native"),
 Label("started"),Ins("4e75","rts"),
]

record=[
 Ins("0c2e000103b6","cmpi.b #$1, $3b6(a6)"),Branch("beq","pick"),
 Ins("422e03b6","clr.b $3b6(a6)"),JmpNext(MOVE_RECORD),
 Label("pick"),Ins("1d7c000203b6","move.b #$2, $3b6(a6)"),
 Ins("302e0062","move.w $62(a6), d0"),Ins("5340","subq.w #$1, d0"),
 Ins("e948","lsl.w #$4, d0"),LeaPc("records",0),
 Ins("41f00000","lea.l (a0, d0.w), a0"),JmpAbs(0x1D770),
 Label("records"),
 Raw(''.join('00000000000000000030'+f'{aid:04x}'+'00001000' for aid in ANIMS)),
]
window=[
 Ins("0c2e000203b6","cmpi.b #$2, $3b6(a6)"),Branch("beq","locked"),
 JmpNext(ATTACK_WINDOW),
 Label("locked"),
 Ins("426e0218","clr.w $218(a6)"),Ins("426e0274","clr.w $274(a6)"),
 JmpAbs(0x1C0B2),
]
def anim(poses):
 return b''.join(bytes([0x80|d,f])+v.to_bytes(2,'big')
                 for d,f,v in [(6,0,poses[0]),(12,0,poses[1]),(0,0x80,poses[0])])
PATCH=Patch(id="throw-whiff-recovery",title="Grab errado mostra tentativa e deixa 18 frames vulneravel",
 spec="src/backend/specs/SPEC-066-throw-whiff-recovery.md",
 blocks=[Block("grab_attempt",attempt),Block("grab_record",record),Block("grab_window",window)]+
        [DataBlock(f"grab_pose_{c}",12,lambda org,poses=poses:anim(poses)) for c,poses in enumerate(POSES,1)],
 hooks=[Hook(0x1D836,"082e0006027167046100027e",to_block="grab_attempt"),
        shared_hook(MOVE_RECORD,"grab_record"),shared_hook(ATTACK_WINDOW,"grab_window")],
 data=[Data(0x50000+aid*4,"00000000",lambda addrs,c=c:(0x03000000|addrs[f"grab_pose_{c}"]).to_bytes(4,'big').hex())
       for c,aid in enumerate(ANIMS,1)])
