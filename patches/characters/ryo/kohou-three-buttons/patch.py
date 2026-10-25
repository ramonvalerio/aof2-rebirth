"""Ryo: tres versoes do Kohou — SPEC-062."""
from asm68k import Branch, Ins, JmpAbs, JmpNext, Label, LeaPc
from charlib import RYO, SPECIAL_CHOSEN, CMD_STEP, MOVE_TABLE, ATTACK_STATE, HIT_SOUND, only, shared_hook, player_sprite, rearm_children
from patchlib import Block, Data, Hook, Patch
choose = [
    *only(RYO, SPECIAL_CHOSEN),
    Ins("082e00010218", "btst.b #$1, $218(a6)"), Branch("beq", "out"),
    Ins("0c6d00230010", "cmpi.w #$23, $10(a5)"), Branch("bcs", "out"),
    Ins("0c6d00250010", "cmpi.w #$25, $10(a5)"), Branch("bhi", "out"),
    Ins("422e03b4", "clr.b $3b4(a6)"),
    Ins("422e03b5", "clr.b $3b5(a6)"),
    Ins("3b7c00230010", "move.w #$23, $10(a5)"),
    Ins("197c0003005c", "move.b #$3, $5c(a4)"),
    Ins("1d7c00c0023f", "move.b #$c0, $23f(a6)"),
    Ins("082e00020218", "btst.b #$2, $218(a6)"), Branch("beq", "single"),
    Ins("1d7c000103b4", "move.b #$1, $3b4(a6)"), Branch("bra", "out"),
    Label("single"),
    Ins("526d0010", "addq.w #$1, $10(a5)"),
    Ins("197c0001005c", "move.b #$1, $5c(a4)"),
    Ins("1d7c0080023f", "move.b #$80, $23f(a6)"),
    Ins("082e00000218", "btst.b #$0, $218(a6)"), Branch("beq", "out"),
    Ins("526d0010", "addq.w #$1, $10(a5)"),
    Ins("197c0002005c", "move.b #$2, $5c(a4)"),
    Ins("1d7c00a0023f", "move.b #$a0, $23f(a6)"),
    Label("out"), JmpNext(SPECIAL_CHOSEN),
]
command = [
    *only(RYO, CMD_STEP),
    Ins("0c450047", "cmpi.w #$47, d5"), Branch("bne", "out"),
    Ins("0c440268", "cmpi.w #$268, d4"), Branch("beq", "punch"),
    Ins("0c440258", "cmpi.w #$258, d4"), Branch("beq", "diagonal"),
    Ins("0c440260", "cmpi.w #$260, d4"), Branch("bne", "out"),
    Label("diagonal"),
    # Frente ja registrada: baixo-frente com soco/par conclui o DP.
    Ins("0c01005a", "cmpi.b #$5a, d1"), Branch("beq", "complete"),
    Ins("0c01001a", "cmpi.b #$1a, d1"), Branch("bne", "out"),
    Label("complete"), JmpAbs(0x1E0E0),
    Label("punch"),
    # O passo final real e $268 (F0/10), nao $260 (FF/0A).
    Ins("020000bf", "andi.b #$bf, d0"),
    Label("out"), JmpNext(CMD_STEP),
]

# Conta somente acertos reais do Kohou forte. Segundo contato abre o cancel.
contact = [
    Ins("0c6800010062", "cmpi.w #$1, $62(a0)"), Branch("bne", "out"),
    Ins("0c6800470230", "cmpi.w #$47, $230(a0)"), Branch("beq", "break_move"),
    Ins("0c6800430230", "cmpi.w #$43, $230(a0)"), Branch("bne", "out"),
    Label("break_move"),
    Ins("4a2803b4", "tst.b $3b4(a0)"), Branch("beq", "out"),
    Ins("700f", "moveq #$f, d0"), Ins("c02e007c", "and.b $7c(a6), d0"),
    Ins("0c000003", "cmpi.b #$3, d0"), Branch("beq", "blocked"),
    Ins("522803b4", "addq.b #$1, $3b4(a0)"), Branch("bra", "out"),
    Label("blocked"), Ins("422803b4", "clr.b $3b4(a0)"),
    Label("out"), JmpNext(HIT_SOUND),
]

