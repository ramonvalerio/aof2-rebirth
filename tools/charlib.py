"""Peças comuns dos patches de personagem.

Hooks compartilhados: pontos do motor que vários personagens alteram. Cada
patch de personagem declara o hook com `shared_hook(...)` e termina com
`JmpNext(<endereço>)` quando o personagem não é o dele; o build liga os
patches do mesmo endereço em sequência (patchlib.Hook.chain).
"""
from asm68k import Branch, Ins, JmpAbs, JmpNext, Label
from patchlib import Data, Hook

MOVE_TABLE = 0x023BA4   # 16 bytes por golpe

RYO, ROBERT, TAKUMA, YURI = 1, 2, 10, 11   # $62

# $1D41E: andi.w #$7f,d4 / move.w d4,$20(a5)  (segue em $1D426)
# Escolha do chute em pé: $1DC9E calcula d4 ($30 fraco longe, $31 forte
# longe, $32 fraco perto, $33 forte perto). Os blocos rodam ANTES do
# original e podem trocar d4.
KICK_SELECT = 0x1D41E
# $1D75C: move.l a1,-(a7) / movea.l $64(a6),a1  (segue em $1D762)
# Leitura do registro do golpe. Os blocos rodam DEPOIS do original; para
# usar um registro próprio: lea registro,a0 / jmp $1D770.
MOVE_RECORD = 0x1D75C
# $1C066: btst.b #4,$3f(a6)  (segue no bne de $1C06C)
# Janela de ataque (estado 3, a cada frame). Os blocos rodam ANTES do original.
ATTACK_WINDOW = 0x1C066
# $1C1DA: clr.l $20(a6) / jsr $1df7e(pc)  (segue em $1C1E2)
# Começo do estado de ataque. Os blocos rodam DEPOIS do original.
ATTACK_STATE = 0x1C1DA

_SHARED = {
    KICK_SELECT: ("0244007f3b440020", "before", [
        Ins("0244007f", "andi.w #$7f, d4"),
        Ins("3b440020", "move.w d4, $20(a5)"),
    ]),
    MOVE_RECORD: ("2f09226e0064", "after", [
        Ins("2f09", "move.l a1, -(a7)"),
        Ins("226e0064", "movea.l $64(a6), a1"),
    ]),
    ATTACK_WINDOW: ("082e0004003f", "before", [
        Ins("082e0004003f", "btst.b #$4, $3f(a6)"),
    ]),
    ATTACK_STATE: ("42ae00204eba1d9e", "after", [
        Ins("42ae0020", "clr.l $20(a6)"),
        Ins("4eb90001df7e", "jsr $1df7e.l"),
    ]),
}


def shared_hook(addr, block):
    expect, chain, original = _SHARED[addr]
    return Hook(addr=addr, expect=expect, to_block=block, chain=chain, original=original)


def only(char, hook):
    """Começo de bloco: se não é o personagem, segue a cadeia."""
    return [
        Ins(f"0c6e{char:04x}0062", f"cmpi.w #${char:x}, $62(a6)"),
        Branch("beq", "mine"),
        JmpNext(hook),
        Label("mine"),
    ]


def forward_bit(label):
    """d0 = bit da frente em $270 (3 direita / 2 esquerda); usa a0.

    O lado vem do $5E do sprite (bit 0 = 1 -> frente é a direita, como no
    dash, $1BBF0).
    """
    return [
        Ins("7000", "moveq #$0, d0"),
        Ins("102e0003", "move.b $3(a6), d0"),       # sprite do jogador
        Ins("e148", "lsl.w #$8, d0"),
        Ins("41f50000", "lea.l (a5, d0.w), a0"),
        Ins("7003", "moveq #$3, d0"),               # frente = direita
        Ins("08280000005e", "btst.b #$0, $5e(a0)"),
        Branch("bne", label),
        Ins("7002", "moveq #$2, d0"),               # frente = esquerda
        Label(label),
    ]


def rearm_children():
    """Rearma as caixas de ataque (filhos 5/6 do sprite, $70 bit 7). Usa d0/a0;
    espera a0 = sprite do jogador."""
    return [
        Ins("7000", "moveq #$0, d0"),
        Ins("10280007", "move.b $7(a0), d0"),            # filho 5
        Ins("e148", "lsl.w #$8, d0"),
        Ins("08b500070070", "bclr.b #$7, $70(a5, d0.w)"),
        Ins("7000", "moveq #$0, d0"),
        Ins("10280008", "move.b $8(a0), d0"),            # filho 6
        Ins("e148", "lsl.w #$8, d0"),
        Ins("08b500070070", "bclr.b #$7, $70(a5, d0.w)"),
    ]


