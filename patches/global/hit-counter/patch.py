"""hit-counter — SPEC-013.

Contador de combo na tela ("2 HIT COMBO", "3 HIT COMBO"...), com a fonte do HUD do
jogo (a do "BEAT BY 0").

Por jogador, a cada frame (hook na atualização do jogador, $1B6A0):
  - oponente voltou a um estado livre ($40: neutro, andar, agachado,
    ataque, pulo, dash) -> combo acabou. (A v1 usava o fim da animação de
    reação, $A69 bit 7: golpes que prendem o oponente, como o Zanretsuken
    (estado $1F, animação em loop), ou que pegam no ar, como o 2º hit do
    Hien forte, zeravam o contador entre os hits.)
  - vida do oponente ($6C) caiu e não foi defesa ($7C & $F != 3, o mesmo
    teste de $21872) -> +1 no contador (BCD); começa em 1 se não havia combo
  - a partir de 2 hits: enfileira o registro "NN HIT COMBO" e arma 90 frames
  - fim do timer: enfileira um registro de espaços (apaga)

Texto: fila de tarefas do VBlank (-$5F8(a5), trava -$5F4(a5), executor
$0FD8). Registros: [parâmetro][comando]:
  cmd 2  REG_VRAMMOD = parâmetro         cmd 3  REG_VRAMADDR = word
  cmd 8  string em 2 linhas: tile (parâmetro<<8 | char), linha de baixo +$100
  cmd $10 número BCD da RAM: param $C1 = 2 dígitos, 2 linhas, zero à esquerda
          em branco; words: endereço, offset em a5, base do tile
  cmd 0  fim
Parâmetro $2D = paleta 2, tiles $D00+c / $E00+c: a fonte do "BEAT BY".

RAM: 8 bytes no registro de cada jogador, offset $3A0 (P1 $109620, P2
$109720). Nenhuma instrução usa os offsets $39B-$3DE do registro e eles
nunca mudaram numa sessão completa medida com tools/lua/ram_scan.lua.
(A 1ª versão usava $10EF80, fim da área de slots de objetos: o jogo
reiniciava ao apertar start na tela de título.)
  +0 contador BCD   +1 combo ativo   +2 timer   +4 vida anterior (word)
"""
from asm68k import Branch, Ins, JmpAbs, Label, LeaPc, Raw
from patchlib import Block, Hook, Patch

P1, P2 = 0x109280, 0x109380               # registros dos jogadores (a5+$1280/$1380)
FIELD = 0x3A0                             # 8 bytes livres no registro de cada jogador
RAM_OFFSET_A5 = {"p1": P1 + FIELD - 0x108000, "p2": P2 + FIELD - 0x108000}   # $1620 / $1720
SHOW_FRAMES = 90
AFTER_HOOK = 0x1B6A8
# Estados ($40) em que o oponente está livre: o combo acaba quando ele volta
# a um deles. 0/1/2 neutro e andar, 3 ataque, 4 pulo, 8 pulo (variante),
# $D/$E agachado, $10/$11 dash. Reação (6/7), "pegada" ($1F, Zanretsuken),
# queda e no ar continuam o combo.
FREE_STATES = sum(1 << st for st in (0, 1, 2, 3, 4, 8, 0xD, 0xE, 0x10, 0x11))

TILE = "2d"                               # paleta 2, fonte do HUD
LABEL = " HIT COMBO"                      # texto depois do número ("2 HIT COMBO")
WIDTH = 2 + len(LABEL)                    # colunas ocupadas (2 dígitos + texto)
ROW = 8


def fix_addr(col, row=ROW):
    """Endereço na camada fixa: $7000 + coluna*$20 + linha."""
    return 0x7000 + col * 0x20 + row


POS = {  # coluna do número; o texto começa 2 colunas depois
    "p1": 2,                              # colunas 2-13
    "p2": 38 - WIDTH,                     # termina na coluna 37 (borda visível)
}


def text(s):
    return s.encode("ascii").hex()


def string2(s):
    """Cmd 8 (2 linhas) + string + $FF, com 1 byte de enchimento se preciso:
    o handler ($11D6) realinha o registro para endereço par depois do $FF."""
    body = f"{TILE}08" + text(s) + "ff"
    return body + ("00" if (len(s) + 1) % 2 else "")


def show_record(side, ram_off):
    col = POS[side]
    return Raw(
        "2002"                                                       # VRAMMOD = $20
        + f"c110{fix_addr(col):04x}{ram_off:04x}{TILE}00"            # número BCD
        + f"0003{fix_addr(col + 2):04x}"                             # posição do texto
        + string2(LABEL)
        + "0000"                                                     # fim
    )


def clear_record(side):
    return Raw("2002" + f"0003{fix_addr(POS[side]):04x}" + string2(" " * WIDTH) + "0000")


