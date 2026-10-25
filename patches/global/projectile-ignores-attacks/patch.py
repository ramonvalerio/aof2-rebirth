"""projectile-ignores-attacks — SPEC-038.

Regra global: projétil não é dissipado ao receber golpe. Encostar na caixa
de ataque de um jogador (filhos 5/6 do sprite) não desfaz mais o projétil;
ele continua voando e pode acertar.

$22D80 (estado do projétil, depois do contato $70 bit 7): $6D = id do
objeto atingido.
  - objeto é projétil ($6F bit 7): disputa pela força $6B (não muda)
  - senão, estado do objeto != 8 -> d0 = 1 -> dissipa ($22F80, estado $E)
Esse "senão" vale para o corpo do oponente (acerto normal) e para a caixa
de ataque dele (golpe no projétil). O hook em $22DD2 desvia o segundo caso:
se o id é o filho 5 ou 6 de P1 ou P2, o projétil sobrevive como no caminho
original de $22DC4 (bclr #7,$70 / d0 = 0).
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

PLAYERS = (0x109280, 0x109380)


def attack_child_check(player, n):
    return [
        Ins("7000", "moveq #$0, d0"),
        Ins(f"1039{player + 3:08x}", f"move.b ${player + 3:x}.l, d0"),   # sprite do jogador
        Ins("e148", "lsl.w #$8, d0"),
        Ins("b4350007", "cmp.b $7(a5, d0.w), d2"),          # filho 5
        Branch("beq", "attack"),
        Ins("b4350008", "cmp.b $8(a5, d0.w), d2"),          # filho 6
        Branch("beq", "attack"),
    ]


survive = [
    Ins("2f02", "move.l d2, -(a7)"),
    Ins("142e006d", "move.b $6d(a6), d2"),                 # objeto atingido
    Branch("beq", "original"),
    *attack_child_check(PLAYERS[0], 0),
    *attack_child_check(PLAYERS[1], 1),
    Label("original"),
    Ins("241f", "move.l (a7)+, d2"),
    Ins("0c7500081000", "cmpi.w #$8, (a5, d1.w)"),       # original
    Branch("beq", "state8"),
    Ins("7001", "moveq #$1, d0"),                          # dissipa
    Ins("4e75", "rts"),
    Label("state8"),
    JmpAbs(0x22DDE),
    Label("attack"),
    Ins("241f", "move.l (a7)+, d2"),
    Ins("08ae00070070", "bclr.b #$7, $70(a6)"),           # como $22DC4: sobrevive
    Ins("7000", "moveq #$0, d0"),
    Ins("4e75", "rts"),
]

PATCH = Patch(
    id="projectile-ignores-attacks",
    title="Projétil não é dissipado ao receber golpe (só some ao acertar ou contra outro projétil)",
    spec="src/backend/specs/SPEC-038-projectile-ignores-attacks.md",
    blocks=[Block("projectile_survive", survive)],
    hooks=[
        # $22DD2: cmpi.w #8,(a5,d1.w) / beq.b $22dde  (depois: moveq #1,d0 / rts)
        Hook(addr=0x22DD2, expect="0c75000810006704", to_block="projectile_survive"),
    ],
)
