"""air-fireball-forward-jump (Ryo) — SPEC-006.

O Kou'ouken aéreo só sai com altura $18(a6) >= $60. No pulo para frente
do Ryo essa altura não é alcançada, então a magia não sai (vira soco/chute).
Para o Ryo ($62 == 1), no pulo para frente, o limite cai para
FORWARD_MIN_HEIGHT. Pulo neutro, pulo para trás e os outros personagens
continuam com $60.

Pulo para frente = velocidade horizontal $30(a6) no sentido para onde o
personagem olha ($5E bit 0 = 1 -> direita/positivo), a mesma regra que o
lançamento do pulo usa em $1DD54.

Handlers afetados (só no ar):
  $1D52A  Kou'ouken aéreo para baixo (meia-lua + soco), falha -> soco $1DC88
  $1D4EC  Kou'ouken aéreo reto (meia-lua + chute), falha -> chute $1DC9E
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

RYO = 1                     # $62(a6): 1=Ryo, 2=Robert, ... (ordem da tela de seleção)
ORIGINAL_MIN_HEIGHT = 0x60
FORWARD_MIN_HEIGHT = 0x30   # ajustar com a medição da SPEC-006

SPECIAL_OK = 0x1D53E        # continua o especial (ver SPEC-004)


def height_check(fail_target):
    """Substitui: cmpi.w #$60,$18(a6) / bcs.w <fail_target>."""
    return [
        Ins("0c6e00010062", f"cmpi.w #${RYO:x}, $62(a6)"),
        Branch("bne", "original"),
        Ins("302e0030", "move.w $30(a6), d0"),
        Branch("beq", "original"),          # pulo neutro
        Ins("082e0000005e", "btst.b #$0, $5e(a6)"),
        Branch("beq", "facing_left"),
        Ins("4a40", "tst.w d0"),
        Branch("bmi", "original"),          # olhando p/ direita e indo p/ esquerda
        Branch("bra", "forward"),
        Label("facing_left"),
        Ins("4a40", "tst.w d0"),
        Branch("bpl", "original"),          # olhando p/ esquerda e indo p/ direita
        Label("forward"),
        Ins(f"0c6e{FORWARD_MIN_HEIGHT:04x}0018", f"cmpi.w #${FORWARD_MIN_HEIGHT:x}, $18(a6)"),
        Branch("bcs", "fail"),
        JmpAbs(SPECIAL_OK),
        Label("original"),
        Ins(f"0c6e{ORIGINAL_MIN_HEIGHT:04x}0018", f"cmpi.w #${ORIGINAL_MIN_HEIGHT:x}, $18(a6)"),
        Branch("bcs", "fail"),
        JmpAbs(SPECIAL_OK),
        Label("fail"),
        JmpAbs(fail_target),
    ]


PATCH = Patch(
    id="air-fireball-forward-jump",
    title="Ryo: Kou'ouken aéreo também no pulo para frente",
    spec="src/backend/specs/SPEC-006-ryo-air-fireball-forward-jump.md",
    blocks=[
        Block("air_punch_check", height_check(0x1DC88)),
        Block("air_kick_check", height_check(0x1DC9E)),
    ],
    hooks=[
        # $1D534: cmpi.w #$60,$18(a6) / bcs.w $1dc88   (segue em $1D53E)
        Hook(addr=0x1D534, expect="0c6e006000186500074c", to_block="air_punch_check"),
        # $1D4F6: cmpi.w #$60,$18(a6) / bcs.w $1dc9e   (segue em bra $1D53E)
        Hook(addr=0x1D4F6, expect="0c6e00600018650007a0", to_block="air_kick_check"),
    ],
)
