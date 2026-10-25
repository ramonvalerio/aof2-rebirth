"""normal-remap — SPEC-026 (Yuri) / SPEC-030 (Robert).

Remapeamento dos chutes em pé por personagem. Fica num patch só porque os
dois hooks ($1D41E e $1D75C) são compartilhados; cada personagem tem a
sua seção. (O Ryo tem o próprio, overhead-kick, SPEC-016.)

Seleção do chute: $1DC9E calcula d4 ($30 fraco longe, $31 forte longe,
$32 fraco perto, $33 forte perto) e pula para $1D41E, que grava d4 em
$20(a5) e acha o golpe na tabela de comandos do personagem. O hook em
$1D41E (andi.w #$7f,d4 / move.w d4,$20(a5)) troca d4 conforme a direção.
Frente/trás: $270 bits 2 (esquerda) e 3 (direita); o lado vem do $5E do
sprite (bit 0 = 1 -> frente é a direita, como no dash, $1BBF0).

Yuri ($62 = 11), SPEC-026:
  B (qualquer distância) -> $33 chute forte perto ($170)
  frente + B             -> $31 bundada ($177)
  trás + D               -> $30: anim do chute fraco ($172) com dano forte
  D neutro               -> original
  Dados: o $172 só sai pelo trás + D -> dano $0A -> $14, hitstop $0A -> $0D.

Robert ($62 = 2), SPEC-030:
  frente + B -> $33 chute forte perto ($031), agora overhead ($4F30 -> $4B20)
  trás + D   -> $31 chute forte longe ($032)
  D neutro   -> $3F (d4 livre do Robert; a tabela de comandos ganha
                $3F -> entrada 11): registro novo = chute fraco ($030, anim
                $1B0) com dano $1C, hitstop $14 e reação pesada.
  B          -> original
  chute forte durante o dash (d4 $3D) -> registro próprio (cópia do $038
                com efeito $15, a queda da rasteira); o chute fraco do dash não muda
  O registro novo entra no hook em $1D75C (antes da leitura em $1D762, que
  o overhead-kick do Ryo usa): Robert com $20(a5) = $3F usa o registro do
  bloco e segue em $1D770; senão segue em $1D762.
"""
from asm68k import Branch, Ins, JmpAbs, Label, LeaPc, Raw
from patchlib import Block, Data, Hook, Patch

MOVE_TABLE = 0x023BA4
YURI, ROBERT = 11, 2
YURI_LIGHT_KICK = 0x172
ROBERT_CLOSE_HK = 0x031
ROBERT_NEUTRAL_D = 0x3F
ROBERT_COMMANDS = 0x01EC98           # tabela de comandos do Robert (ponteiro em $1E888 + 2*4)

# Registro do D neutro do Robert: chute fraco ($030: 0c 0c 00 00 00 0c 00 00
# 4f30 01b0 0000 0100) com dano/hitstop do chute forte longe ($032) e
# reação pesada.
ROBERT_NEUTRAL_D_RECORD = "1c1c" "0000" "0014" "0000" "4f30" "01b0" "0000" "0200"
# Chute forte durante o dash (d4 $3D; $1DCBC com $20C = $91 -> base $2C):
# o fraco ($3C) e o forte ($3D) usam o mesmo golpe $038 (anim $1B9). O forte
# ganha registro próprio = $038 com efeito $15 (a queda da rasteira, o
# baixo D do Robert, $035). O no-knockdown-normals só bloqueia a queda no ar.
ROBERT_DASH_HK = 0x3D
ROBERT_DASH_HK_RECORD = "0c0c" "0000" "0008" "1500" "4710" "01b9" "0000" "0100"


def forward_bit(label):
    """d0 = bit da frente em $270 (3 direita / 2 esquerda); usa a0."""
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


