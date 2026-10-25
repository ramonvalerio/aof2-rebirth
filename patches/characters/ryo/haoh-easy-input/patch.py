"""haoh-easy-input (Ryo) — SPEC-021.

Haoh Shoukouken (SUPER, comando $42, handler $1D5A8) com um comando mais
fácil: frente, um "C" (trás, baixo, frente) e soco (A ou C, a força vem do
botão).

Tabela de comandos: $1DFC2 usa $25D04 + ($62 - 1) * $20, então o Ryo usa a
1ª linha ($25D04); a word do comando $42 (+4) aponta para a lista de passos
$25D04 + $2DC. Passo = 8 bytes: [máscara][valor][prazo][0][próximo][0 0];
o passo vale quando (direção & máscara) == valor; direções já relativas ao
lado (8 = frente, 4 = trás, 2 = baixo); próximo $FFFF = comando completo.

Original ($2DC, exato, 10 frames por passo; a mesma lista é usada por mais
6 personagens):
  -> <- <v v v> -> + soco
Novo (lista própria numa lista órfã, só o Ryo aponta para ela):
  frente  (máscara 8: -> , frente-cima, frente-baixo)
  trás    (máscara 4: <- , trás-cima, trás-baixo)
  baixo   (máscara 2: qualquer direção com baixo)
  frente  (máscara 8)
  soco
com 20 frames por passo. As diagonais no meio do "C" deixam de ser
obrigatórias, e as que sobram valem como o passo seguinte. Para o comando
rápido: trás-baixo fecha trás + baixo, e frente + soco no mesmo frame
fecha o comando.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Data, Hook, Patch

COMMANDS = 0x025D04
RYO_ROW = COMMANDS                 # ($62 - 1) * $20 = 0
HAOH_SLOT = RYO_ROW + 2 * (0x42 - 0x40)
ORIGINAL_STEPS = 0x2DC
# Lista órfã: $26018-$26087 (offsets $314/$34C) não é alcançada por nenhuma
# linha da tabela (13 personagens, comandos $40-$4F). São variantes do
# mesmo movimento (+ chute, + A+B), sobras do jogo. A 1ª (56 bytes) vira a
# lista nova.
NEW_TRACK = 0x026018
ORPHAN = ("ff080f00031c0000" "ff040a0003240000" "ff060a00032c0000" "ff020a0003340000"
          "ff0a0a00033c0000" "ff080a0003440000" "f0200a00ffff0000")
WINDOW = 20

# Cada passo é uma lista de alternativas de 6 bytes ([máscara][valor][prazo]
# [segurar][próximo]) terminada por máscara 0 ($1E05C). O leitor avança UM
# passo por frame ($1E048): no comando rápido, a última frente e o soco
# chegam no mesmo frame e o soco (evento de 1 frame) se perdia. Por isso
# há alternativas que fecham dois passos de uma vez.
END = "end"
STEPS = [  # lista de alternativas (máscara, valor, próximo passo)
    [(0x09, 0x08, 1)],                     # 0 frente sem cima: com cima, o passo
                                           #   aceito liga $A0E e bloqueia o pulo
                                           #   ($1D862); frente-cima tem que pular
    [(0x06, 0x06, 3),                      # 1 trás-baixo: trás e baixo juntos
     (0x04, 0x04, 2)],                     #   trás
    [(0x02, 0x02, 3)],                     # 2 baixo
    [(0xF8, 0x18, END),                    # 3 frente + soco no mesmo frame
     (0x08, 0x08, 4)],                     #   frente
    [(0xF0, 0x10, END)],                   # 4 soco
]


def track_bytes():
    starts, pos = [], NEW_TRACK
    for alts in STEPS:
        starts.append(pos)
        pos += len(alts) * 6 + 2
    out = bytearray()
    for alts in STEPS:
        for mask, value, nxt in alts:
            off = 0xFFFF if nxt == END else starts[nxt] - COMMANDS
            out += bytes([mask, value, WINDOW, 0]) + off.to_bytes(2, "big")
        out += b"\x00\x00"
    return bytes(out)


TRACK = track_bytes()

# Prioridade no mesmo frame: o leitor percorre os comandos $40 -> $4F e
# cada um completo grava $218 ($1E102, que arma $A77 = $3C). Feito rápido,
# -> <- v -> + soco também completa o Kohou ($47: -> v v> + soco; o 1º ->
# começa o Kohou e o v v> + soco chegam dentro do prazo), que vem depois do
# $42 e sobrescrevia o Haoh. Hook em $1E0E0 (comando completo, antes de
# gravar): Ryo, $218 = $42 gravado neste frame ($A77 = $3C) e o novo é o
# Kohou -> não grava. (O Kou'ouken, $40, vem antes do $42 na ordem.)
HAOH = 0x42
KOHOU = 0x47

keep_haoh = [
    Ins("0c6e00010062", "cmpi.w #$1, $62(a6)"),
    Branch("bne", "original"),
    Ins(f"0c45{KOHOU:04x}", f"cmpi.w #${KOHOU:x}, d5"),
    Branch("bne", "original"),
    Ins("0c2e003c0a77", "cmpi.b #$3c, $a77(a6)"),
    Branch("bne", "original"),
    Ins("302e0218", "move.w $218(a6), d0"),
    Ins("0240007f", "andi.w #$7f, d0"),
    Ins(f"0c40{HAOH:04x}", f"cmpi.w #${HAOH:x}, d0"),
    Branch("bne", "original"),
    JmpAbs(0x1E10C),                          # não grava (moveq #0,d0 / rts)
    Label("original"),
    Ins("302e0062", "move.w $62(a6), d0"),
    Ins("5340", "subq.w #$1, d0"),
    JmpAbs(0x1E0E6),
]

PATCH = Patch(
    id="haoh-easy-input",
    title="Ryo: Haoh Shoukouken com comando fácil (frente, trás, baixo, frente + soco)",
    spec="src/backend/specs/SPEC-021-ryo-haoh-easy-input.md",
    blocks=[Block("keep_haoh", keep_haoh)],
    hooks=[
        # $1E0E0: move.w $62(a6),d0 / subq.w #1,d0  (comando completo)
        Hook(addr=0x1E0E0, expect="302e00625340", to_block="keep_haoh"),
    ],
    data=[
        Data(NEW_TRACK, ORPHAN[:len(TRACK) * 2], TRACK.hex()),
        Data(HAOH_SLOT, f"{ORIGINAL_STEPS:04x}", f"{NEW_TRACK - COMMANDS:04x}"),
    ],
)
