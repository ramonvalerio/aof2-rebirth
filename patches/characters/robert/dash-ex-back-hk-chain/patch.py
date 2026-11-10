"""Robert: EX de dois chutes executa rasteira e HK automaticamente — SPEC-071."""
from asm68k import Ins,Branch,Label,JmpAbs,JmpNext
from charlib import ATTACK_WINDOW,only,shared_hook,player_sprite,rearm_children
from patchlib import Patch,Block
chain=[
 *only(2,ATTACK_WINDOW),
 Ins("0c6e003d0230","cmpi.w #$3d, $230(a6)"),Branch("bne","pass"),
 Ins("0c2e000103be","cmpi.b #$1, $3be(a6)"),Branch("bne","pass"),
 Ins("4a2e021b","tst.b $21b(a6)"),Branch("beq","follow"),
 # No erro, conclui a primeira fase ativa antes de iniciar a segunda.
 *player_sprite(),Ins("0c280003005a","cmpi.b #$3, $5a(a0)"),Branch("bcc","follow"),
 Label("pass"),JmpNext(ATTACK_WINDOW),
 Label("follow"),
 Ins("1d7c000203be","move.b #$2, $3be(a6)"),
 Ins("426e0274","clr.w $274(a6)"),Ins("426e0218","clr.w $218(a6)"),
 Ins("7831","moveq #$31, d4"),Ins("4eb90001d41e","jsr $1d41e.l"),Branch("beq","pass"),
 Ins("48e78080","movem.l d0/a0, -(a7)"),*player_sprite(),*rearm_children(),
 Ins("4cdf0101","movem.l (a7)+, d0/a0"),JmpAbs(0x1C0BA),
]
PATCH=Patch(id="dash-ex-back-hk-chain",title="Robert: rasteira EX e HK automatico, segundo hit lanca em juggle",
 spec="src/backend/specs/SPEC-071-robert-dash-ex-back-hk-chain.md",
 blocks=[Block("robert_ex_hk_chain",chain)],hooks=[shared_hook(ATTACK_WINDOW,"robert_ex_hk_chain")])
