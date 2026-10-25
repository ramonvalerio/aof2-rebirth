"""kick-remap (Robert) — SPEC-030.

Chutes em pé remapeados pela direção, no hook compartilhado de escolha do
chute ($1D41E, charlib.KICK_SELECT):
  frente + B -> $33 chute forte perto ($031), agora overhead ($4F30 -> $4B20)
  trás + D   -> $31 chute forte longe ($032)
  D neutro   -> $3F (d4 livre do Robert; a tabela de comandos ganha
                $3F -> entrada 11): registro novo = chute fraco ($030, anim
                $1B0) com dano $1C, hitstop $14 e reação pesada.
  B          -> original
  chute forte durante o dash (d4 $3D) -> registro próprio (cópia do $038
                com efeito $15, a queda da rasteira); o chute fraco do dash não muda

Os registros novos entram no hook compartilhado de leitura do registro
($1D75C, charlib.MOVE_RECORD): Robert com $20(a5) = $3F / $3D usa o
registro do bloco e segue em $1D770.
"""
from asm68k import Branch, Ins, JmpAbs, JmpNext, Label, LeaPc, Raw
from charlib import KICK_SELECT, MOVE_RECORD, MOVE_TABLE, ROBERT, forward_bit, only, shared_hook
from patchlib import Block, Data, Patch

ROBERT_CLOSE_HK = 0x031
NEUTRAL_D = 0x3F
COMMANDS = 0x01EC98           # tabela de comandos do Robert (ponteiro em $1E888 + 2*4)

# Registro do D neutro: chute fraco ($030: 0c 0c 00 00 00 0c 00 00
# 4f30 01b0 0000 0100) com dano/hitstop do chute forte longe ($032) e
# reação pesada.
NEUTRAL_D_RECORD = "1c1c" "0000" "0014" "0000" "4f30" "01b0" "0000" "0200"
# Chute forte durante o dash (d4 $3D; $1DCBC com $20C = $91 -> base $2C):
# o fraco ($3C) e o forte ($3D) usam o mesmo golpe $038 (anim $1B9). O forte
# ganha registro próprio = $038 com efeito $15 (a queda da rasteira, o
# baixo D do Robert, $035). O no-knockdown-normals só bloqueia a queda no ar.
DASH_HK = 0x3D
DASH_HK_RECORD = "0c0c" "0000" "0008" "1500" "4710" "01b9" "0000" "0100"

remap = [
    *only(ROBERT, KICK_SELECT),
    Ins("0244007f", "andi.w #$7f, d4"),             # como o original
    Ins("0c440030", "cmpi.w #$30, d4"),
    Branch("bcs", "out"),
    Ins("0c440033", "cmpi.w #$33, d4"),
    Branch("bhi", "out"),
    *forward_bit("dir"),
    Ins("08040000", "btst.b #$0, d4"),
    Branch("bne", "strong"),
    Ins("012e0270", "btst.l d0, $270(a6)"),        # fraco: frente?
    Branch("beq", "out"),                           # B: original
    Ins("7833", "moveq #$33, d4"),                  # frente + B: forte perto (overhead)
    Branch("bra", "out"),
    Label("strong"),
    Ins("0a000001", "eori.b #$1, d0"),              # trás
    Ins("012e0270", "btst.l d0, $270(a6)"),
    Branch("beq", "neutral"),
    Ins("7831", "moveq #$31, d4"),                  # trás + D: forte longe
    Branch("bra", "out"),
    Label("neutral"),
    Ins(f"78{NEUTRAL_D:02x}", f"moveq #${NEUTRAL_D:x}, d4"),   # D neutro: novo
    Label("out"),
    JmpNext(KICK_SELECT),
]

record = [
    Branch("bra", "start"),
    Label("pass"),
    JmpNext(MOVE_RECORD),
    Label("start"),
    Ins(f"0c6e{ROBERT:04x}0062", f"cmpi.w #${ROBERT:x}, $62(a6)"),
    Branch("bne", "pass"),
    Ins(f"0c6d{NEUTRAL_D:04x}0020", f"cmpi.w #${NEUTRAL_D:x}, $20(a5)"),
    Branch("bne", "dash_hk"),
    LeaPc("neutral_d", 0),
    JmpAbs(0x1D770),
    Label("dash_hk"),
    Ins(f"0c6d{DASH_HK:04x}0020", f"cmpi.w #${DASH_HK:x}, $20(a5)"),
    Branch("bne", "pass"),
    LeaPc("dash_hk_record", 0),
    JmpAbs(0x1D770),
    Label("neutral_d"),
    Raw(NEUTRAL_D_RECORD),
    Label("dash_hk_record"),
    Raw(DASH_HK_RECORD),
]

PATCH = Patch(
    id="kick-remap",
    title="Robert: chutes remapeados: frente+B overhead, trás+D forte longe, D neutro novo, chute forte do dash derruba",
    spec="src/backend/specs/SPEC-030-robert-kick-remap.md",
    blocks=[Block("kick_remap", remap), Block("kick_record", record)],
    hooks=[
        shared_hook(KICK_SELECT, "kick_remap"),
        shared_hook(MOVE_RECORD, "kick_record"),
    ],
    data=[
        # chute forte perto overhead; d4 $3F -> entrada 11 (handler do chute)
        Data(MOVE_TABLE + ROBERT_CLOSE_HK * 16 + 8, "4f30", "4b20"),
        Data(COMMANDS + NEUTRAL_D, "ff", "0b"),
    ],
)
