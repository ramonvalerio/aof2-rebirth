"""zanretsuken-19-hits (Ryo) — SPEC-025.

O Zanretsuken (comando $44) prende o oponente e bate várias vezes; cada
golpe passa a contar como hit (19 no total), com o dano por golpe reduzido.
Mecanismo em charlib.multi_hit_block (SPEC-027), no hook compartilhado do
estado de ataque ($1C1DA, charlib.ATTACK_STATE).
"""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import (ATTACK_STATE, SPECIAL_CHOSEN, HIT_SOUND, MOVE_TABLE,
                     RYO, multi_hit_block, multi_hit_data, only, shared_hook)
from patchlib import Block, Data, Patch

ZANRETSUKEN = 0x44
HITS = 19
BUDGET = 0x3AA  # byte livre, após $3A8 (som) e $3A9 (target combo).

start = [
    *only(RYO, SPECIAL_CHOSEN),
    Ins("0c6d001e0010", "cmpi.w #$1e, $10(a5)"),
    Branch("bcs", "out"),
    Ins("0c6d001f0010", "cmpi.w #$1f, $10(a5)"),
    Branch("bhi", "out"),
    Ins("1d7c001303aa", "move.b #$13, $3aa(a6)"),
    Label("out"),
    JmpNext(SPECIAL_CHOSEN),
]

contact = [
    Ins("0c6800010062", "cmpi.w #$1, $62(a0)"),
    Branch("bne", "out"),
    Ins("0c6800440230", "cmpi.w #$44, $230(a0)"),
    Branch("bne", "out"),
    Ins("4a2803aa", "tst.b $3aa(a0)"),
    Branch("beq", "exhausted"),
    Ins("532803aa", "subq.b #$1, $3aa(a0)"),
    Branch("bra", "out"),
    Label("exhausted"),
    # Caixas já enfileiradas/soltura não aplicam dano depois do limite.
    Ins("422e0071", "clr.b $71(a6)"),
    Ins("422e0248", "clr.b $248(a6)"),
    Ins("08ae00000252", "bclr.b #$0, $252(a6)"),
    Label("out"),
    JmpNext(HIT_SOUND),
]

PATCH = Patch(
    id="zanretsuken-19-hits",
    title="Ryo: Zanretsuken conta cada golpe: 19 hits",
    spec="src/backend/specs/SPEC-025-ryo-zanretsuken-19-hits.md",
    blocks=[Block("multi_hit", multi_hit_block(RYO, ZANRETSUKEN, budget=BUDGET)),
            Block("zanretsuken_start", start), Block("zanretsuken_contact", contact)],
    hooks=[shared_hook(ATTACK_STATE, "multi_hit"),
           shared_hook(SPECIAL_CHOSEN, "zanretsuken_start"),
           shared_hook(HIT_SOUND, "zanretsuken_contact")],
    data=multi_hit_data([(0x01E, 0x28, 0x02), (0x01F, 0x1E, 0x02)], HITS) + [
        # +2/+3: valores de dano na defesa, antes 10/8 por contato.
        Data(MOVE_TABLE + 0x01E * 16 + 2, "0a0a", "0101"),
        Data(MOVE_TABLE + 0x01F * 16 + 2, "0808", "0101"),
    ],
)
