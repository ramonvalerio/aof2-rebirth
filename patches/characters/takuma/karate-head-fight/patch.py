"""Takuma: máscara de tengu do Mr. Karate na luta ao escolher com START — SPEC-085.

Protótipo: guarda parada ($580, corpos $169E/$16A1/$16A4). Só a parte do rosto
da máscara do Mr. Karate do AOF1 (face vermelha, nariz longo, olho), espelhada
e alinhada pelo olho sobre o rosto do Takuma; o cabelo do Takuma fica.

Cada quadro de luta desenha gráficos (opcode $85 da peça); o decodificador
comum é $6364. Hook nele: quando o objeto `a6` é o sprite de um jogador
Takuma (registro: $62 = $A) com cor 1 e flag `$3DA` (global/start-select-flag),
o decodificador roda como sub-rotina e depois as colunas/linhas recém-escritas
na VRAM são relidas: tile do banco 1 que está em TABLE vira o tile novo (mesmo
atributo). A máscara usa os vermelhos 7-11 que já existem na paleta 0 da cor 1.

Tiles novos na C-ROM a partir de $11661 (sequência zerada $1165B-$116FF, banco
1). $11660 fica vazio e substitui as cabeças sobrepostas (normal e machucada),
que cobririam a máscara; o corpo já desenha o rosto por baixo.
"""
from asm68k import Branch, Dbra, Ins, JmpAbs, Label, LeaPc, Raw
from charlib import START_FLAG as FLAG
from patchlib import Block, Hook, Patch, RomData

TAKUMA = 0xA
P1_RECORD, P2_RECORD = 0x109280, 0x109380
BLANK_TILE = 0x11660

# Tile original (banco 1) -> tile novo (banco 1).
TABLE = [(0x1A405, 0x11661), (0x1A408, 0x11662), (0x1A409, 0x11663), (0x1A413, 0x11660), (0x1A414, 0x11660), (0x1A41D, 0x11664), (0x1A424, 0x11665), (0x1A425, 0x11666), (0x1A43F, 0x11660), (0x1A440, 0x11660), (0x1A449, 0x11667), (0x1A451, 0x11668), (0x1A452, 0x11669), (0x1A46C, 0x11660), (0x1A46D, 0x11660)]

