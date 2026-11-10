"""Robert: LK neutro com startup/recuperacao do LP — SPEC-070."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext,LeaPc,Raw
from charlib import MOVE_RECORD,only,shared_hook
from patchlib import Patch,Block,DataBlock,Data
ANIM=0x22C
FRAMES=[(1,0x10,None),(1,0x18,0x0c23),(8,0x18,0x0c24),
        (1,0,0x0c23),(0,0x80,0x0c22)]
CMD=bytes.fromhex("c70046c701960c22")
def frames(org):
 out=bytearray()
 for k,(duration,flags,piece) in enumerate(FRAMES):
  if piece is None:
   rel=len(FRAMES)*4-(k*4+2)
   out+=bytes([duration,flags])+rel.to_bytes(2,'big')
  else:out+=bytes([duration|0x80,flags])+piece.to_bytes(2,'big')
 return bytes(out)+CMD
record=[
 *only(2,MOVE_RECORD),
 Ins("0c6d00300020","cmpi.w #$30, $20(a5)"),Branch("beq","pick"),
 Ins("0c6d00320020","cmpi.w #$32, $20(a5)"),Branch("bne","out"),
 Label("pick"),LeaPc("lk",0),JmpAbs(0x1D770),
 Label("out"),JmpNext(MOVE_RECORD),
 Label("lk"),Raw("0c0c0000000c00004f30"+f"{ANIM:04x}"+"00000100"),
]
PATCH=Patch(id="standing-lk-frames",title="Robert: LK neutro startup 2 e recuperacao 1, como LP",
 spec="src/backend/specs/SPEC-070-robert-standing-lk-frames.md",
 blocks=[Block("robert_lk_record",record),DataBlock("robert_lk_anim",len(frames(0)),frames)],
 hooks=[shared_hook(MOVE_RECORD,"robert_lk_record")],
 data=[Data(0x50000+ANIM*4,"00000000",lambda addrs:(len(FRAMES)<<24|addrs['robert_lk_anim']).to_bytes(4,'big').hex())])
