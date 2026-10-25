"""Ryo: LP/baixo LP -> HP perto -> tras HK — SPEC-061."""
from asm68k import Branch, Ins, JmpAbs, JmpNext, Label, LeaPc
from charlib import ATTACK_WINDOW, MOVE_RECORD, RYO, only, shared_hook, forward_bit, player_sprite, rearm_children
from patchlib import Block, Hook, Patch

STAGE = 0x3B2


def need(cond, label):
    return [Branch(cond, label), JmpNext(ATTACK_WINDOW), Label(label)]


def confirm():
    return [
        # Um especial ja reconhecido conserva a prioridade de cancelamento.
        Ins("4a6e0218", "tst.w $218(a6)"), *need("beq", "no_special"),
        Ins("4a2e021b", "tst.b $21b(a6)"), *need("beq", "connected"),
        Ins("206e0064", "movea.l $64(a6), a0"),
        Ins("4a68006c", "tst.w $6c(a0)"), *need("bgt", "alive"),
        Ins("4aa80018", "tst.l $18(a0)"), *need("ble", "grounded"),
        Ins("720f", "moveq #$f, d1"),
        Ins("c228007c", "and.b $7c(a0), d1"),
        Ins("0c010003", "cmpi.b #$3, d1"), *need("bne", "hit"),
        Ins("0c2800060040", "cmpi.b #$6, $40(a0)"),
        Branch("beq", "stunned"),
        Ins("0c2800070040", "cmpi.b #$7, $40(a0)"), *need("beq", "stunned"),
    ]


def begin(cmd, stage):
    return [
        Ins(f"78{cmd:02x}", f"moveq #${cmd:x}, d4"),
        Ins("4eb90001d41e", "jsr $1d41e.l"), *need("bne", "started"),
        Ins(f"1d7c{stage:04x}03b2", f"move.b #${stage:x}, $3b2(a6)"),
        Ins("426e0274", "clr.w $274(a6)"),
        Ins("48e780c0", "movem.l d0/a0-a1, -(a7)"),
        *player_sprite(), *rearm_children(),
        # Reinicia a reacao ja existente para cobrir o startup do link.
        Ins("206e0064", "movea.l $64(a6), a0"),
        Ins("42280a69", "clr.b $a69(a0)"),
        Ins("7000", "moveq #$0, d0"),
        Ins("10280003", "move.b $3(a0), d0"),
        Ins("e148", "lsl.w #$8, d0"),
        Ins("43f50000", "lea.l (a5, d0.w), a1"),
        Ins("42690056", "clr.w $56(a1)"),
        Ins("137c00010042", "move.b #$1, $42(a1)"),
        Ins("4cdf0301", "movem.l (a7)+, d0/a0-a1"),
        JmpAbs(0x1C0BA),
    ]


first = [
    *only(RYO, ATTACK_WINDOW),
    Ins("0c6e00200230", "cmpi.w #$20, $230(a6)"), Branch("beq", "lp"),
    Ins("0c6e00220230", "cmpi.w #$22, $230(a6)"), Branch("beq", "lp"),
    Ins("0c6e00280230", "cmpi.w #$28, $230(a6)"), *need("beq", "lp"),
    Ins("302e0270", "move.w $270(a6), d0"),
    Ins("806e0274", "or.w $274(a6), d0"),
    Ins("02401010", "andi.w #$1010, d0"),
    Ins("0c401010", "cmpi.w #$1010, d0"), *need("beq", "button"),
    *confirm(), *begin(0x23, 1),
]

last = [
    *only(RYO, ATTACK_WINDOW),
    Ins("0c6e00230230", "cmpi.w #$23, $230(a6)"), *need("beq", "hp"),
    Ins("0c2e000103b2", "cmpi.b #$1, $3b2(a6)"), *need("beq", "target"),
    Ins("302e0270", "move.w $270(a6), d0"),
    Ins("806e0274", "or.w $274(a6), d0"),
    Ins("02402020", "andi.w #$2020, d0"),
    Ins("0c402020", "cmpi.w #$2020, d0"), *need("beq", "button"),
    *forward_bit("facing"),
    Ins("0a000001", "eori.b #$1, d0"),
    Ins("012e0270", "btst.l d0, $270(a6)"), *need("bne", "back"),
    *confirm(), *begin(0x31, 2),
]

