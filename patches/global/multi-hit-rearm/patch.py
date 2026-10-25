"""multi-hit-rearm — SPEC-025 / SPEC-027.

Especiais que prendem o oponente e batem várias vezes passam a registrar
cada golpe como um hit (contador "N HIT COMBO", SPEC-013).

Esses golpes prendem o oponente no 1º contato (efeito de "pegada": o
oponente fica num estado próprio até o atacante sair do ataque) e depois
só tocam a animação de golpes. A caixa de ataque (filhos 5/6 do sprite)
fica marcada como "já acertou" ($70 bit 7) e nunca é rearmada, e o golpe
não tem hits extras (byte 7): sai 1 hit.

Para cada golpe da tabela:
  - byte 7 (hits extras -> $247) = hits - 1; dano por golpe ajustado;
  - a cada frame do estado de ataque, depois do 1º contato ($21B = 0) e
    enquanto $247 > 0, rearma os filhos 5/6 uma vez por peça (contador do
    quadro do sprite $56 = 1). Com $247 > 0 o contato segue o caminho de
    vários hits ($1CEC0 -> $1CFA0), que não troca a reação do oponente.

Hook no começo do estado de ataque ($1C1DA: clr.l $20(a6) / jsr $1DF7E).
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Data, Hook, Patch

MOVE_TABLE = 0x023BA4

# (personagem $62, comando, [(golpe, dano original, dano novo)], hits)
MOVES = [
    (1, 0x44, [(0x01E, 0x28, 0x02), (0x01F, 0x1E, 0x02)], 19),   # Ryo: Zanretsuken (SPEC-025)
    (11, 0x43, [(0x17F, 0x28, 0x04)], 10),                       # Yuri: Hyakuretsu Binta (SPEC-027)
]


def row_check(char, cmd, label_next):
    return [
        Ins(f"0c6e{char:04x}0062", f"cmpi.w #${char:x}, $62(a6)"),
        Branch("bne", label_next),
        Ins(f"0c6e{cmd:04x}0230", f"cmpi.w #${cmd:x}, $230(a6)"),
        Branch("beq", "rearm"),
        Label(label_next),
    ]


rows = []
for k, (char, cmd, _, _) in enumerate(MOVES):
    rows += row_check(char, cmd, f"next{k}")

rearm = [
    Ins("42ae0020", "clr.l $20(a6)"),                # original
    Ins("4eb90001df7e", "jsr $1df7e.l"),             # original
    *rows,
    Branch("bra", "out"),
    Label("rearm"),
    Ins("4a2e021b", "tst.b $21b(a6)"),              # antes do 1º contato: nada
    Branch("bne", "out"),
    Ins("4a2e0247", "tst.b $247(a6)"),              # acabaram os hits extras
    Branch("beq", "out"),
    Ins("48e780c0", "movem.l d0/a0-a1, -(a7)"),
    Ins("7000", "moveq #$0, d0"),
    Ins("102e0003", "move.b $3(a6), d0"),            # sprite do jogador
    Ins("e148", "lsl.w #$8, d0"),
    Ins("41f50000", "lea.l (a5, d0.w), a0"),
    Ins("0c2800010056", "cmpi.b #$1, $56(a0)"),     # 1 vez por peça
    Branch("bne", "done"),
    Ins("7000", "moveq #$0, d0"),
    Ins("10280007", "move.b $7(a0), d0"),            # filho 5
    Ins("e148", "lsl.w #$8, d0"),
    Ins("08b500070070", "bclr.b #$7, $70(a5, d0.w)"),
    Ins("7000", "moveq #$0, d0"),
    Ins("10280008", "move.b $8(a0), d0"),            # filho 6
    Ins("e148", "lsl.w #$8, d0"),
    Ins("08b500070070", "bclr.b #$7, $70(a5, d0.w)"),
    Label("done"),
    Ins("4cdf0301", "movem.l (a7)+, d0/a0-a1"),
    Label("out"),
    JmpAbs(0x1C1E2),
]

data = []
for _, _, moves, hits in MOVES:
    for mid, old, new in moves:
        data.append(Data(MOVE_TABLE + mid * 16, f"{old:02x}{old:02x}", f"{new:02x}{new:02x}"))
        data.append(Data(MOVE_TABLE + mid * 16 + 7, "00", f"{hits - 1:02x}"))

PATCH = Patch(
    id="multi-hit-rearm",
    title="Especiais que prendem e batem várias vezes contam cada hit (Zanretsuken 19, Hyakuretsu Binta 10)",
    spec="src/backend/specs/SPEC-027-multi-hit-rearm.md",
    blocks=[Block("multi_hit_rearm", rearm)],
    hooks=[
        # $1C1DA: clr.l $20(a6) / jsr $1df7e(pc)  (estado de ataque; segue em $1C1E2)
        Hook(addr=0x1C1DA, expect="42ae00204eba1d9e", to_block="multi_hit_rearm"),
    ],
    data=data,
)
