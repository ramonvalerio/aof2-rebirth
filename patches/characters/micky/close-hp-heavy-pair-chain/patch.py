"""Micky: HP perto -> HP+HK, que derruba — SPEC-078."""
from asm68k import Ins,Branch
from charlib import MICKY,ATTACK_WINDOW,MOVE_TABLE,normal_chain_block,shared_hook
from patchlib import Patch,Block,Data
chain=normal_chain_block(MICKY,[(0x23,0x60)])
# Exige acerto real, sem liberar o chain contra defesa ou KO.
pos=next(k for k,i in enumerate(chain) if isinstance(i,Ins) and i.text=='move.b $270(a6), d0')
chain[pos:pos]=[
 Ins("206e0064","movea.l $64(a6), a0"),
 Ins("4a68006c","tst.w $6c(a0)"),Branch("ble","pass"),
 Ins("700f","moveq #$f, d0"),Ins("c028007c","and.b $7c(a0), d0"),
 Ins("0c000003","cmpi.b #$3, d0"),Branch("beq","pass"),
]
PATCH=Patch(id="close-hp-heavy-pair-chain",title="Micky: HP perto cancela em HP+HK com queda",
 spec="src/backend/specs/SPEC-078-micky-close-hp-heavy-pair-chain.md",
 blocks=[Block("micky_hp_pair_chain",chain)],
 hooks=[shared_hook(ATTACK_WINDOW,"micky_hp_pair_chain")],
 data=[Data(MOVE_TABLE+0xe5*16+6,"00","15")])