cancel = [
    *only(RYO, ATTACK_STATE),
    Ins("0c6e00470230", "cmpi.w #$47, $230(a6)"), Branch("beq", "break_move"),
    Ins("0c6e00430230", "cmpi.w #$43, $230(a6)"), Branch("bne", "pass"),
    Label("break_move"),
    Ins("0c2e000303b4", "cmpi.b #$3, $3b4(a6)"), Branch("bne", "pass"),
    Ins("4a2e03b5", "tst.b $3b5(a6)"), Branch("beq", "pass"),
    Ins("206e0064", "movea.l $64(a6), a0"),
    Ins("4a68006c", "tst.w $6c(a0)"), Branch("ble", "pass"),
    Branch("bra", "perform"),
    Label("pass"), JmpNext(ATTACK_STATE),
    Label("perform"),
    Ins("422e03b4", "clr.b $3b4(a6)"),
    Ins("422e03b5", "clr.b $3b5(a6)"),
    Ins("426e0274", "clr.w $274(a6)"),
    Ins("426e0218", "clr.w $218(a6)"),
    Ins("2d7c000700000028", "move.l #$70000, $28(a6)"),
    Ins("297c000700000028", "move.l #$70000, $28(a4)"),
    Ins("3d7cff700038", "move.w #$ff70, $38(a6)"),
    Ins("206e0064", "movea.l $64(a6), a0"),
    Ins("3d7c017c006e", "move.w #$17c, $6e(a6)"),
    Ins("0c6e00430230", "cmpi.w #$43, $230(a6)"), Branch("beq", "hien_return"),
    Ins("217c000800000028", "move.l #$80000, $28(a0)"),
    Ins("317cffc00038", "move.w #$ffc0, $38(a0)"),
    LeaPc("return_pose",1), Ins("4ed1", "jmp (a1)"),
    Label("hien_return"),
    # Hien: flip de retorno no mesmo X, sem o impulso horizontal para tras.
    Ins("3d7c011e006e", "move.w #$11e, $6e(a6)"),
    Ins("42ae0020", "clr.l $20(a6)"),
    Ins("42ac0020", "clr.l $20(a4)"),
    Ins("426e0030", "clr.w $30(a6)"),
    Ins("426e0034", "clr.w $34(a6)"),
    Ins("422e0247", "clr.b $247(a6)"),
    # Restauracao do relancamento do cancel manual do Hien.
    Ins("217c000800000028", "move.l #$80000, $28(a0)"),
    Ins("317cffc00038", "move.w #$ffc0, $38(a0)"),
    Ins("08a80007003f", "bclr.b #$7, $3f(a0)"),
    Ins("0228007e0070", "andi.b #$7e, $70(a0)"),
    Ins("08e800040060", "bset.b #$4, $60(a0)"),
    Ins("117c00010268", "move.b #$1, $268(a0)"),
    Ins("117c00070040", "move.b #$7, $40(a0)"),
    Ins("42280041", "clr.b $41(a0)"),
    Ins("42280a69", "clr.b $a69(a0)"),
    Ins("4228024b", "clr.b $24b(a0)"),
    Ins("42a80020", "clr.l $20(a0)"),
    Ins("42680030", "clr.w $30(a0)"),
    Ins("42680034", "clr.w $34(a0)"),
    Ins("30280062", "move.w $62(a0), d0"),
    Ins("06400790", "addi.w #$790, d0"),
    Ins("3140006e", "move.w d0, $6e(a0)"),
    Ins("7000", "moveq #$0, d0"),
    Ins("10280003", "move.b $3(a0), d0"),
    Ins("e148", "lsl.w #$8, d0"),
    Ins("43f50000", "lea.l (a5, d0.w), a1"),
    Ins("137c00010042", "move.b #$1, $42(a1)"),
    Label("return_pose"),
    Ins("197c00010042", "move.b #$1, $42(a4)"),
    Ins("422e0240", "clr.b $240(a6)"),
    Ins("022e006f0060", "andi.b #$6f, $60(a6)"),
    Ins("08ee00040060", "bset.b #$4, $60(a6)"),
    JmpAbs(0x1C208),
]


