"""kick-remap (Yuri) — SPEC-026.

Chutes em pé remapeados pela direção, no hook compartilhado de escolha do
chute ($1D41E, charlib.KICK_SELECT). Frente/trás: $270 bits 2 (esquerda)
e 3 (direita), com o lado do sprite (charlib.forward_bit).

  B (qualquer distância) -> $33 chute forte perto ($170)
  frente + B             -> $31 bundada ($177)
  trás + D               -> $30: anim do chute fraco ($172) com dano forte
  D neutro               -> original
Dados: o $172 só sai pelo trás + D -> dano $0A -> $14, hitstop $0A -> $0D.
"""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import KICK_SELECT, MOVE_TABLE, YURI, forward_bit, only, shared_hook
from patchlib import Block, Data, Patch

YURI_LIGHT_KICK = 0x172

remap = [
    *only(YURI, KICK_SELECT),
    Ins("0244007f", "andi.w #$7f, d4"),             # como o original
    Ins("0c440030", "cmpi.w #$30, d4"),
    Branch("bcs", "out"),
    Ins("0c440033", "cmpi.w #$33, d4"),
    Branch("bhi", "out"),
    *forward_bit("dir"),
    Ins("08040000", "btst.b #$0, d4"),
    Branch("bne", "strong"),
    Ins("012e0270", "btst.l d0, $270(a6)"),        # fraco: frente?
    Branch("beq", "weak_any"),
    Ins("7831", "moveq #$31, d4"),                  # frente + B: bundada
    Branch("bra", "out"),
    Label("weak_any"),
    Ins("7833", "moveq #$33, d4"),                  # B: chute forte perto
    Branch("bra", "out"),
    Label("strong"),
    Ins("0a000001", "eori.b #$1, d0"),              # trás
    Ins("012e0270", "btst.l d0, $270(a6)"),
    Branch("beq", "out"),                           # D neutro: original
    Ins("7830", "moveq #$30, d4"),                  # trás + D
    Label("out"),
    JmpNext(KICK_SELECT),
]

PATCH = Patch(
    id="kick-remap",
    title="Yuri: chutes remapeados: B = forte perto, frente+B = bundada, trás+D = fraco com dano forte",
    spec="src/backend/specs/SPEC-026-yuri-kick-remap.md",
    blocks=[Block("kick_remap", remap)],
    hooks=[shared_hook(KICK_SELECT, "kick_remap")],
    data=[
        # o chute fraco vira golpe forte (só sai pelo trás + D)
        Data(MOVE_TABLE + YURI_LIGHT_KICK * 16, "0a0a", "1414"),
        Data(MOVE_TABLE + YURI_LIGHT_KICK * 16 + 5, "0a", "0d"),
    ],
)
