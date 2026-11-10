"""Ryo: tres Zanretsuken com finais HP/gancho/HK juggle — SPEC-079."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext,LeaPc,Raw
from charlib import RYO,SPECIAL_CHOSEN,CMD_STEP,only,shared_hook,HIT_SOUND,ANIM_FRAME,rearm_children
from patchlib import Patch,Block,Hook,Data,DataBlock

def pick(mid,level,gauge,variant):
 return [Ins(f"3b7c{mid:04x}0010",f"move.w #${mid:x}, $10(a5)"),
         Ins(f"197c{level:04x}005c",f"move.b #${level:x}, $5c(a4)"),
         Ins(f"1d7c{gauge:04x}023f",f"move.b #${gauge:x}, $23f(a6)"),
         Ins(f"1d7c{variant:04x}03c2",f"move.b #${variant:x}, $3c2(a6)"),Branch("bra","out")]
choose=[
 *only(RYO,SPECIAL_CHOSEN),Ins("422e03c2","clr.b $3c2(a6)"),
 Ins("082e00010218","btst.b #$1, $218(a6)"),Branch("beq","out"),
 Ins("0c6d001e0010","cmpi.w #$1e, $10(a5)"),Branch("bcs","out"),
 Ins("0c6d00200010","cmpi.w #$20, $10(a5)"),Branch("bhi","out"),
 Ins("082e00020218","btst.b #$2, $218(a6)"),Branch("bne","ex"),
 Ins("082e00000218","btst.b #$0, $218(a6)"),Branch("bne","strong"),
 *pick(0x1f,1,0x80,1),Label("strong"),*pick(0x1e,3,0xc0,2),
 Label("ex"),*pick(0x1e,3,0xc0,3)[:-1],Label("out"),JmpNext(SPECIAL_CHOSEN),
]
command=[
 *only(RYO,CMD_STEP),Ins("0c450044","cmpi.w #$44, d5"),Branch("bne","out"),
 Ins("0c44049a","cmpi.w #$49a, d4"),Branch("bne","out"),
 Ins("020000bf","andi.b #$bf, d0"),Label("out"),JmpNext(CMD_STEP),
]
sequence=[
 Ins("3228000a","move.w $a(a0), d1"),
 Ins("0c6e00010062","cmpi.w #$1, $62(a6)"),Branch("bne","original"),
 Ins("0c6d00440020","cmpi.w #$44, $20(a5)"),Branch("bne","original"),
 Ins("0c2e000103c2","cmpi.b #$1, $3c2(a6)"),Branch("beq","weak"),
 Ins("0c2e000303c2","cmpi.b #$3, $3c2(a6)"),Branch("beq","ex"),
 Label("original"),Ins("4a41","tst.w d1"),Branch("bmi","native_sequence"),JmpAbs(0x1D756),
 Label("native_sequence"),JmpAbs(0x1D740),
 Label("weak"),LeaPc("weak_seq",0),Branch("bra","setup"),
 Label("ex"),LeaPc("ex_seq",0),
 Label("setup"),Ins("3218","move.w (a0)+, d1"),Ins("2948004c","move.l a0, $4c(a4)"),JmpAbs(0x1D756),
 Label("weak_seq"),Raw("414e813f81488148814981498149814a814a814a814b814b814b814c814c814c023a"),Label("ex_seq"),Raw("414e813f8148814881488149814981498149814a814a814a814a814b814b814b814b814c814c814c814c023b"),
]
WEAK=0x23A
EX=0x23B
# DE encerra o modo de golpes extras; DD muda a reacao antes do unico final.
WEAK_FRAMES=[(2,0x18,None),(2,0x18,0x626),(6,0x18,0x627),(8,0,0x626),(8,0,0x62a),(0,0x80,0x62a)]
EX_FRAMES=[(2,0x10,None),(3,0x18,0x636),(8,0x18,0x637),(10,0,0x638),(10,0,0x639),(0,0x80,0x639)]
WEAK_CMD=bytes.fromhex("dedd00c70044c70172062a")
# Som de movimento do chute; impacto $0140 do Hien e aplicado no contato.
EX_CMD=bytes.fromhex("dedd00c70046c701720635ec010636")
# Marca o efeito no contato: a reacao do defensor pode ocorrer apos a troca
# de quadro/animacao do atacante. Nao depender de $6E nesse despacho tardio.
impact=[
 Ins("0c6800010062","cmpi.w #$1, $62(a0)"),Branch("bne","out"),
 Ins("0c6800440230","cmpi.w #$44, $230(a0)"),Branch("bne","out"),
 Ins("0c28000303c2","cmpi.b #$3, $3c2(a0)"),Branch("bne","out"),
 # $6E conserva $414E (inicio da sequencia); $54 do sprite acompanha o final.
 Ins("48e78040","movem.l d0/a1, -(a7)"),
 Ins("7000","moveq #$0, d0"),Ins("10280003","move.b $3(a0), d0"),
 Ins("e148","lsl.w #$8, d0"),Ins("43f50000","lea.l (a5, d0.w), a1"),
 Ins("0c69023b0054","cmpi.w #$23b, $54(a1)"),
 Ins("4cdf0201","movem.l (a7)+, d0/a1"),Branch("bne","out"),
 Ins("700f","moveq #$f, d0"),Ins("c02e007c","and.b $7c(a6), d0"),
 Ins("0c000003","cmpi.b #$3, d0"),Branch("beq","out"),
 Ins("08ee0007024b","bset.b #$7, $24b(a6)"),
 Ins("3d7c01400a5e","move.w #$140, $a5e(a6)"),
 Label("out"),JmpNext(HIT_SOUND)]
# Entrada do final: liberar uma unica pancada e rearmar suas caixas.
# a6 e sprite neste hook; o ator fica em a5 + parent*256 - $80.
final_frame=[Ins("48e78080","movem.l d0/a0, -(a7)"),
 Ins("7000","moveq #$0, d0"),Ins("102e000b","move.b $b(a6), d0"),
 Ins("e148","lsl.w #$8, d0"),Ins("41f50080","lea.l -$80(a5, d0.w), a0"),
 Ins("0c6800010062","cmpi.w #$1, $62(a0)"),Branch("bne","out"),
 Ins("0c6800440230","cmpi.w #$44, $230(a0)"),Branch("bne","out"),
 Ins("0c28000303c2","cmpi.b #$3, $3c2(a0)"),Branch("bne","out"),
 Ins("0c6e023b0054","cmpi.w #$23b, $54(a6)"),Branch("bne","out"),
 Ins("4a2e005a","tst.b $5a(a6)"),Branch("bne","out"),
 Ins("117c000103aa","move.b #$1, $3aa(a0)"),
 Ins("41d6","lea.l (a6), a0"),*rearm_children(),
 Label("out"),Ins("4cdf0101","movem.l (a7)+, d0/a0"),JmpNext(ANIM_FRAME)]

def animation(frames,stream,org):
 out=bytearray()
 for k,(duration,flags,piece) in enumerate(frames):
  if piece is None:out+=bytes([duration,flags])+(len(frames)*4-(k*4+2)).to_bytes(2,'big')
  else:out+=bytes([duration|0x80,flags])+piece.to_bytes(2,'big')
 return bytes(out)+stream
PATCH=Patch(id="zanretsuken-three-buttons",title="Ryo: Zanretsuken fraco HP, forte gancho, EX tras+HK com estalo e juggle",
 spec="src/backend/specs/SPEC-079-ryo-zanretsuken-three-buttons.md",
 blocks=[Block("zan_buttons",choose),Block("zan_pair_input",command),Block("zan_sequence",sequence),Block("zan_ex_impact",impact),Block("zan_ex_frame",final_frame),
         DataBlock("zan_weak_end",len(animation(WEAK_FRAMES,WEAK_CMD,0)),lambda org:animation(WEAK_FRAMES,WEAK_CMD,org)),
         DataBlock("zan_ex_end",len(animation(EX_FRAMES,EX_CMD,0)),lambda org:animation(EX_FRAMES,EX_CMD,org))],
 hooks=[shared_hook(HIT_SOUND,"zan_ex_impact"),shared_hook(ANIM_FRAME,"zan_ex_frame"),shared_hook(SPECIAL_CHOSEN,"zan_buttons"),shared_hook(CMD_STEP,"zan_pair_input"),
        Hook(0x1D73A,"3228000a6a16",to_block="zan_sequence")],
 data=[Data(0x50000+WEAK*4,"00000000",lambda addrs:(len(WEAK_FRAMES)<<24|addrs['zan_weak_end']).to_bytes(4,'big').hex()),
       Data(0x50000+EX*4,"00000000",lambda addrs:(len(EX_FRAMES)<<24|addrs['zan_ex_end']).to_bytes(4,'big').hex())])
