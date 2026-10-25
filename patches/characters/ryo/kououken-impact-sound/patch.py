"""kououken-impact-sound (Ryo) — SPEC-035.

Kou'ouken fraco (C+D, SPEC-033): o acerto toca o som "pesado" do Hien
Shippuukyaku ($0140), como o Kohou com 2 hits (SPEC-034). Médio, forte e
defesa: som original (sorteado em $21E60).

Hook compartilhado no contato de projétil ($224EA, charlib.PROJ_HIT_SOUND;
a6 = defensor, a5 + d4 = projétil):
  projétil do comando $40 ($44) com nível 0 ($3C: tamanho pequeno = fraco,
  barra equivalente $80 do kououken-three-buttons), dono Ryo (o adversário
  do defensor, $64(a6)), sem defesa ($7C & $F != 3, como $21872)
  -> $A5E(defensor) = $0140.
"""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import PROJ_HIT_SOUND, RYO, shared_hook
from patchlib import Block, Patch

KOUOUKEN_CMD = 0x40
IMPACT_SOUND = 0x0140      # som de acerto do Hien Shippuukyaku

impact = [
    Ins("48e78080", "movem.l d0/a0, -(a7)"),
    Ins("41f54000", "lea.l (a5, d4.w), a0"),            # projétil
    Ins(f"0c68{KOUOUKEN_CMD:04x}0044", f"cmpi.w #${KOUOUKEN_CMD:x}, $44(a0)"),
    Branch("bne", "out"),
    Ins("4a28003c", "tst.b $3c(a0)"),                   # nível 0 = fraco
    Branch("bne", "out"),
    Ins("206e0064", "movea.l $64(a6), a0"),             # dono = adversário do defensor
    Ins(f"0c68{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a0)"),
    Branch("bne", "out"),
    Ins("102e007c", "move.b $7c(a6), d0"),              # defesa: som original
    Ins("0200000f", "andi.b #$f, d0"),
    Ins("0c000003", "cmpi.b #$3, d0"),
    Branch("beq", "out"),
    Ins(f"3d7c{IMPACT_SOUND:04x}0a5e", f"move.w #${IMPACT_SOUND:x}, $a5e(a6)"),
    Label("out"),
    Ins("4cdf0101", "movem.l (a7)+, d0/a0"),
    JmpNext(PROJ_HIT_SOUND),
]

PATCH = Patch(
    id="kououken-impact-sound",
    title="Ryo: Kou'ouken fraco (C+D) toca o som de impacto do Hien Shippuukyaku",
    spec="src/backend/specs/SPEC-035-ryo-kououken-impact-sound.md",
    blocks=[Block("kououken_impact", impact)],
    hooks=[shared_hook(PROJ_HIT_SOUND, "kououken_impact")],
)
