"""crouch-punch-advantage (Ryo) — SPEC-024.

Soco forte agachado ($29) com a mesma vantagem do soco forte perto ($23):
hitstun extra no oponente e o tempo de quadros do soco forte perto.
(O pulo com soco forte, SPEC-019, voltou ao original.)

Hitstun: a reação do defensor tem dois estados. Estado 6 ($1C434): a
animação de reação fica parada enquanto o atacante está no hitstop
($41 = 2). Quando o hitstop acaba, $1C454 zera o contador do quadro
($56 do sprite) e passa para o estado 7 ($1C460), que toca a reação até o
fim ($A69 bit 7). O hook em $1C454 grava os frames extras no contador
quando o atacante (a0 = $64 do defensor) é o Ryo com o soco forte agachado:
o 1º quadro da reação dura esse tanto a mais.

Reação ($21314 -> $20604): em pé, nível leve = 16 frames, pesado = 26
(sobe de nível com dano > $10, $21C42); agachado = 14 nos dois. O soco
forte perto (dano $14) dá a pesada; o agachado (dano $0C), a leve.
Por isso o agachado ganha +10 só contra oponente em pé ($60 bit 5 = 0).

Soco forte agachado (anim $124, golpe $004) com o tempo do soco forte perto
(anim $127: startup 3, ativo 9, recuperação 6, total 18) e o mesmo hitstop
($10, byte 5):
  q1 2 -> 1, q3 9 -> 7 (ativo 2 + 7), q4 4 -> 2, q5 4 -> 2, q6 3 -> 2
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Data, Hook, Patch

RYO = 1
CROUCH_HP = 0x29
CROUCH_HP_EXTRA = 26 - 16       # reação pesada - leve (oponente em pé)
MOVE_TABLE = 0x023BA4
CROUCH_HP_MOVE = 0x004
HITSTOP = 5

hitstun = [
    Ins(f"0c68{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a0)"),
    Branch("bne", "original"),
    Ins(f"0c68{CROUCH_HP:04x}0230", f"cmpi.w #${CROUCH_HP:x}, $230(a0)"),
    Branch("bne", "original"),
    Ins("082e00050060", "btst.b #$5, $60(a6)"),    # defensor agachado: 14 nos dois
    Branch("bne", "original"),
    Ins(f"197c{CROUCH_HP_EXTRA:04x}0056", f"move.b #${CROUCH_HP_EXTRA:x}, $56(a4)"),
    JmpAbs(0x1C45A),
    Label("original"),
    Ins("197c00000056", "move.b #$0, $56(a4)"),
    JmpAbs(0x1C45A),
]

# (endereço do byte de duração, original, novo); bit 7 = peça
FRAME_DURATIONS = [
    # soco forte agachado, anim $124: tempo do soco forte perto
    (0x052EEE + 1 * 4, 0x82, 0x81),
    (0x052EEE + 3 * 4, 0x89, 0x87),
    (0x052EEE + 4 * 4, 0x04, 0x02),
    (0x052EEE + 5 * 4, 0x84, 0x82),
    (0x052EEE + 6 * 4, 0x83, 0x82),
]

PATCH = Patch(
    id="crouch-punch-advantage",
    title="Ryo: soco forte agachado com a vantagem do soco forte perto",
    spec="src/backend/specs/SPEC-024-ryo-crouch-punch-advantage.md",
    blocks=[Block("crouch_hp_hitstun", hitstun)],
    hooks=[
        # $1C454: move.b #0,$56(a4)  (segue em $1C45A: estado 7)
        Hook(addr=0x1C454, expect="197c00000056", to_block="crouch_hp_hitstun"),
    ],
    data=[
        *[Data(addr, f"{old:02x}", f"{new:02x}") for addr, old, new in FRAME_DURATIONS],
        Data(MOVE_TABLE + CROUCH_HP_MOVE * 16 + HITSTOP, "0c", "10"),
    ],
)