def player_sprite():
    """a0 = sprite do jogador; usa d0."""
    return [
        Ins("7000", "moveq #$0, d0"),
        Ins("102e0003", "move.b $3(a6), d0"),
        Ins("e148", "lsl.w #$8, d0"),
        Ins("41f50000", "lea.l (a5, d0.w), a0"),
    ]


def normal_chain_block(char, rows):
    """Chain ao conectar (SPEC-018): rows = [(golpe atual $230, botões no byte alto de $270)].

    Já conectado ($21B = 0), com o botão pedido apertado agora ($270) ou
    guardado ($274, acumulado no hitstop): $274 & $7070 -> $270, zera $274,
    jsr $1D808 (consome $270). Se o golpe começou (flags da volta, como em
    $1C0B8), rearma os filhos 5/6 e sai como o cancel ($1C0BA).
    """
    out = [
        Branch("bra", "start"),
        Label("pass"),                                   # (no começo: desvios curtos)
        JmpNext(ATTACK_WINDOW),
        Label("start"),
        Ins(f"0c6e{char:04x}0062", f"cmpi.w #${char:x}, $62(a6)"),
        Branch("bne", "pass"),
        Ins("4a2e021b", "tst.b $21b(a6)"),              # ainda não conectou
        Branch("bne", "pass"),
        Ins("102e0270", "move.b $270(a6), d0"),         # apertado agora
        Ins("802e0274", "or.b $274(a6), d0"),           # ou guardado
    ]
    for k, (cmd, mask) in enumerate(rows):
        nxt = f"next{k}"
        out += [
            Ins(f"0c6e{cmd:04x}0230", f"cmpi.w #${cmd:x}, $230(a6)"),
            Branch("bne", nxt),
            Ins("1200", "move.b d0, d1"),
            Ins(f"020100{mask:02x}", f"andi.b #${mask:x}, d1"),
            Ins(f"0c0100{mask:02x}", f"cmpi.b #${mask:x}, d1"),
            Branch("beq", "go"),
            Label(nxt),
        ]
    out += [
        Branch("bra", "pass"),
        Label("go"),
        Ins("302e0274", "move.w $274(a6), d0"),
        Ins("02407070", "andi.w #$7070, d0"),
        Ins("816e0270", "or.w d0, $270(a6)"),
        Ins("426e0274", "clr.w $274(a6)"),
        Ins("4eb90001d808", "jsr $1d808.l"),
        Branch("beq", "none"),                           # flags da volta, como $1C0B8
        Ins("48e780c0", "movem.l d0/a0-a1, -(a7)"),     # como o rearm do SPEC-008
        *player_sprite(),
        *rearm_children(),
        Ins("4cdf0301", "movem.l (a7)+, d0/a0-a1"),
        JmpAbs(0x1C0BA),                                 # cancel feito
        Label("none"),
        Ins("4e75", "rts"),
    ]
    return out


def multi_hit_block(char, cmd):
    """Golpe que prende e bate várias vezes conta cada hit (SPEC-027).

    Depois do 1º contato ($21B = 0) e enquanto houver hits extras ($247),
    rearma os filhos 5/6 uma vez por peça (contador do quadro $56 = 1).
    """
    return [
        *only(char, ATTACK_STATE),
        Ins(f"0c6e{cmd:04x}0230", f"cmpi.w #${cmd:x}, $230(a6)"),
        Branch("bne", "out"),
        Ins("4a2e021b", "tst.b $21b(a6)"),              # antes do 1º contato: nada
        Branch("bne", "out"),
        Ins("4a2e0247", "tst.b $247(a6)"),              # acabaram os hits extras
        Branch("beq", "out"),
        Ins("48e780c0", "movem.l d0/a0-a1, -(a7)"),
        *player_sprite(),
        Ins("0c2800010056", "cmpi.b #$1, $56(a0)"),     # 1 vez por peça
        Branch("bne", "done"),
        *rearm_children(),
        Label("done"),
        Ins("4cdf0301", "movem.l (a7)+, d0/a0-a1"),
        Label("out"),
        JmpNext(ATTACK_STATE),
    ]


def multi_hit_data(moves, hits):
    """moves = [(golpe, dano original, dano novo)]: byte 7 = hits extras."""
    out = []
    for mid, old, new in moves:
        out.append(Data(MOVE_TABLE + mid * 16, f"{old:02x}{old:02x}", f"{new:02x}{new:02x}"))
        out.append(Data(MOVE_TABLE + mid * 16 + 7, "00", f"{hits - 1:02x}"))
    return out


DESPERATION_COMMANDS = 0x025D04   # linha = + ($62 - 1) * $20, word por comando $40-$4F
RYO_DESPERATION = 0xA0E           # lista de passos v v> -> v> v <v <- + C


def desperation_slot(char, cmd):
    return DESPERATION_COMMANDS + (char - 1) * 0x20 + (cmd - 0x40) * 2
