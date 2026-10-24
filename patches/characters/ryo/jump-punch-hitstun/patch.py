"""jump-punch-hitstun (Ryo) — SPEC-019.

Pulo com soco forte do Ryo (comando $2B, golpe $006, animação $126):
  - o oponente acertado fica mais tempo na reação (hitstun maior);
  - a aterrissagem do Ryo recupera mais rápido;
  => dá para emendar um golpe no chão depois de acertar o pulo.

Hitstun: a reação do defensor tem dois estados. Estado 6 ($1C434): a
animação de reação fica parada enquanto o atacante está no hitstop
($41 = 2). Quando o hitstop acaba, $1C454 zera o contador do quadro
($56 do sprite) e passa para o estado 7 ($1C460), que toca a reação até o
fim ($A69 bit 7). O hook em $1C454 grava EXTRA_HITSTUN no contador quando
o atacante (a0 = $64 do defensor) é o Ryo no pulo com soco forte: o
1º quadro da reação dura EXTRA_HITSTUN frames a mais.

Aterrissagem: a $126 segura o último quadro do ar (q2, fim $80) até
tocar o chão ($58 do sprite = 1, $1C1F4); daí toca q3..q7, a recuperação:
2 + 12 + 3 + 3 = 20 frames. Passa para 2 + 2 + 2 + 1 = 7.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Data, Hook, Patch

RYO = 1
JUMP_HP = 0x2B
EXTRA_HITSTUN = 12
JUMP_HP_FRAMES = 0x052F46      # quadros da $126

hitstun = [
    Ins(f"0c68{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a0)"),
    Branch("bne", "original"),
    Ins(f"0c68{JUMP_HP:04x}0230", f"cmpi.w #${JUMP_HP:x}, $230(a0)"),
    Branch("bne", "original"),
    Ins(f"197c{EXTRA_HITSTUN:04x}0056", f"move.b #${EXTRA_HITSTUN:x}, $56(a4)"),
    JmpAbs(0x1C45A),
    Label("original"),
    Ins("197c00000056", "move.b #$0, $56(a4)"),
    JmpAbs(0x1C45A),
]

# (quadro, duração original, nova) da aterrissagem; bit 7 = peça
LANDING = [(4, 12, 2), (5, 3, 2), (6, 3, 1)]

PATCH = Patch(
    id="jump-punch-hitstun",
    title="Ryo: pulo com soco forte deixa hitstun e aterrissa rápido",
    spec="src/backend/specs/SPEC-019-ryo-jump-punch-hitstun.md",
    blocks=[Block("jump_hp_hitstun", hitstun)],
    hooks=[
        # $1C454: move.b #0,$56(a4)  (segue em $1C45A: estado 7)
        Hook(addr=0x1C454, expect="197c00000056", to_block="jump_hp_hitstun"),
    ],
    data=[
        Data(JUMP_HP_FRAMES + q * 4, f"{0x80 | old:02x}", f"{0x80 | new:02x}")
        for q, old, new in LANDING
    ],
)
