"""START na seleção: confirma como B e marca o jogador — SPEC-083.

A seleção ($C77E) lê só A-D ($F0) na borda dos botões da BIOS. Sem A-D, a
borda de START em $10FDAD (bit 0 P1, bit 2 P2) confirma como B (cor 1) e liga
`$3DA` no registro do jogador. A-D desligam; o tempo esgotado ($C75E) também.
Os patches de personagem usam a flag para trocar paleta/retrato.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from charlib import START_FLAG as FLAG
from patchlib import Block, Hook, Patch

P1_RECORD = 0x109280

# $C7CE: andi.w #$f0,d0 / beq.w $c84a (confirmação da seleção).
select = [
    Ins("024000f0", "andi.w #$f0, d0"),
    Ins("4a2e0029", "tst.b $29(a6)"),
    Branch("bne", "check"),                      # continue: mantém cor e flag
    Ins("226e001c", "movea.l $1c(a6), a1"),
    Ins("4a40", "tst.w d0"),
    Branch("beq", "try_start"),
    Ins(f"4229{FLAG:04x}", f"clr.b ${FLAG:x}(a1)"),     # A-D: cor normal
    Branch("bra", "check"),
    Label("try_start"),
    Ins("12390010fdad", "move.b $10fdad.l, d1"),         # bordas de START/SELECT
    Ins(f"b3fc{P1_RECORD:08x}", f"cmpa.l #${P1_RECORD:x}, a1"),
    Branch("beq", "p1"),
    Ins("e409", "lsr.b #$2, d1"),                         # P2: bit 2
    Label("p1"),
    Ins("08010000", "btst.b #$0, d1"),
    Branch("beq", "none"),
    Ins(f"137c0001{FLAG:04x}", f"move.b #$1, ${FLAG:x}(a1)"),
    Ins("7020", "moveq #$20, d0"),                       # confirma como B (cor 1)
    Label("check"),
    Ins("4a40", "tst.w d0"),
    Branch("beq", "none"),
    JmpAbs(0xC7D6),
    Label("none"),
    JmpAbs(0xC84A),
]

# $C75E: move.w #$10,d0 / bra.w $c7f4 (tempo esgotado confirma como A).
timeout = [
    Ins("226e001c", "movea.l $1c(a6), a1"),
    Ins(f"4229{FLAG:04x}", f"clr.b ${FLAG:x}(a1)"),
    Ins("303c0010", "move.w #$10, d0"),
    JmpAbs(0xC7F4),
]

PATCH = Patch(
    id="start-select-flag",
    title="START na seleção confirma como B e marca o jogador",
    spec="src/backend/specs/SPEC-083-ryo-black-gi-start.md",
    blocks=[Block("select_start", select), Block("select_timeout", timeout)],
    hooks=[
        Hook(0xC7CE, "024000f067000076", to_block="select_start"),
        Hook(0xC75E, "303c001060000090", to_block="select_timeout"),
    ],
)
