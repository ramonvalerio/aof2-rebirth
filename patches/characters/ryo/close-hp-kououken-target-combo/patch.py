"""close-hp-kououken-target-combo (Ryo) — SPEC-036.

Target combo: soco forte perto (comando $23) que acertou, cancelado no
Kou'ouken fraco ($013, C+D, SPEC-033), sempre acerta, em qualquer distância,
no canto ou não, contra qualquer personagem.

Por que falhava: o projétil nasce 96 px à frente do Ryo com a caixa de 54 a
92 px ($229C0, anim $172). Colado (canto) o oponente fica antes da caixa e
o projétil passa por trás dele; com pushback grande, fica longe demais.

  1. Hook compartilhado $1D676 (charlib.SPECIAL_CHOSEN; roda depois do
     kououken-three-buttons, pela ordem do manifest): golpe atual ($230,
     ainda o anterior: $1D6E2 só grava depois) = $23, já conectou
     ($21B = 0) e versão escolhida $013 -> marca $3A9 do Ryo e zera o
     empurrão do oponente ($20 velocidade X, $30/$34); senão desmarca.
  2. Hook compartilhado $22AC2 (charlib.PROJ_SPAWN_X): projétil do Ryo com a
     marca nasce NA origem do oponente ($64). A caixa do projétil pequeno
     ocupa 4..42 px de um dos lados da origem e o corpo do oponente ~30 px
     para cada lado: encosta qualquer que seja o lado. Desmarca.
Tempo: startup 11 cabe no hitstun pesado do soco forte perto (26 + hitstop).
$3A9: livre no registro do jogador (ram_scan; $3A0-$3A7 hit-counter,
$3A8 kohou-impact-sound).
"""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import PROJ_SPAWN_X, RYO, SPECIAL_CHOSEN, only, shared_hook
from patchlib import Block, Patch

CLOSE_HP_CMD = 0x23
WEAK_KOUOUKEN = 0x013
MARK = 0x3A9

mark = [
    *only(RYO, SPECIAL_CHOSEN),
    Ins(f"0c6d{WEAK_KOUOUKEN:04x}0010", f"cmpi.w #${WEAK_KOUOUKEN:x}, $10(a5)"),
    Branch("bne", "unmark"),
    Ins(f"0c6e{CLOSE_HP_CMD:04x}0230", f"cmpi.w #${CLOSE_HP_CMD:x}, $230(a6)"),
    Branch("bne", "unmark"),
    Ins("4a2e021b", "tst.b $21b(a6)"),                 # já conectou
    Branch("bne", "unmark"),
    Ins(f"1d7c0001{MARK:04x}", f"move.b #$1, ${MARK:x}(a6)"),
    Ins("2f08", "move.l a0, -(a7)"),                   # sem empurrão no oponente
    Ins("206e0064", "movea.l $64(a6), a0"),
    Ins("42a80020", "clr.l $20(a0)"),                  # velocidade X (pushback)
    Ins("42680030", "clr.w $30(a0)"),                  # vx / atrito, como $1C6EE-$1C6FE
    Ins("42680034", "clr.w $34(a0)"),
    Ins("205f", "movea.l (a7)+, a0"),
    Branch("bra", "out"),
    Label("unmark"),
    Ins(f"422e{MARK:04x}", f"clr.b ${MARK:x}(a6)"),
    Label("out"),
    JmpNext(SPECIAL_CHOSEN),
]

# No $229C0 (opcode $D8 da animação) a3 é o objeto de SPRITE; a6 é o jogador
# ("movep.w $b(a3),d0 / lea -$80(a5,d0.w),a6"), a0 o projétil.
place = [
    Ins(f"0c6e{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a6)"),
    Branch("bne", "out"),
    Ins(f"4a2e{MARK:04x}", f"tst.b ${MARK:x}(a6)"),
    Branch("beq", "out"),
    Ins(f"422e{MARK:04x}", f"clr.b ${MARK:x}(a6)"),
    Ins("2f09", "move.l a1, -(a7)"),
    Ins("226e0064", "movea.l $64(a6), a1"),            # oponente
    Ins("316900100010", "move.w $10(a1), $10(a0)"),   # nasce na origem dele
    Ins("225f", "movea.l (a7)+, a1"),
    Label("out"),
    JmpNext(PROJ_SPAWN_X),
]

PATCH = Patch(
    id="close-hp-kououken-target-combo",
    title="Ryo: target combo soco forte perto -> Kou'ouken fraco sempre acerta",
    spec="src/backend/specs/SPEC-036-ryo-close-hp-kououken-target-combo.md",
    blocks=[Block("tc_mark", mark), Block("tc_place", place)],
    hooks=[
        shared_hook(SPECIAL_CHOSEN, "tc_mark"),
        shared_hook(PROJ_SPAWN_X, "tc_place"),
    ],
)
