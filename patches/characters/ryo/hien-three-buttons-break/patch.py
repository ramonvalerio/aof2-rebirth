from asm68k import Branch, Ins, JmpNext, Label
from charlib import MOVE_TABLE, SPECIAL_CHOSEN, only, shared_hook
from patchlib import Block, Data, Patch


def pick(move, level, gauge):
    return [
        Ins(f"3b7c{move:04x}0010", f"move.w #${move:x}, $10(a5)"),
        Ins(f"197c{level:04x}005c", f"move.b #${level:x}, $5c(a4)"),
        Ins(f"1d7c00{gauge:02x}023f", f"move.b #${gauge:x}, $23f(a6)"),
        Branch("bra", "out"),
    ]


choose = [
    *only(1, SPECIAL_CHOSEN),
    Ins("082e00010218", "btst.b #$1, $218(a6)"),
    Branch("beq", "out"),
    Ins("0c6d001b0010", "cmpi.w #$1b, $10(a5)"),
    Branch("bcs", "out"),
    Ins("0c6d001d0010", "cmpi.w #$1d, $10(a5)"),
    Branch("bhi", "out"),
    Ins("422e03b4", "clr.b $3b4(a6)"),
    Ins("422e03b5", "clr.b $3b5(a6)"),
    Ins("082e00030218", "btst.b #$3, $218(a6)"),
    Branch("bne", "strong"),
    Ins("082e00000218", "btst.b #$0, $218(a6)"),
    Branch("bne", "medium"),
    *pick(0x1D, 1, 0x80),
    Label("medium"),
    *pick(0x1C, 2, 0xA0),
    Label("strong"),
    Ins("1d7c000103b4", "move.b #$1, $3b4(a6)"),
    *pick(0x1B, 3, 0xC0)[:-1],
    Label("out"),
    JmpNext(SPECIAL_CHOSEN),
]


# Retorno original do Hien fraco ($147), com lancamento vertical e sem ataque.
FLIP_ANIM=0x11E
FLIP_FRAMES=[(3,0x40,None),(0,0x20,0x061b),(5,0,0x100e),
             (5,0,0x061a),(5,0,0x0619),(5,0,0x0618),
             (0,0,0x0617),(3,0,0x0617),(0,0x80,0x0605)]
FLIP_LAUNCH=bytes.fromhex("d200000bc000ff7000000000061b")
def flip_data(org):
    out=bytearray()
    for k,(duration,flags,value) in enumerate(FLIP_FRAMES):
        if value is None:
            rel=org+len(FLIP_FRAMES)*4-(org+k*4+2)
            out+=bytes([duration,flags])+rel.to_bytes(2,'big')
        else:out+=bytes([duration|0x80,flags])+value.to_bytes(2,'big')
    return bytes(out)+FLIP_LAUNCH

from patchlib import DataBlock
PATCH=Patch(id="hien-three-buttons-break",
 title="Ryo: Hien tres versoes, forte de dois chutes com flip vertical automatico",
 spec="src/backend/specs/SPEC-064-ryo-hien-strong-break.md",
 blocks=[Block("hien_buttons",choose),DataBlock("hien_vertical_flip",len(flip_data(0)),flip_data)],
 hooks=[shared_hook(SPECIAL_CHOSEN,"hien_buttons")],
 data=[Data(0x50000+FLIP_ANIM*4,"00000000",
    lambda addrs:(len(FLIP_FRAMES)<<24|addrs["hien_vertical_flip"]).to_bytes(4,'big').hex())])
