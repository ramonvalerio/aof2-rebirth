"""Dash imediato ao levantar do agachamento — SPEC-081."""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

# Estado 5 ($1BEA4): agachado ($20C=$85) ou defesa agachada ($86).
# Estado 11 ($1BE4A): levantando ($20C=$87) até o fim da animação.
# O detector de dois toques ($1CCDA, SPEC-011) só rodava no neutro/andar:
# toques dados ao soltar o baixo e durante o levantar se perdiam.


def leave_crouch_and_dash():
    """Limpa o agachado (como o fim do estado 11) e inicia o dash.
    $1BC84 escolhe frente/trás pelo lado atual e termina em rts."""
    return [
        Label("dash"),
        Ins("08ae00050060", "bclr.b #$5, $60(a6)"),
        Ins("302efe62", "move.w -$19e(a6), d0"),
        Ins("01ad17bd", "bclr.b d0, $17bd(a5)"),
        JmpAbs(0x1BC84),
    ]


# $1BECE: btst #1,$270(a6) / bne $1BEEC (baixo segurado = continua agachado).
# Ao soltar o baixo, lê o toque deste mesmo frame antes do comando 8.
crouched = [
    Ins("082e00010270", "btst.b #$1, $270(a6)"),
    Branch("beq", "released"),
    JmpAbs(0x1BEEC),
    Label("released"),
    # Defesa agachada não vira dash (o oponente está atacando).
    Ins("0c2e0086020c", "cmpi.b #$86, $20c(a6)"),
    Branch("beq", "stand"),
    Ins("4eb90001ccda", "jsr $1ccda.l"),
    Branch("bne", "dash"),
    Label("stand"),
    JmpAbs(0x1BED6),
    *leave_crouch_and_dash(),
]

# $1BE74: tst.b $a69(a6) / bpl $1BE92, depois da checagem de defesa.
# A defesa continua com prioridade; golpes ($1D808) ficam depois do dash,
# na mesma ordem do neutro ($1BA5C).
standing_up = [
    Ins("4eb90001ccda", "jsr $1ccda.l"),
    Branch("bne", "dash"),
    Ins("4a2e0a69", "tst.b $a69(a6)"),
    Branch("bmi", "anim_end"),
    JmpAbs(0x1BE92),
    Label("anim_end"),
    JmpAbs(0x1BE7A),
    *leave_crouch_and_dash(),
]

PATCH = Patch(
    id="crouch-stand-dash",
    title="Dash imediato ao levantar do agachamento",
    spec="src/backend/specs/SPEC-081-crouch-stand-dash.md",
    blocks=[Block("crouch_release_dash", crouched),
            Block("stand_up_dash", standing_up)],
    hooks=[
        Hook(0x1BECE, "082e000102706616", to_block="crouch_release_dash"),
        Hook(0x1BE74, "4a2e0a696a18", to_block="stand_up_dash"),
    ],
)