remap = [
    Ins("0244007f", "andi.w #$7f, d4"),             # original
    Ins("0c440030", "cmpi.w #$30, d4"),
    Branch("bcs", "out"),
    Ins("0c440033", "cmpi.w #$33, d4"),
    Branch("bhi", "out"),
    Ins(f"0c6e{YURI:04x}0062", f"cmpi.w #${YURI:x}, $62(a6)"),
    Branch("beq", "yuri"),
    Ins(f"0c6e{ROBERT:04x}0062", f"cmpi.w #${ROBERT:x}, $62(a6)"),
    Branch("beq", "robert"),
    Label("out"),
    Ins("3b440020", "move.w d4, $20(a5)"),          # original
    JmpAbs(0x1D426),
    # ---- Yuri ----
    Label("yuri"),
    *forward_bit("y_dir"),
    Ins("08040000", "btst.b #$0, d4"),
    Branch("bne", "y_strong"),
    Ins("012e0270", "btst.l d0, $270(a6)"),        # fraco: frente?
    Branch("beq", "y_weak_any"),
    Ins("7831", "moveq #$31, d4"),                  # frente + B: bundada
    Branch("bra", "out"),
    Label("y_weak_any"),
    Ins("7833", "moveq #$33, d4"),                  # B: chute forte perto
    Branch("bra", "out"),
    Label("y_strong"),
    Ins("0a000001", "eori.b #$1, d0"),              # trás
    Ins("012e0270", "btst.l d0, $270(a6)"),
    Branch("beq", "out"),                           # D neutro: original
    Ins("7830", "moveq #$30, d4"),                  # trás + D
    Branch("bra", "out"),
    # ---- Robert ----
    Label("robert"),
    *forward_bit("r_dir"),
    Ins("08040000", "btst.b #$0, d4"),
    Branch("bne", "r_strong"),
    Ins("012e0270", "btst.l d0, $270(a6)"),        # fraco: frente?
    Branch("beq", "out"),                           # B: original
    Ins("7833", "moveq #$33, d4"),                  # frente + B: forte perto (overhead)
    Branch("bra", "out"),
    Label("r_strong"),
    Ins("0a000001", "eori.b #$1, d0"),              # trás
    Ins("012e0270", "btst.l d0, $270(a6)"),
    Branch("beq", "r_neutral"),
    Ins("7831", "moveq #$31, d4"),                  # trás + D: forte longe
    Branch("bra", "out"),
    Label("r_neutral"),
    Ins(f"78{ROBERT_NEUTRAL_D:02x}", f"moveq #${ROBERT_NEUTRAL_D:x}, d4"),   # D neutro: novo
    Branch("bra", "out"),
]

record = [
    Ins("2f09", "move.l a1, -(a7)"),                # original
    Ins("226e0064", "movea.l $64(a6), a1"),         # original
    Ins(f"0c6e{ROBERT:04x}0062", f"cmpi.w #${ROBERT:x}, $62(a6)"),
    Branch("bne", "original"),
    Ins(f"0c6d{ROBERT_NEUTRAL_D:04x}0020", f"cmpi.w #${ROBERT_NEUTRAL_D:x}, $20(a5)"),
    Branch("bne", "dash_hk"),
    LeaPc("robert_d", 0),
    JmpAbs(0x1D770),
    Label("dash_hk"),
    Ins(f"0c6d{ROBERT_DASH_HK:04x}0020", f"cmpi.w #${ROBERT_DASH_HK:x}, $20(a5)"),
    Branch("bne", "original"),
    LeaPc("robert_dash_hk", 0),
    JmpAbs(0x1D770),
    Label("original"),
    JmpAbs(0x1D762),
    Label("robert_d"),
    Raw(ROBERT_NEUTRAL_D_RECORD),
    Label("robert_dash_hk"),
    Raw(ROBERT_DASH_HK_RECORD),
]

PATCH = Patch(
    id="normal-remap",
    title="Chutes remapeados: Yuri (B forte perto, frente+B bundada, trás+D) e Robert (frente+B overhead, trás+D, D novo)",
    spec="src/backend/specs/SPEC-030-robert-kick-remap.md",
    blocks=[Block("kick_remap", remap), Block("robert_record", record)],
    hooks=[
        # $1D41E: andi.w #$7f,d4 / move.w d4,$20(a5)  (segue em $1D426)
        Hook(addr=0x1D41E, expect="0244007f3b440020", to_block="kick_remap"),
        # $1D75C: move.l a1,-(a7) / movea.l $64(a6),a1  (segue em $1D762)
        Hook(addr=0x1D75C, expect="2f09226e0064", to_block="robert_record"),
    ],
    data=[
        # Yuri: o chute fraco vira golpe forte (só sai pelo trás + D)
        Data(MOVE_TABLE + YURI_LIGHT_KICK * 16, "0a0a", "1414"),
        Data(MOVE_TABLE + YURI_LIGHT_KICK * 16 + 5, "0a", "0d"),
        # Robert: chute forte perto overhead; d4 $3F -> entrada 11 (handler do chute)
        Data(MOVE_TABLE + ROBERT_CLOSE_HK * 16 + 8, "4f30", "4b20"),
        Data(ROBERT_COMMANDS + ROBERT_NEUTRAL_D, "ff", "0b"),
    ],
)
