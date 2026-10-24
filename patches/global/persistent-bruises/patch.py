"""persistent-bruises — SPEC-014.

O rosto machucado continua no round seguinte da mesma luta.

Mecanismo original:
  - nível do rosto = $5B do objeto de sprite do jogador (0 normal, 1, 2);
    é o seletor de peça alternativa (cabeça machucada) do desenho ($4C88)
  - sobe em $22384: a cada acerto $26C desce; ao zerar recarrega com $26D
    e soma 1 em $5B (teto 2)
  - no round novo o sprite do jogador é recriado pela inicialização genérica
    de objetos ($06C0), que zera $5B em $074A

Patch: em $074A, se o objeto é o sprite de um jogador (slot apontado pelo
byte $3 do P1/P2) e a luta já está em andamento (algum jogador já venceu um
round: -$190 do jogador, word, +1 no vencedor em $A9BA), o $5B NÃO é
zerado. No 1º round (0 x 0) zera como antes, então cada luta nova começa
com o rosto limpo. ($25A, o "BEAT BY", não serve: é a sequência de
adversários vencidos no arcade, não o placar da luta.)
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

P1, P2 = 0x109280, 0x109380
SPRITE_SLOT = 0x3          # byte do jogador: slot do objeto de sprite
ROUND_WINS = -0x190        # vitórias de ROUND na luta atual (word; +1 em $A9BA)
AFTER = 0x752              # move.b d0,$5d(a0) (continua a inicialização)

# Substitui: move.b d0,$5b(a0) / move.b d0,$5c(a0)  em $074A (d0 = 0)
keep_bruise = [
    Ins("1140005c", "move.b d0, $5c(a0)"),            # 2ª instrução substituída
    Ins("48e740c0", "movem.l d1/a0-a1, -(a7)"),
    Ins("7200", "moveq #$0, d1"),
    Ins(f"1239{P1 + SPRITE_SLOT:08x}", f"move.b ${P1 + SPRITE_SLOT:x}.l, d1"),
    Ins("e149", "lsl.w #$8, d1"),
    Ins("43f51000", "lea.l (a5, d1.w), a1"),
    Ins("b1c9", "cmpa.l a1, a0"),
    Branch("beq", "player"),
    Ins("7200", "moveq #$0, d1"),
    Ins(f"1239{P2 + SPRITE_SLOT:08x}", f"move.b ${P2 + SPRITE_SLOT:x}.l, d1"),
    Ins("e149", "lsl.w #$8, d1"),
    Ins("43f51000", "lea.l (a5, d1.w), a1"),
    Ins("b1c9", "cmpa.l a1, a0"),
    Branch("bne", "clear"),
    Label("player"),
    Ins(f"4a79{P1 + ROUND_WINS:08x}", f"tst.w ${P1 + ROUND_WINS:x}.l"),
    Branch("bne", "keep"),
    Ins(f"4a79{P2 + ROUND_WINS:08x}", f"tst.w ${P2 + ROUND_WINS:x}.l"),
    Branch("bne", "keep"),
    Label("clear"),
    Ins("4cdf0302", "movem.l (a7)+, d1/a0-a1"),
    Ins("1140005b", "move.b d0, $5b(a0)"),            # 1ª instrução substituída
    JmpAbs(AFTER),
    Label("keep"),
    Ins("4cdf0302", "movem.l (a7)+, d1/a0-a1"),
    JmpAbs(AFTER),
]

PATCH = Patch(
    id="persistent-bruises",
    title="Rosto machucado continua nos rounds seguintes da mesma luta",
    spec="src/backend/specs/SPEC-014-persistent-bruises.md",
    blocks=[Block("keep_bruise", keep_bruise)],
    hooks=[
        Hook(addr=0x74A, expect="1140005b1140005c", to_block="keep_bruise"),
    ],
)