tick = [
    Ins("4eb900022074", "jsr $22074.l"),           # instruções substituídas pelo hook
    Ins("4eb90001b7f2", "jsr $1b7f2.l"),
    Ins("48e7e0e0", "movem.l d0-d2/a0-a2, -(a7)"),
    Ins("206e0064", "movea.l $64(a6), a0"),          # oponente
    Ins(f"43ee{FIELD:04x}", f"lea.l ${FIELD:x}(a6), a1"),
    # Só roda com a luta montada: a6 e o oponente ($64) têm que ser os dois
    # jogadores. Na demo / transição do "press start" o $64 pode ser lixo
    # (endereço ímpar -> erro de endereço -> a BIOS reinicia o jogo).
    Ins(f"bdfc{P1:08x}", f"cmpa.l #${P1:x}, a6"),
    Branch("bne", "not_p1"),
    Ins(f"b1fc{P2:08x}", f"cmpa.l #${P2:x}, a0"),
    Branch("beq", "ok"),
    Branch("bra", "skip"),
    Label("not_p1"),
    Ins(f"bdfc{P2:08x}", f"cmpa.l #${P2:x}, a6"),
    Branch("bne", "skip"),
    Ins(f"b1fc{P1:08x}", f"cmpa.l #${P1:x}, a0"),
    Branch("bne", "skip"),
    Branch("bra", "ok"),
    Label("skip"),
    Ins("4cdf0707", "movem.l (a7)+, d0-d2/a0-a2"),
    JmpAbs(AFTER_HOOK),
    Label("ok"),
    # oponente defendendo ($7C & $F = 3) ou livre de novo -> combo acabou
    Ins("720f", "moveq #$f, d1"),
    Ins("c228007c", "and.b $7c(a0), d1"),
    Ins("0c010003", "cmpi.b #$3, d1"),
    Branch("beq", "reset"),
    Ins("7200", "moveq #$0, d1"),
    Ins("12280040", "move.b $40(a0), d1"),
    Ins("0c010020", "cmpi.b #$20, d1"),
    Branch("bcc", "check"),                          # estados altos: preso/no ar
    Ins(f"243c{FREE_STATES:08x}", f"move.l #${FREE_STATES:x}, d2"),
    Ins("0302", "btst.l d1, d2"),
    Branch("beq", "check"),
    Label("reset"),
    Ins("42290001", "clr.b $1(a1)"),
    Label("check"),
    Ins("3028006c", "move.w $6c(a0), d0"),
    Ins("b0690004", "cmp.w $4(a1), d0"),
    Branch("bcc", "store"),                          # vida não caiu
    Ins("720f", "moveq #$f, d1"),
    Ins("c228007c", "and.b $7c(a0), d1"),
    Ins("0c010003", "cmpi.b #$3, d1"),
    Branch("beq", "store"),                          # defesa: não conta
    Ins("4a290001", "tst.b $1(a1)"),
    Branch("bne", "more"),
    Ins("12bc0001", "move.b #$1, (a1)"),             # 1º hit
    Ins("137c00010001", "move.b #$1, $1(a1)"),
    Branch("bra", "store"),
    Label("more"),
    Ins("1211", "move.b (a1), d1"),
    Ins("0c010099", "cmpi.b #$99, d1"),
    Branch("beq", "show"),
    # ABCD soma tambem o flag X herdado da fisica/cancel. Limpa-o antes
    # de incrementar para que cada dano conte exatamente um hit.
    Ins("9402", "sub.b d2, d2"),
    Ins("7401", "moveq #$1, d2"),
    Ins("c302", "abcd.b d2, d1"),
    Ins("1281", "move.b d1, (a1)"),
    Label("show"),
    Ins(f"137c{SHOW_FRAMES:04x}0002", f"move.b #${SHOW_FRAMES:x}, $2(a1)"),
    LeaPc("show_p1", 2),
    Ins(f"bdfc{P1:08x}", f"cmpa.l #${P1:x}, a6"),
    Branch("beq", "show_go"),
    LeaPc("show_p2", 2),
    Label("show_go"),
    Branch("bsr", "enqueue"),
    Label("store"),
    Ins("33400004", "move.w d0, $4(a1)"),
    Ins("4a290002", "tst.b $2(a1)"),
    Branch("beq", "done"),
    Ins("53290002", "subq.b #$1, $2(a1)"),
    Branch("bne", "done"),
    LeaPc("clear_p1", 2),
    Ins(f"bdfc{P1:08x}", f"cmpa.l #${P1:x}, a6"),
    Branch("beq", "clear_go"),
    LeaPc("clear_p2", 2),
    Label("clear_go"),
    Branch("bsr", "enqueue"),
    Label("done"),
    Ins("4cdf0707", "movem.l (a7)+, d0-d2/a0-a2"),
    JmpAbs(AFTER_HOOK),
    # enfileira o registro em a2 na fila de texto do VBlank
    Label("enqueue"),
    Ins("522dfa0c", "addq.b #$1, -$5f4(a5)"),
    Ins("2f08", "move.l a0, -(a7)"),
    Ins("206dfa08", "movea.l -$5f8(a5), a0"),
    Ins("20ca", "move.l a2, (a0)+"),
    Ins("2b48fa08", "move.l a0, -$5f8(a5)"),
    Ins("205f", "movea.l (a7)+, a0"),
    Ins("532dfa0c", "subq.b #$1, -$5f4(a5)"),
    Ins("4e75", "rts"),
    Label("show_p1"), show_record("p1", RAM_OFFSET_A5["p1"]),
    Label("show_p2"), show_record("p2", RAM_OFFSET_A5["p2"]),
    Label("clear_p1"), clear_record("p1"),
    Label("clear_p2"), clear_record("p2"),
]

PATCH = Patch(
    id="hit-counter",
    title="Contador de combo na tela (N HIT COMBO) com a fonte do HUD",
    spec="src/backend/specs/SPEC-013-hit-counter.md",
    blocks=[Block("tick", tick)],
    hooks=[
        # $1B6A0: jsr $22074(pc) / bsr.w $1b7f2  ->  jmp tick
        Hook(addr=0x1B6A0, expect="4eba69d26100014c", to_block="tick"),
    ],
)
