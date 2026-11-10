"""John: HK aereo usa rasteira; baixo+HK mantem o aereo original — SPEC-075."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext,LeaPc,Raw
from charlib import MOVE_RECORD,JOHN,only,shared_hook
from patchlib import Patch,Block,DataBlock,Data
ANIM=0x22D
# Poses e tempos do baixo+HK original, sem comandos que alterem o salto.
FRAMES=[(1,0x18,None),(1,0x18,0x02b8),(1,0x18,0x02ba),
        (9,0x18,0x02bb),(8,0,0x02ba),(8,0,0x02b8),
        (8,0,0x02b2),(0,0x80,0x02b2)]
CMD=bytes.fromhex("c70046ca0246043c02b2")
def frames(org):
 out=bytearray()
 for k,(duration,flags,piece) in enumerate(FRAMES):
  if piece is None:out+=bytes([duration,flags])+(len(FRAMES)*4-(k*4+2)).to_bytes(2,'big')
  else:out+=bytes([duration|0x80,flags])+piece.to_bytes(2,'big')
 return bytes(out)+CMD
record=[
 *only(JOHN,MOVE_RECORD),
 Ins("0c6d003b0020","cmpi.w #$3b, $20(a5)"),Branch("bne","out"),
 Ins("082e00010068","btst.b #$1, $68(a6)"),Branch("bne","out"),
 LeaPc("air_sweep",0),JmpAbs(0x1D770),
 Label("out"),JmpNext(MOVE_RECORD),
 # Propriedades da voadora forte do Ryo ($010); somente animacao e do John.
 Label("air_sweep"),Raw("16160000000a0e004b20"+f"{ANIM:04x}"+"00000200"),
]
PATCH=Patch(id="air-heavy-kick-remap",title="John: HK aereo com rasteira; baixo+HK com aereo original",
 spec="src/backend/specs/SPEC-075-john-air-heavy-kick-remap.md",
 blocks=[Block("john_air_hk_record",record),DataBlock("john_air_sweep",len(frames(0)),frames)],
 hooks=[shared_hook(MOVE_RECORD,"john_air_hk_record")],
 data=[Data(0x50000+ANIM*4,"00000000",lambda addrs:(len(FRAMES)<<24|addrs['john_air_sweep']).to_bytes(4,'big').hex())])