# Segundo contato tem quadro proprio: rearme na troca REAL de quadro,
# nao no estado do jogador (a animacao continua sendo atualizada no sprite).
rearm = [
    Ins("2d480050", "move.l a0, $50(a6)"),
    Ins("08ee0007005e", "bset.b #$7, $5e(a6)"),
    Ins("0c6e017b0054", "cmpi.w #$17b, $54(a6)"), Branch("bne", "out"),
    Ins("0c2e0003005a", "cmpi.b #$3, $5a(a6)"), Branch("bne", "out"),
    Ins("48e78080", "movem.l d0/a0, -(a7)"),
    Ins("41d6", "lea.l (a6), a0"), *rearm_children(),
    Ins("4cdf0101", "movem.l (a7)+, d0/a0"),
    Label("out"), JmpAbs(0x4A8E),
]
FRAME_LIST = 0x51DBC
NEW_ANIM = 0x17B
# Primeiro/segundo contato no chao; terceiro na subida. O segundo abre
# o break; sem pedido, o lançamento original segue e termina derrubando.
FRAMES = [(2,0x10,0x1141),(2,0x10,0x1142),(5,0x10,0x1143),
          (1,0x10,0x1143),(0,0x30,0x51ded),(22,0,0x0ae9),
          (4,0,0x0ae8),(6,0,0x0aec),(6,0,0x0aea),
          (0,0,0x0aeb),(6,0,0x5365a),(0,0x80,0x0605)]
frames=bytearray()
for k,(duration,flags,value) in enumerate(FRAMES):
    if value>0xffff:
        rel=value-(FRAME_LIST+k*4+2)
        assert -32768<=rel<=32767
        frames+=bytes([duration,flags])+(rel&0xffff).to_bytes(2,'big')
    else:
        frames+=bytes([duration|0x80,flags])+value.to_bytes(2,'big')

BREAK_LIST=0x51C94
BREAK_FRAMES=[(6,0,0x0ae9),(6,0,0x0aec),(6,0,0x0aea),
              (0,0,0x0aeb),(2,0,0x5365a),(0,0x80,0x0605)]
break_frames=bytearray()
for k,(duration,flags,value) in enumerate(BREAK_FRAMES):
    if value>0xffff:
        rel=value-(BREAK_LIST+k*4+2)
        assert -32768<=rel<=32767
        break_frames+=bytes([duration,flags])+(rel&0xffff).to_bytes(2,'big')
    else:
        break_frames+=bytes([duration|0x80,flags])+value.to_bytes(2,'big')

PATCH = Patch(id="kohou-three-buttons", title="Ryo: Kohou LP fraco, HP medio, LP+HP forte",
    spec="src/backend/specs/SPEC-062-ryo-kohou-three-buttons.md",
    blocks=[Block("kohou_buttons", choose), Block("kohou_pair_command", command), Block("kohou_cancel", cancel), Block("kohou_contacts", contact), Block("kohou_frame_rearm", rearm)],
    hooks=[shared_hook(SPECIAL_CHOSEN,"kohou_buttons"), shared_hook(CMD_STEP,"kohou_pair_command"), shared_hook(ATTACK_STATE,"kohou_cancel"), shared_hook(HIT_SOUND,"kohou_contacts"), Hook(0x4A84,"2d48005008ee0007005e",to_block="kohou_frame_rearm")],
    data=[# Lancamento exclusivo: sobe reto, sem ataque antes do terceiro.
          Data(0x51ded,"00"*21,"deebdd01c7003ed20c000cc000ff70000000000ae9"),
          Data(BREAK_LIST,"00"*len(break_frames),break_frames.hex()),
          Data(0x50000+0x17c*4,"00000000",(len(BREAK_FRAMES)<<24|BREAK_LIST).to_bytes(4,'big').hex()),
          Data(FRAME_LIST,"00"*len(frames),frames.hex()),
          Data(0x50000+NEW_ANIM*4,"00000000",(len(FRAMES)<<24|FRAME_LIST).to_bytes(4,'big').hex()),
          Data(MOVE_TABLE+0x23*16+10,"0145",f"{NEW_ANIM:04x}"),
          Data(MOVE_TABLE+0x25*16,"10100000a41001004f30012100000100",
              "0909030300100b004f30014500001000")])
