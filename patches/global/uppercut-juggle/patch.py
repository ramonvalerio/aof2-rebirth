"""Uppercut anti-aéreo abre juggle global — SPEC-043.

Intercepta o efeito somente nos comandos $24/$26, contra alvo vivo no ar.
Usa a reação aérea comum, sem a animação de queda/som de grito. As poses
de cada defensor têm animações próprias para manter a janela de combo.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Data, DataBlock, Hook, Patch

ANIM_BASE = 0x780  # $781..$78F: entradas vazias, uma por defensor.
# Peças das três poses de reação aérea de cada personagem (inclui chefes).
POSES = [
    (0x659, 0x65A, 0x65B), (0xBB2, 0xBB3, 0xBB4),
    (0x428, 0x429, 0x42A), (0x50B, 0x50C, 0x50D),
    (0xB3F, 0xB40, 0xB41), (0x71F, 0x720, 0x721),
    (0x37F, 0x380, 0x381), (0x2D5, 0x2D6, 0x2D7),
    (0xC7B, 0xC7C, 0xC7D), (0xA09, 0xA0A, 0xA0B),
    (0x140, 0x141, 0x142), (0x22E, 0x22F, 0x230),
    (0x5AF, 0x5B0, 0x5B1), (0xA8D, 0xA88, 0xA88),
    (0xACA, 0xAC5, 0xAC5),
]


FALL_POSES=[(0x65f,0x660,0x661),(0xbb8,0xbb9,0xbba),(0x42b,0x42c,0x42d),
 (0x503,0x504,0x505),(0xb38,0xb39,0xb3a),(0x91a,0x91b,0x91c),
 (0x3c3,0x3c4,0x3c5),(0x2d8,0x2d9,0x2da),(0xc7b,0xc7e,0xc7f),
 (0xa0c,0xa0d,0xa0e),(0x143,0x144,0x145),(0x231,0x232,0x233),
 (0x5b7,0x5b5,0x5b6),(0xa92,0xa93,0xa93),(0xa96,0xa97,0xa97)]


def animation(poses):
    return b"".join(bytes((0x80 | duration, flags)) + pose.to_bytes(2, "big")
                    for duration, flags, pose in
                    [(36, 0, poses[0]), (3, 0, poses[1]),
                     (3, 0, poses[2]), (0, 0x80, poses[2])])


reaction = [
    Ins("0c6800010062", "cmpi.w #$1, $62(a0)"), Branch("bne", "normal_uppercut"),
    Ins("0c6800470230", "cmpi.w #$47, $230(a0)"), Branch("bne", "normal_uppercut"),
    Ins("0c28000303b4", "cmpi.b #$3, $3b4(a0)"), Branch("beq", "candidate"),
    Label("normal_uppercut"),
    Ins("0c6800240230", "cmpi.w #$24, $230(a0)"),
    Branch("beq", "uppercut"),
    Ins("0c6800260230", "cmpi.w #$26, $230(a0)"),
    Branch("bne", "original"),
    Label("uppercut"),
    Ins("4aae0018", "tst.l $18(a6)"),
    Branch("ble", "original"),
    Label("candidate"),
    Ins("4a6e006c", "tst.w $6c(a6)"),
    Branch("ble", "original"),
    Ins("082e0002003f", "btst.b #$2, $3f(a6)"),
    Branch("bne", "original"),
    Ins("0c6e00010062", "cmpi.w #$1, $62(a6)"),
    Branch("bcs", "original"),
    Ins("0c6e000f0062", "cmpi.w #$f, $62(a6)"),
    Branch("bhi", "original"),
    Ins("700f", "moveq #$f, d0"),
    Ins("c02e007c", "and.b $7c(a6), d0"),
    Ins("0c000003", "cmpi.b #$3, d0"),
    Branch("beq", "original"),
    Branch("bra", "launch"),
    Label("original"),
    Ins("7000", "moveq #$0, d0"),
    Ins("08ae0007024b", "bclr.b #$7, $24b(a6)"),
    JmpAbs(0x2134C),
    Label("launch"),
    # Mesmo desenrolamento de pilha dos efeitos especiais originais:
    # sai de $21344 E $21314; evita o segundo despacho de reação em $205F2.
    Ins("508f", "addq.l #$8, a7"),
    Ins("7221", "moveq #$21, d1"),
    Ins("4eb900020604", "jsr $20604.l"),
    Ins("302e0062", "move.w $62(a6), d0"),
    Ins("06400780", "addi.w #$780, d0"),
    Ins("0c6800470230", "cmpi.w #$47, $230(a0)"), Branch("bne", "pose_selected"),
    Ins("06400010", "addi.w #$10, d0"),
    Label("pose_selected"),
    Ins("3d40006e", "move.w d0, $6e(a6)"),
    Ins("08ae0007003f", "bclr.b #$7, $3f(a6)"),
    Ins("022e007e0070", "andi.b #$7e, $70(a6)"),
    Ins("08ee00040060", "bset.b #$4, $60(a6)"),
    Ins("1d7c00010268", "move.b #$1, $268(a6)"),
    Ins("42ae0020", "clr.l $20(a6)"),
    Ins("426e0030", "clr.w $30(a6)"),
    Ins("426e0034", "clr.w $34(a6)"),
    Ins("203c00060000", "move.l #$60000, d0"),
    Ins("0c6e0791006e", "cmpi.w #$791, $6e(a6)"), Branch("bcs", "velocity_selected"),
    Ins("203c000c0000", "move.l #$c0000, d0"),
    Label("velocity_selected"),
    Ins("2d400028", "move.l d0, $28(a6)"),
    Ins("29400028", "move.l d0, $28(a4)"),
    Ins("3d7cff800038", "move.w #$ff80, $38(a6)"),
    Ins("422e024b", "clr.b $24b(a6)"),
    Ins("4e75", "rts"),
]

# $1C520 normalmente encerra a reação quando a animação acaba, mesmo no ar.
# A animação identifica o juggle sem reservar RAM: outro acerto troca $6E.
hold_air = [
    Ins("0c6e0781006e", "cmpi.w #$781, $6e(a6)"),
    Branch("bcs", "release"),
    Ins("0c6e079f006e", "cmpi.w #$79f, $6e(a6)"),
    Branch("bhi", "release"),
    Ins("4a6e006c", "tst.w $6c(a6)"),
    Branch("ble", "release"),
    Ins("4aae0018", "tst.l $18(a6)"),
    Branch("ble", "land"),
    # Continua a física, inclusive a rotina original de aterrissagem.
    Ins("4eb90001c6ca", "jsr $1c6ca.l"),
    Ins("4e75", "rts"),
    Label("land"),
    # A volta direta pelo fim da reação não passa em $1C374, onde a
    # aterrissagem normal limpa $240 e $60 bit 7 (trava de ataques).
    # Também resolve altura exatamente zero, sem esperar um frame negativo.
    Ins("42ae0018", "clr.l $18(a6)"),
    Ins("42ae0020", "clr.l $20(a6)"),
    Ins("42ae0028", "clr.l $28(a6)"),
    Ins("42ac0028", "clr.l $28(a4)"),
    Ins("426e0030", "clr.w $30(a6)"),
    Ins("426e0034", "clr.w $34(a6)"),
    Ins("422e0240", "clr.b $240(a6)"),
    Ins("08ae00070060", "bclr.b #$7, $60(a6)"),
    Ins("08ae00040060", "bclr.b #$4, $60(a6)"),
    Label("release"),
    Ins("426c0060", "clr.w $60(a4)"),
    Ins("4a6e006c", "tst.w $6c(a6)"),
    JmpAbs(0x1C528),
]

PATCH = Patch(
    id="uppercut-juggle",
    title="Uppercut anti-aéreo permite continuar o combo (global)",
    spec="src/backend/specs/SPEC-043-uppercut-juggle.md",
    blocks=[Block("uppercut_reaction", reaction), Block("hold_air", hold_air)] + [
        DataBlock(f"air_pose_{char}", 16, lambda org, poses=poses: animation(poses))
        for char, poses in enumerate(POSES, 1)
    ] + [DataBlock(f"kohou_fall_{char}",16,lambda org,poses=poses:animation(poses))
         for char,poses in enumerate(FALL_POSES,1)],
    hooks=[
        Hook(0x21344, "700008ae0007024b", to_block="uppercut_reaction"),
        Hook(0x1C520, "426c00604a6e006c", to_block="hold_air"),
    ],
    data=[Data(0x50000 + (ANIM_BASE + char) * 4, "00000000",
               lambda addrs, char=char:
               (0x04000000 | addrs[f"air_pose_{char}"]).to_bytes(4, "big").hex())
          for char in range(1, 16)] + [
        Data(0x50000+(0x790+char)*4,"00000000",
             lambda addrs,char=char:(0x04000000|addrs[f"kohou_fall_{char}"]).to_bytes(4,"big").hex())
        for char in range(1,16)],
)
