"""HP+HK no ar para todo o elenco — SPEC-076."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext,LeaPc,Raw
from charlib import MOVE_RECORD,shared_hook
from patchlib import Patch,Block

# Copias dos golpes HP+HK nativos ($34) de cada personagem, com propriedade
# alta $4B20 para uso aereo. Animacoes/dano/reacoes originais preservados.
RECORDS = [
    "0c0c0000001015004b20013300000300",
    "0c0c0000001015004b2001b300000300",
    "0c0c0000001015004b20023300000300",
    "1c1c0000001616004b2002b700000200",
    "0c0c0000000f00004b20033900000100",
    "10100000001015004b2003b300000300",
    "0c0c0000001015004b20042700000100",
    "0e0e0000001015004b2004b300000300",
    "14160000000c00004b20052200000100",
    "0c0c0000001015004b2005b300000300",
    "0a0a0000000815004b20063100000100",
    "0c0c0000001215004b2006b200000100",
    "181c0000000e00004b20073100000100",
]
record=[
 Ins("422e03c0","clr.b $3c0(a6)"),
 Ins("082e00040060","btst.b #$4, $60(a6)"),Branch("beq","out"),
 Ins("0c6d003a0020","cmpi.w #$3a, $20(a5)"),Branch("beq","input"),
 Ins("0c6d003b0020","cmpi.w #$3b, $20(a5)"),Branch("bne","out"),
 Label("input"),
 Ins("302e0270","move.w $270(a6), d0"),Ins("806e0274","or.w $274(a6), d0"),
 Ins("02406000","andi.w #$6000, d0"),Ins("0c406000","cmpi.w #$6000, d0"),Branch("bne","out"),
 Ins("302e0062","move.w $62(a6), d0"),Ins("5340","subq.w #$1, d0"),
 Ins("0c40000c","cmpi.w #$c, d0"),Branch("bhi","out"),
 Ins("1d7c000103c0","move.b #$1, $3c0(a6)"),
 Ins("e948","lsl.w #$4, d0"),LeaPc("records",0),
 Ins("41f00000","lea.l (a0, d0.w), a0"),JmpAbs(0x1D770),
 Label("out"),JmpNext(MOVE_RECORD),Label("records"),Raw(''.join(RECORDS)),
]
PATCH=Patch(id="air-heavy-pair-kick",title="Global: HP+HK permitido no ar, com golpe proprio de cada personagem",
 spec="src/backend/specs/SPEC-076-air-heavy-pair-kick.md",
 blocks=[Block("air_heavy_pair_record",record)],hooks=[shared_hook(MOVE_RECORD,"air_heavy_pair_record")])