# Tiles novos: 16 linhas de 16 índices (hex) cada.
TILES = {
    0x11661: ["0000000000000000", "0000000000000000", "5000000000077777", "1500000000088788", "1600000000000887", "6000000000008777", "0000000000065432", "0000000000643222", "0000000006432222", "6655000064322254", "3512600054322531", "2511606665443655", "2456654333335312", "234c432222336556", "34c4222222235321", "4643222222254231"],
    0x11662: ["0000000000000000", "0000000ccccc0000", "0000ccccc6ccc000", "00ccccc6cc6cccc0", "0cccc6c66c5cc6cc", "ccc6cc66566c656c", "cccc6c6c6c6656c6", "cc6cccccccc6c66c", "ccccc6cc6556c6cc", "c87c7777878abc6c", "87777777a788cccc", "877777778788c535", "a777777a887ccc52", "c7777aaa8778c662", "0878aac87787cc63", "0aaaac177877cc35"],
    0x11663: ["088788777777c546", "0777787778878563", "787a87a88aa8a463", "aa87a7aa778aa453", "777bbbb97b7aa553", "7777777b87aaa633", "2235633424234633", "2223554243456431", "2234511456654321", "4456456665543322", "2322644465433335", "6522543446454553", "3114352235655333", "5114436225533333", "1323435225333432", "1132344624333354"],
    0x11664: ["0000000000000000", "5000000000077777", "1500000000088788", "1600000000000887", "6000000000008777", "0000000000065432", "0000000000643222", "0000000006432222", "6655000064322254", "3512600054322531", "2511606665443655", "2456654333335312", "234c432222336556", "34c4222222235321", "4643222222254231", "cc43222222256542"],
    0x11665: ["0000000ccccc0000", "0000ccccc6ccc000", "00ccccc6cc6cccc0", "0cccc6c66c5cc6cc", "ccc6cc66566c656c", "cccc6c6c6c6656c6", "cc6cccccccc6c66c", "ccccc6cc6556c6cc", "c87c7777878abc6c", "87777777a788cccc", "877777778788c535", "a777777a887ccc52", "c7777aaa8778c662", "0878aac87787cc63", "0aaaac177877cc35", "088788777777c546"],
    0x11666: ["0777787778878563", "787a87a88aa8a463", "aa87a7aa778aa453", "777bbbb97b7aa553", "7777777b87aaa633", "2235633424234633", "2223554243456431", "2234511456654321", "4456456665543322", "2322644465433335", "6522543446454553", "3114352235655333", "5114436225533332", "1323435225333432", "1132344624333254", "3113334543322235"],
    0x11667: ["1600000000077777", "6000000000088788", "0000000000000887", "0000000000008777", "0000000000665432", "6655000006443222", "3512600064332254", "2511600054322531", "2456606665422655", "234c654333345312", "34c4232222336556", "4643222222235321", "cc43222222254231", "6543222222256542", "6543222222364311", "4643322233352311"],
    0x11668: ["0000ccccc6ccc000", "00ccccc6cc6cccc0", "0cccc6c66c5cc6cc", "ccc6cc66566c656c", "cccc6c6c6c6656c6", "cc6cccccccc6c66c", "ccccc6cc6556c6cc", "c87c7777878abc6c", "87777777a788cccc", "877777778788c535", "a777777a887ccc52", "c7777aaa8778c662", "0878aac87787cc63", "0aaaac177877cc35", "088788777777c546", "0777787778878563"],
    0x11669: ["787a87a88aa8a463", "aa87a7aa778aa453", "777bbbb97b7aa553", "7777777b87aaa633", "2235633424234633", "2223554243456431", "4456511456654321", "2322656665543322", "6522544465433335", "3114353446454553", "5114436235655333", "1323435225533332", "1132344625333432", "3113334524332254", "3221233463322235", "2112233356222223"]
}


def _encode(rows):
    px = [[int(ch, 16) for ch in row] for row in rows]
    a, b = bytearray(), bytearray()
    for x0, y0 in ((8, 0), (8, 8), (0, 0), (0, 8)):
        for y in range(8):
            planes = [0, 0, 0, 0]
            for x in range(8):
                v = px[y0 + y][x0 + x]
                for k in range(4):
                    planes[k] |= ((v >> k) & 1) << x
            a += bytes(planes[0:2])
            b += bytes(planes[2:4])
    return bytes(a), bytes(b)


def _rom_data():
    out = []
    for t, rows in TILES.items():
        pair, idx = divmod(t, 0x8000)
        odd, even = _encode(rows)
        out.append(RomData(f"056-c{pair * 2 + 1}.c{pair * 2 + 1}", idx * 64, "00" * 64, odd))
        out.append(RomData(f"056-c{pair * 2 + 2}.c{pair * 2 + 2}", idx * 64, "00" * 64, even))
    return out


TABLE_HEX = f"{len(TABLE) - 1:04x}" + "".join(f"{o & 0xFFFF:04x}{n & 0xFFFF:04x}" for o, n in TABLE)


def _player_check():
    """Sub-rotina: a0 = registro. Z=1 se a6 é o sprite de um Takuma marcado."""
    return [
        Label("check"),
        Ins(f"0c68{TAKUMA:04x}0062", f"cmpi.w #${TAKUMA:x}, $62(a0)"),
        Branch("bne", "no"),
        Ins("0c6800010276", "cmpi.w #$1, $276(a0)"),
        Branch("bne", "no"),
        Ins(f"4a28{FLAG:04x}", f"tst.b ${FLAG:x}(a0)"),
        Branch("beq", "no"),
        Ins("7000", "moveq #$0, d0"),
        Ins("10280003", "move.b $3(a0), d0"),           # slot do sprite do jogador
        Ins("e148", "lsl.w #$8, d0"),
        Ins("d08d", "add.l a5, d0"),
        Ins("b08e", "cmp.l a6, d0"),
        Ins("4e75", "rts"),
        Label("no"),
        Ins("7001", "moveq #$1, d0"),
        Ins("4e75", "rts"),
    ]


