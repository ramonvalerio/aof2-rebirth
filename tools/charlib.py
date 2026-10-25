"""Peças comuns dos patches de personagem.

Hooks compartilhados: pontos do motor que vários personagens alteram. Cada
patch de personagem declara o hook com `shared_hook(...)` e termina com
`JmpNext(<endereço>)` quando o personagem não é o dele; o build liga os
patches do mesmo endereço em sequência (patchlib.Hook.chain).
"""
from asm68k import Branch, Ins, JmpAbs, JmpNext, Label
from patchlib import Block, Data, Hook

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

# $1D676: btst.b #4,$60(a6)  (segue no beq de $1D67C)
# Especial com versão já escolhida ($10(a5) = golpe, $5C(a4) = nível; $218
# ainda tem as marcas do botão, SPEC-004). Os blocos rodam ANTES do original
# e podem trocar a versão.
SPECIAL_CHOSEN = 0x1D676

# $224BE: move.w $a5c(a0),$a5e(a6)  (segue no rts de $224C4)
# Contato de golpe corpo a corpo: a6 = defensor, a0 = atacante. O som fixo
# do golpe ($A5C do atacante, opcode $E7 das listas) passa para $A5E do
# defensor; $21E34 toca $A5E ou sorteia na tabela $21E60. Os blocos rodam
# DEPOIS do original e podem trocar $A5E(a6).
HIT_SOUND = 0x224BE

# $1E062: and.b d1,d0 / cmp.b $1(a1,d4.w),d0  (segue no beq de $1E068)
# Leitor de comandos: compara o input (d1) com um passo da tabela $25D04
# (a1; d4 = offset do passo; d0 = máscara do passo). a6 = jogador. Os
# blocos rodam ANTES do original e podem mudar a máscara (d0). As listas de
# passos são compartilhadas entre personagens (ex.: $1B8 = soco final do
# ↓↘→ + soco de 11 personagens).
CMD_STEP = 0x1E062

# $224EA: move.w $30(a5,d4.w),$a5e(a6)  (segue no rts de $224F0)
# Contato de projétil: a6 = defensor, a5 + d4 = objeto do projétil (criado
# em $229C0: $44 = comando do dono, $3C = nível 0/1/2 do tamanho). O som do
# projétil ($30, 0 = sorteado) passa para $A5E. Blocos DEPOIS do original.
PROJ_HIT_SOUND = 0x224EA

# $22AC2: add.w $10(a3),d3 / move.w d3,$10(a0)  (segue em $22ACA)
# Criação do projétil ($229C0, opcode $D8 da animação): a6 = jogador dono,
# a3 = objeto de sprite dele, a0 = projétil, d3 = X, d1 = vx
# (16.16, sinal = sentido). Blocos DEPOIS do original: podem trocar $10(a0).
PROJ_SPAWN_X = 0x22AC2

# Saída de ataque aéreo depois do contato com chão; antes do original.
LANDING_ATTACK = 0x1C234
# Movimento horizontal da reação; depois da conversão original para 16.16.
REACTION_PUSH = 0x1CBB0