reset = [
    *only(RYO, MOVE_RECORD),
    Ins("422e03b2", "clr.b $3b2(a6)"),
    JmpNext(MOVE_RECORD),
]

# Somente a caixa ativa dos links marcados ganha confirmacao de alcance.
# Modifica os limites usados nesta consulta, nunca posicoes dos lutadores.
reach = [
    Ins("4a2e0070", "tst.b $70(a6)"), Branch("bpl", "check"),
    JmpAbs(0xF6BE0),
    Label("check"),
    Ins("48e7c0c0", "movem.l d0-d1/a0-a1, -(a7)"),
    Ins("082e00000070", "btst.b #$0, $70(a6)"), Branch("bne", "select"),
    LeaPc("done", 1), Ins("4ed1", "jmp (a1)"),
    Label("select"),
    Ins("41f900109280", "lea.l $109280.l, a0"),
    Label("owner"),
    Ins("0c6800010062", "cmpi.w #$1, $62(a0)"), Branch("bne", "next"),
    Ins("0c28000103b2", "cmpi.b #$1, $3b2(a0)"), Branch("beq", "hp"),
    Ins("0c28000203b2", "cmpi.b #$2, $3b2(a0)"), Branch("bne", "next"),
    Ins("0c6800310230", "cmpi.w #$31, $230(a0)"), Branch("beq", "child"),
    Branch("bra", "next"),
    Label("hp"),
    Ins("0c6800230230", "cmpi.w #$23, $230(a0)"), Branch("bne", "next"),
    Label("child"),
    Ins("7000", "moveq #$0, d0"),
    Ins("10280003", "move.b $3(a0), d0"),
    Ins("e148", "lsl.w #$8, d0"),
    Ins("43f50000", "lea.l (a5, d0.w), a1"),
    Ins("102e0002", "move.b $2(a6), d0"),
    Ins("b0290007", "cmp.b $7(a1), d0"), Branch("beq", "found"),
    Ins("b0290008", "cmp.b $8(a1), d0"), Branch("beq", "found"),
    Label("next"),
    Ins("b1fc00109280", "cmpa.l #$109280, a0"), Branch("bne", "done"),
    Ins("41f900109380", "lea.l $109380.l, a0"),
    LeaPc("owner", 1), Ins("4ed1", "jmp (a1)"),
    Label("done"),
    Ins("4cdf0303", "movem.l (a7)+, d0-d1/a0-a1"),
    JmpAbs(0xF6B80),
    Label("found"),
    Ins("20680064", "movea.l $64(a0), a0"),
    Ins("4a68006c", "tst.w $6c(a0)"), Branch("ble", "done"),
    Ins("4aa80018", "tst.l $18(a0)"), Branch("bgt", "done"),
    Ins("36280010", "move.w $10(a0), d3"),
    Ins("04430100", "subi.w #$100, d3"),
    Ins("38280010", "move.w $10(a0), d4"),
    Ins("06440100", "addi.w #$100, d4"),
    Ins("3a3c7fff", "move.w #$7fff, d5"),
    Ins("3c3c8000", "move.w #$8000, d6"),
    Ins("4cdf0303", "movem.l (a7)+, d0-d1/a0-a1"),
    JmpAbs(0xF6B80),
]

def namespace(program, prefix):
    out = []
    for item in program:
        if isinstance(item, Label): item = Label(prefix + item.name)
        elif isinstance(item, Branch): item = Branch(item.cond, prefix + item.target)
        elif isinstance(item, LeaPc): item = LeaPc(prefix + item.target, item.reg)
        out.append(item)
    return out


combo = []
for item in namespace(first, "first_"):
    if isinstance(item, JmpNext):
        combo += [LeaPc("last_link", 1), Ins("4ed1", "jmp (a1)")]
    else:
        combo.append(item)
combo += [Label("last_link"), *namespace(last, "last_")]

PATCH = Patch(
    id="lp-hp-hk-target-combo",
    title="Ryo: target LP ou baixo LP -> HP perto -> tras + HK (3 hits)",
    spec="src/backend/specs/SPEC-061-ryo-lp-hp-hk-target-combo.md",
    blocks=[Block("target_chain", combo),
            Block("target_reset", reset), Block("target_reach", reach)],
    hooks=[shared_hook(ATTACK_WINDOW, "target_chain"),
           shared_hook(MOVE_RECORD, "target_reset"),
           Hook(0xF6B78, "4a2e00706b000062", to_block="target_reach")],
)