# $6364: move.w $a8(a5),d3 / add.w d6,$a8(a5)  (d3 = 1º sprite, d5 = linhas, d6 = colunas)
decoder = [
    Ins("362d00a8", "move.w $a8(a5), d3"),
    Ins("dd6d00a8", "add.w d6, $a8(a5)"),
    Ins("48e78080", "movem.l d0/a0, -(a7)"),
    Ins(f"41f9{P1_RECORD:08x}", f"lea.l ${P1_RECORD:x}.l, a0"),
    Branch("bsr", "check"),
    Branch("beq", "go"),
    Ins(f"41f9{P2_RECORD:08x}", f"lea.l ${P2_RECORD:x}.l, a0"),
    Branch("bsr", "check"),
    Branch("beq", "go"),
    Ins("4cdf0101", "movem.l (a7)+, d0/a0"),
    JmpAbs(0x636C),
    *_player_check(),
    Label("go"),
    Ins("4cdf0101", "movem.l (a7)+, d0/a0"),
    Ins("48e71600", "movem.l d3/d5-d6, -(a7)"),
    Ins("4eb90000636c", "jsr $636c.l"),
    Ins("4cdf0068", "movem.l (a7)+, d3/d5-d6"),
    Ins("48e7fff8", "movem.l d0-d7/a0-a4, -(a7)"),
    Ins("45f9003c0000", "lea.l $3c0000.l, a2"),
    Ins("357c00010004", "move.w #$1, $4(a2)"),          # VRAMMOD = 1
    LeaPc("table", 3),
    Ins("3845", "movea.w d5, a4"),                       # linhas
    Ins("5346", "subq.w #$1, d6"),
    Label("col"),
    Ins("3803", "move.w d3, d4"),
    Ins("ed4c", "lsl.w #$6, d4"),                        # SCB1 do sprite
    Ins("340c", "move.w a4, d2"),
    Ins("5342", "subq.w #$1, d2"),
    Label("row"),
    Ins("3484", "move.w d4, (a2)"),
    Ins("302a0002", "move.w $2(a2), d0"),                # tile (16 bits baixos)
    Ins("3204", "move.w d4, d1"),
    Ins("5241", "addq.w #$1, d1"),
    Ins("3481", "move.w d1, (a2)"),
    Ins("322a0002", "move.w $2(a2), d1"),                # atributo
    Ins("3a01", "move.w d1, d5"),
    Ins("024500f0", "andi.w #$f0, d5"),
    Ins("0c450010", "cmpi.w #$10, d5"),                  # banco 1 (tiles do Takuma)
    Branch("bne", "next"),
    Ins("224b", "movea.l a3, a1"),
    Ins("3a19", "move.w (a1)+, d5"),                     # quantidade - 1
    Label("search"),
    Ins("b059", "cmp.w (a1)+, d0"),
    Branch("beq", "found"),
    Branch("bcs", "next"),                               # tabela em ordem crescente
    Ins("5489", "addq.l #$2, a1"),
    Dbra(5, "search"),
    Branch("bra", "next"),
    Label("found"),
    Ins("3484", "move.w d4, (a2)"),
    Ins("35510002", "move.w (a1), $2(a2)"),              # tile novo (atributo mantido)
    Label("next"),
    Ins("5444", "addq.w #$2, d4"),
    Dbra(2, "row"),
    Ins("5243", "addq.w #$1, d3"),
    Dbra(6, "col"),
    Label("out"),
    Ins("4cdf1fff", "movem.l (a7)+, d0-d7/a0-a4"),
    Ins("4e75", "rts"),
    Label("table"),
    Raw(TABLE_HEX),
]

PATCH = Patch(
    id="karate-head-fight",
    title="START na seleção: máscara de tengu na luta (protótipo: parado)",
    spec="src/backend/specs/SPEC-085-takuma-karate-head-fight.md",
    blocks=[Block("fight_head", decoder)],
    hooks=[Hook(0x6364, "362d00a8dd6d00a8", to_block="fight_head")],
    rom_data=_rom_data(),
)