_SHARED = {
    LANDING_ATTACK: ("197c00010058", "before", [
        Ins("197c00010058", "move.b #$1, $58(a4)"),
    ]),
    REACTION_PUSH: ("3028002048c0e188", "after", [
        Ins("30280020", "move.w $20(a0), d0"),
        Ins("48c0", "ext.l d0"),
        Ins("e188", "lsl.l #$8, d0"),
    ]),
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
    CMD_STEP: ("c001b0314001", "before", [
        Ins("c001", "and.b d1, d0"),
        Ins("b0314001", "cmp.b $1(a1, d4.w), d0"),
    ]),
    PROJ_HIT_SOUND: ("3d7540300a5e", "after", [
        Ins("3d7540300a5e", "move.w $30(a5, d4.w), $a5e(a6)"),
    ]),
    PROJ_SPAWN_X: ("d66b001031430010", "after", [
        Ins("d66b0010", "add.w $10(a3), d3"),
        Ins("31430010", "move.w d3, $10(a0)"),
    ]),
    HIT_SOUND: ("3d680a5c0a5e", "after", [
        Ins("3d680a5c0a5e", "move.w $a5c(a0), $a5e(a6)"),
    ]),
    SPECIAL_CHOSEN: ("082e00040060", "before", [
        Ins("082e00040060", "btst.b #$4, $60(a6)"),
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


def multi_hit_block(char, cmd, budget=None):
    """Golpe que prende e bate várias vezes conta cada hit (SPEC-027).

    Depois do 1º contato ($21B = 0) e enquanto houver hits extras ($247),
    rearma os filhos 5/6 uma vez por peça (contador do quadro $56 = 1).
    Com budget, usa o contador próprio desse offset e não rearma no hitstop.
    """
    return [
        *only(char, ATTACK_STATE),
        Ins(f"0c6e{cmd:04x}0230", f"cmpi.w #${cmd:x}, $230(a6)"),
        Branch("bne", "out"),
        Ins("4a2e021b", "tst.b $21b(a6)"),              # antes do 1º contato: nada
        Branch("bne", "out"),
        Ins(f"4a2e{(0x247 if budget is None else budget):04x}",
            f"tst.b ${(0x247 if budget is None else budget):x}(a6)"),
        Branch("beq", "out"),
        *([] if budget is None else [
            Ins("0c2e00020041", "cmpi.b #$2, $41(a6)"),
            Branch("beq", "out"),
        ]),
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


# ---------------------------------------------------------------------------
# Especial ↓↘→ + soco com três versões pelo botão (SPEC-033):
#   ↓↘→ + C + D -> fraco (id+2, derruba)   ↓↘→ + C -> médio (id+1)   ↓↘→ + D -> forte (id+0)
QCF_PUNCH_STEP = 0x1B8      # último passo do ↓↘→ + soco (lista $1A0, compartilhada)
_HIT_EFFECT, _KNOCKDOWN = 6, 0x01
_GAUGE = (0xC0, 0xA0, 0x80)  # barra equivalente (bit 7 = marca do special-strength-by-button)
_LEVEL = (3, 2, 1)


def fireball_three_buttons(char, strong_id, name):
    """Blocos, hooks e dados para o ↓↘→ + soco de `char` (golpes strong_id..+2).

    1. $1D676 (SPECIAL_CHOSEN): comando do jogador ($218 bit 9) com golpe
       strong_id..strong_id+2 -> versão pelas marcas do botão: bit 10 (C+D,
       special-strength-by-button) = fraco, bit 8 (forte) = forte, senão médio.
       Grava $10(a5), $5C(a4) e a barra equivalente $23F (tamanho do projétil).
    2. $1E062 (CMD_STEP): no passo final $1B8 (f0 10 = exatamente soco) a
       máscara perde o bit 6, senão o par C+D ($50, "C segurado") era recusado
       e saía o uppercut.
    3. Dados: o fraco (id+2) ganha o efeito de acerto $01 (a queda do Kohou).
    """
    ids = (strong_id, strong_id + 1, strong_id + 2)

    def pick(k, last=False):
        mid = ids[k]
        return [
            Ins(f"3b7c{mid:04x}0010", f"move.w #${mid:x}, $10(a5)"),
            Ins(f"197c{_LEVEL[k]:04x}005c", f"move.b #${_LEVEL[k]:x}, $5c(a4)"),
            Ins(f"1d7c00{_GAUGE[k]:02x}023f", f"move.b #${_GAUGE[k]:x}, $23f(a6)"),
        ] + ([] if last else [Branch("bra", "out")])

    choose = [
        *only(char, SPECIAL_CHOSEN),
        Ins("082e00010218", "btst.b #$1, $218(a6)"),      # bit 9: comando do jogador
        Branch("beq", "out"),
        Ins(f"0c6d{ids[0]:04x}0010", f"cmpi.w #${ids[0]:x}, $10(a5)"),
        Branch("bcs", "out"),
        Ins(f"0c6d{ids[2]:04x}0010", f"cmpi.w #${ids[2]:x}, $10(a5)"),
        Branch("bhi", "out"),
        Ins("082e00020218", "btst.b #$2, $218(a6)"),      # bit 10: C+D
        Branch("bne", "weak"),
        Ins("082e00000218", "btst.b #$0, $218(a6)"),      # bit 8: forte
        Branch("bne", "strong"),
        *pick(1),
        Label("weak"),
        *pick(2),
        Label("strong"),
        *pick(0, last=True),
        Label("out"),
        JmpNext(SPECIAL_CHOSEN),
    ]
    command = [
        *only(char, CMD_STEP),
        Ins(f"0c44{QCF_PUNCH_STEP:04x}", f"cmpi.w #${QCF_PUNCH_STEP:x}, d4"),
        Branch("bne", "out"),
        Ins("020000bf", "andi.b #$bf, d0"),
        Label("out"),
        JmpNext(CMD_STEP),
    ]
    blocks = [Block(f"{name}_buttons", choose), Block(f"{name}_command", command)]
    hooks = [shared_hook(SPECIAL_CHOSEN, f"{name}_buttons"), shared_hook(CMD_STEP, f"{name}_command")]
    data = [Data(MOVE_TABLE + ids[2] * 16 + _HIT_EFFECT, "00", f"{_KNOCKDOWN:02x}")]
    return blocks, hooks, data
