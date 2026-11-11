"""Takuma: START na seleção mostra o Mr. Karate (AOF1) no retrato — SPEC-084.

`global/start-select-flag` confirma START como B (cor 1) e liga `$3DA`.
O retrato grande do Takuma é o gráfico $0DF2 (8x8 tiles, formato $18 em
$7EAA: atributo, 1º tile, 1 byte de máscara por coluna, tiles em sequência
pulando os que terminam em $00); a animação alterna $0DF2-$0E03.

Com flag e cor 1, o retrato do cursor confirmado usa GRAPHIC abaixo: o retrato
do Mr. Karate do AOF1 (C-ROM do aof, tiles $3510-$354F, 6x8), centralizado,
em tiles novos da C-ROM a partir de $DEA0 (sequência zerada $DE9C-$DEFF),
espelhado para olhar para a esquerda, como o retrato original do Takuma.
A tela do AOF1 é sépia; as cores foram montadas pelas rampas do desenho
(cinza: cabelo/barba; quente: pele -> máscara vermelha) com as cores do
Mr. Karate na luta. As paletas 5-6 do retrato vêm do bloco mágico $FD.
"""
from asm68k import Branch, Ins, JmpAbs, Label, LeaPc, Raw
from charlib import (ENEMY_PORTRAIT, PORTRAIT_PALETTE, SELECT_PORTRAIT, START_FLAG as FLAG,
                     shared_hook, start_portrait, start_portrait_palette)
from patchlib import Block, Hook, Patch, RomData

MAGIC = 0xFD
TAKUMA_BLOCK = 0x47           # tabela $C96C: cores 0/1 no bloco $47
FIRST_TILE = 0xDEA0           # banco 0 (atributo $8500, como o original)
PORTRAIT_GRAPHICS = (0x0DF2, 0x0E03)
COLUMNS, ROWS = 8, 8
LEFT = 1                      # arte de 6 colunas nas colunas 1-6

# Retrato do Mr. Karate (AOF1 $3510-$354F), 96x128, espelhado; índices da paleta abaixo.
ART = [
    "................................................................................................",
    "................................................................................................",
    "..........................................d...................2.................................",
    "..........................................1.......1122.....d12.......d11........................",
    ".........................................d1.....d122....dd12.....dd1122.........................",
    ".........................................12...d122...fdd12...fd11222............................",
    "........................................d22..d122..fd122ffd112222...11dddd11123.................",
    "..................................d....f122.d122ffd12fff222222111ddddddd1112222223..............",
    "..................................d...f122.f12fd122fdddddddddddd1111111222223311123.............",
    ".................................d1..f1222f1ff122fdd11111111111112222222333111ddddd23...........",
    ".................................d2..d122f1fd122fd1112222222222222233333311dddd11ddd23..........",
    "................................d12.f122fd1f122fd1122233ffddd1111333ffd11dd111111111122.........",
    "................................d22.f122f1fd122fd12223fdd11222333ffdddddd1112221ddddd1123.......",
    "...............................d1231d12f12f122fd11223fd1222333ffddd11111122222111111dd1323......",
    "...............................d123d122f12f122fd12233f12333ffd111122222222221122222111d2322.....",
    "...............................d223d12fd22d121dd12233d123ddd1122fddd222222222222222222113322....",
    "...............................1233d12d122d1212d12233122d1122ffdddddddddd22333333333322123332...",
    "...............................1233112d12221212dd123312d1123fdd1111111ddddddddd3333333221233332.",
    "...............................12332121122312212d122332d1233d1122222222222211111111333332223....",
    "...............................2223212312232121222122321123dd12233333333332222222221133333223...",
    ".............................dd1123321321232122123212331223d122333333333333333333322213333323...",
    "...........................dd112212321232123212312323332123d12333333333d1122222233332233333332..",
    "..........................d122333333321232233212323333332331223333333dd112233333333333233333332.",
    ".........................d12....223333212332333333333333333333333333d112333333333333333333332332",
    "........................d1........223333331333333bbbaaaaaaa2333333331223333333333333333333233233",
    "........................1.....11123333332d12322277666666667aaa23333323333331dd1122333333333232.3",
    ".......................1....122223333333d123312769999966667777aaa333333331122333332233333333232.",
    ".......................2...22...12332123d123d27699ff996666777777aa77556712233333333322333333233.",
    "..........................2....12232123d1237d269ffff9966667777777aaa755567112223333333333333323.",
    ".........................2....122321233d1377126fffff9966677d77777aaaa7445622dfd3333333333333323.",
    ".............................122.12123ad1376126fffff9966d7dda7777aa7aa745611222dd13333333333332.",
    ".............................12.12.123a12366126ffff9996dfdf1a7777a767aa756711d13331223333333332.",
    "............................122.12.23aa123666129fff9f6dddfd12a77aa6667aa667111ddd133322233333332",
    "............................12..2.123aaa23669126fff9f7dfdf123a77a76667aa667d12111dd1133333333232",
    "............................22.12.123aa7236696129f9ffffffd23b77aa66667ab677dd122333222233333332.",
    "............................2..22.2.3aa7722699626f9ffffd113ba7aba66667ab6771dd12223333322333332.",
    "...........................12..2..2.3aa769269f966d9ffdd123ba77aaa66667ab777111211122223332333332",
    "...........................2...2..2.1a776f626ff99dddffdd332b7abaa76667ab777122332333332233333332",
    "..........................2....2...2da769f966ff96dffd112bbaaaba7a7667ab331dffd22365c453333333333",
    "...................................11a76ff999f96ddd123332a7aba767a667ab3221112335cc44c53333332.3",
    "...................................21a76f9999f9fdfd132bba7aba6997a767ab788833335c4555c45333332..",
    "...................................221a6f996f96d1d233bbaaaba69997a77aab67781336c457776c4333332..",
    "....................................22a79967961dd133baaabba699967aa7abb56772124458887644333332..",
    "....................................32a7966767fd13bbaabbba7999967aaabbb456612345677665453333332.",
    "....................................3327667a77d113bab556aa699967a69967a445561256888764563333332.",
    ".....................................32a777baa123bb3ccc5a769967a69fff96a44552858888874573333332.",
    "......................................3ba7aabb23bb333cc5a76667aa9ffff96674453768765774633333332.",
    "......................................33baabbb2bb3333cc6aa777a69fffff9667444c448866664433333332.",
    "......................................633bbbbbbbc333cc579996999ffffff976aa554cc4888555633333332.",
    ".......................................33bbbbaabbccc5579fffff9699fff96a6ab5654c48788557333333332",
    ".....................................999fff99776675579ffffff99669fff97a67b6665447785463333333332",
    ".................................9999ffff999699996779fffffff99679ff967b67b676658767c573332333332",
    ".............................9999fffff99996699fff9679ffffff9996769f96ab77b677668665c633232333323",
    ".........................999fffff9999999666799fff96769999999967a69f67aba7b77766765c57332323332.3",
    "........................66ffff9999996666777a99fff67a7999999967aa66677abbab777765c4563322323332..",
    "........................77666666666667777aaa766667aa776666677aaa7777aabbb777775445733312323332e1",
    "........................6777777777777aaaaaaa33b77aabba77777aaaaa77aaabaab7767765563323123333332e",
    "........................677aaaaaaaaaaaaaaaa3333aaabbbbaaaaaaaab77aaabb7ab66678767333231233333322",
    ".........................67aaaaaaaaaaa7...7aabbbbbbbbbbbaaaabbbbbbbbba7ab55678333333231233333322",
    "...........................77aaaaa7......1667711222bbbbbbbbbbbaaabbba77b65567b333323331323233332",
    "........................................d69967b1121212bbbbaaa7777abba77b55667b332323b22323233332",
    "....................................e1.ed7aaaaab211d1d21aaa7766667bba77b56667b232233b12323233332",
    "....................................e1ed123223333212d1fda777699967aba7ab66678b232233b13b2323333e",
    "...................................2eed2236999962321211f1766779967aba7bb6667bb122333b13b232333e1",
    "...................................22ed2336999666a323121d339677967ab77bb7678bb1b233b123b23233e1d",
    "....................................21e23e6666677aab32121d3297a667ab77b7778bbb1b133b23bb2323e1dd",
    ".................................77721e23277777aaabbb321372197a77abb7ab778b8bb1b133b23bb333e1dd1",
    "...............................77766e1e22e2aaaaaabbba232376667baabbb7bb78b888b2b13bbb3bbbee1ddd1",
    ".............................6644556711ee333bbbbbba77ab22a777abbbbba7bb8b8788b2b23bbb3bbe11ddd1e",
    "............................644444557e11e233bbaaaa7666abbbbbbbbbbba7bbbb87778b3b2338b3be1dfd11e2",
    "..........................66ccc4e1111e11e3e1aa77aa7666677abbbbbbba7bbb8876788838b2388be1dfd11ee3",
    "........................66cccccc4eee11e12ed1abbb1baa7666abb1bbbaaabbb887656788b8b2388edd11111e33",
    ".......................6cccccccc421ee323ed12b11bdbbdbaaabb12bb1babbb888765678888bbbeedffd111e322",
    "......................6ccccccccc44e1e233dd131d221db1bbbbb112bb21bbb88876556788888bedffdd11eee223",
    ".....................65ccccccccc4421e233d113d2132212b1b1b1232b31bb888876556778888e1dddd11e12123e",
    "....................6c4ccccccccc4e21e23df123d1132d22b1b121232332888887655667788e1111e1111ed22122",
    "...................64c4cccccccc44e21e23df1321f113d2b122333323312888887655667881dddd1ee12e2d23232",
    "..................644ccccccccc44eee212dfd1f2fd1d11212f1232313212888876555677e1dffd1e2212e2d22323",
    ".................6544cccccccc444e11e12df12f2fd2d2222f1d13d213122888876555671ddffdd11e2132e123232",
    ".................65444ccccc44444211e1edd1fd2fd3d2d12ddd13d1d212278887655671ddffdd11e212323232335",
    "................655444444444444521e11dfd2fdfd1312d1fdfd12d1d11277887655561ddffdd11e221333233355c",
    "................655444444444455562ee1dfd2fdfd132dd1f1fd11d1d1128778765661dffdd11ee22d233333355cf",
    "...............75555444444c45555222e11d2dddfd131fd1f1fd11dd1122877776611dffd111e2222123333554cff",
    "...............755555544457c55562e2e12d2fdfd113dfd1f1fd11dd12228877761dfffd11ee2222d1233354ccfff",
    "...............7555555555574556ee1211212fdfd113fdd1d2fd111d1238887771dfffd1e1e222211233354ccffff",
    "..............76655555555565667e1121113fd1fd132fd1112fd111d123887771dfffd1e12e22212233354cccffff",
    "..............7666555555566567e11122e23fd1fd132fd1212dd112d23287711dfffd1e2122e112233354ccccffff",
    ".............7766666666666577e1d1222e13d12fd133fd12121d1121238871ddfffd1ee21232322333544cccccfff",
    ".............77765556666667771dd1ee3213d13dd133dd12221d121123871dffffd1ee222123233333544ccccccff",
    ".............76555555566777711d1ee23213113dd133d113212113132381dffffd1ee2222d32333335444cccccccc",
    "............6544444455667771dd1e1e332131331d123d12321311313231dfffdd1ee222e2d232333654444ccccccc",
    "..........6644cccccc45566711d1111e231d32331d12311232131232331dfffd1eee222e2e12233335544444cccccc",
    "........664ccccccccc455667e111d1ede31d1332211231133223123331dfffd1ee222ee2e1223333655444444ccccc",
    ".......64ccccccccccc45566eee1d11de21dd133131113213322322331dfffd1ee222e11ee122333365544444444444",
    "......64cccccccccccc455611e1dd1dee21d1e3313212231323232331dfffd1ee222e11ee1223333765554444444444",
    ".....64cccccccccccc44551d1edf1fde21d1e2e33132123132333231dfffd1ee222e1eeed2233333766555444444444",
    "....64cccccccccccc44556d1e1fd1fee21d1e2bb233223323233331dfffd1ee2222e12de22333337666555544444444",
    "...644c4cccccccc4cc5561de1ddedde21d1e2bbbb2332322233331dfffd1ee22e2e1e12123233337666655554444444",
    "..644c5fccccccccc5c566ede1de1dee2dd1ebbaabb23233123331dfffd1ee22e12ed1d3232333337766665555555555",
    "..6cc7fccccccccc446561d1e1e1dde2ed1e2baabbbb233322331dfffd1ee22e11e1d1d3323333337777666665555555",
    ".65c664cccccc44445661ed1ee21dee21d1ebba797bbb2233331dfffd1ee22e1d11df1d3332333377777766666656666",
    "65564c544444444445561e11e21d1e2e1d1ebaa76997ab23331dfffd1ee22e1d1f1dfd1e323333377776556665555556",
    "656444c4444444445566ee1ee111ee21dde2ba6aaaaabbb2b1dfffd1ee22e1d1dfdfdd1e33333337775544565544ccc5",
    "65555544444444555562e21e211ee221d1ebb769abbbbbbbbffffd11e22e1d1dffdfd1ee3333336655ccc44544cccccc",
    "66555555555555555662e2ee211ee2e1de2bb776996677a1dfffd11e2ee1d1dffdffd12333336554ccffcc4444cccfff",
    "6665555555555556662ee2ee21e2e2e1debabbbb7777aa1dfffd1ee22e1dfdffd1ffde23333654cccfffcc4444cfffff",
    "6666666655666666662e232e21e2e3e11ebbaabbbbbbbbddfd11e222e1dddffd1edf1e2333654ccccffccc444cfffffc",
    "66666666666666666622232e212223e1e2b76aaaaabbb1dfd11ee22e1dd1dfdd1e1de2333654ccc4cffcc444ccfffffc",
    "666666666666777777aa33323e2233eeebbb7699667aeddd1ee222e1dd111fd1e2ee7665664ccc4ccffcc44ccffccccc",
    "666666666776699996677a333222332e2baab7777bbe1d11e2222ee1d11e1d1e2276544cc56ccc4ccfcc444ccfcccc44",
    "7776666776667677999967a3332333222bababbbbabe111e22222e1d1ee3e77777776544cc565c44cfcc44cccccc4444",
    "77777aa766777a6667766677aa3333332bbaaaaaabe1e2ee2232e1d1ee33754cc57766544cc46544ccc444cccc444445",
    "7788aaa767aa6677aaa7777777aa776655556677bbee1121e33ee11e2237654ccc47776544cc4654cc4454ccc4444555",
    "888aab77aba67aaaaa77554445555444444455556671eee2232e1ee233777654ccc4777654ccc4654445544c44444555",
    "88bab7aaba77abba7755444ccc444ccccccccc444567222333ee1e27777777654ccc4777654ccc465455544444455556",
    "8babbaabb7aabba7755444444ccccccfffffffccc445673332e2e2754cc5777654ccc47776544cc46455444445555566",
    "bbabaabbaabbbaa75555477654ccccffffffffffccc44567323327544ccc5777654ccc4877654ccc6555444555566677",
    "bbbbaabbabbbaa75555566cccc4cccccffffffffffcc4455333777654cccc5777654ccc4877654446654445556667777",
    "bbbbabbaabbba75555564444444444cccfffffffffffcc4563766576654ccc5777654ccc587766555744455566777776",
    "bbbbbbbabbbbb755655555554444444ccccfffffffcccc44567654577654ccc5777654cc587766555754555667777766",
    "bbbbbbbabbbbaa455665555554444444ccccccccccccccc445754cc577654ccc58776544468776555765556677777665",
    "67bbbbbbbbbaa544456666655554444444cccccccccccc44467654cc577654ccc5877655667876557775566777776665",
    "567bbbbbbbba6544455677776655544444444ccccccc4445577765ccc577654cc4887776556877765675667777766655",
    "c456bbbbbbaa6654444567777765555444444444444445555777654cc457765446687765556877655576677777766555",
    "cc4567bbbba86765444456777776665555544444445555566787765ccc47766665688776567887665576777777665556",
    "44c4567bbba8677655444566677776665555555555556666678877644466776555568776655687765677777777665566",
    "54444567bbb8877666555555667777766665556666667777788887766655777655568877655688777777777777665566",
    "555444567bb8887766666555566677777766666677777777788887765555677765668877766688887777777777666667",
]

# R, G, B de 6 bits (pares). 1-3/13-15 cinza; 12,4,5 pele; 6,7,10,11,8 máscara; 9 brilho.
PALETTE = [(0, 0, 0), (28, 28, 30), (16, 16, 18), (6, 6, 8), (58, 44, 32), (52, 34, 24), (52, 18, 10), (44, 12, 6), (14, 2, 2), (62, 30, 18), (34, 6, 4), (24, 4, 2), (62, 54, 44), (50, 50, 50), (38, 38, 38), (62, 62, 60)]


def _tile(cx, cy):
    """Pixels 16x16 da célula (cx, cy) do retrato 8x8 (None se vazia)."""
    ax = cx - LEFT
    if not 0 <= ax < 6:
        return None
    px = [[int(ART[cy * 16 + y][ax * 16 + x].replace(".", "0"), 16) for x in range(16)]
          for y in range(16)]
    return px if any(any(r) for r in px) else None


def _encode(px):
    """Tile da C-ROM: (bytes do arquivo ímpar, bytes do par). Blocos 8x8:
    0 = dir. topo, 1 = dir. base, 2 = esq. topo, 3 = esq. base; por linha,
    planos 0/1 no c ímpar e 2/3 no par; bit 0 = pixel da esquerda."""
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


def _layout():
    masks, tiles, t = [], [], FIRST_TILE
    for cx in range(COLUMNS):
        m = 0
        for cy in range(ROWS):
            px = _tile(cx, cy)
            if px is not None:
                m |= 0x80 >> cy
                tiles.append((t, px))
                t += 1
                assert t & 0xFF, "a sequência não pode cruzar $xx00"
        masks.append(m)
    return masks, tiles


MASKS, TILES = _layout()
GRAPHIC = f"8500{FIRST_TILE:04x}" + "".join(f"{m:02x}" for m in MASKS)


def _rom_data():
    out = []
    for t, px in TILES:
        pair, idx = divmod(t, 0x8000)
        odd, even = _encode(px)
        out.append(RomData(f"056-c{pair * 2 + 1}.c{pair * 2 + 1}", idx * 64, "00" * 64, odd))
        out.append(RomData(f"056-c{pair * 2 + 2}.c{pair * 2 + 2}", idx * 64, "00" * 64, even))
    return out


PALETTE_HEX = "".join(f"{r:02x}{g:02x}{b:02x}" for r, g, b in PALETTE) * 2


def _is_portrait(cursor):
    """Cursor confirmado, a6 é um objeto do retrato dele e o registro tem flag + cor 1."""
    return [
        Ins(f"43ed{cursor:04x}", f"lea.l ${cursor:x}(a5), a1"),
        Ins("4a29003e", "tst.b $3e(a1)"),
        Branch("beq", f"no_{cursor:x}"),
        Ins("7000", "moveq #$0, d0"),
        Ins("10290034", "move.b $34(a1), d0"),          # retrato ($C436, índice $C)
        Ins("e148", "lsl.w #$8, d0"),
        Ins("d08d", "add.l a5, d0"),
        Ins("b08e", "cmp.l a6, d0"),
        Branch("beq", f"obj_{cursor:x}"),
        Ins("7000", "moveq #$0, d0"),
        Ins("1029003c", "move.b $3c(a1), d0"),          # segundo objeto ($C436, índice $10)
        Ins("e148", "lsl.w #$8, d0"),
        Ins("d08d", "add.l a5, d0"),
        Ins("b08e", "cmp.l a6, d0"),
        Branch("bne", f"no_{cursor:x}"),
        Label(f"obj_{cursor:x}"),
        Ins("2269001c", "movea.l $1c(a1), a1"),
        Ins(f"4a29{FLAG:04x}", f"tst.b ${FLAG:x}(a1)"),
        Branch("beq", f"no_{cursor:x}"),
        Ins("0c6900010276", "cmpi.w #$1, $276(a1)"),
        Branch("beq", "found"),
        Label(f"no_{cursor:x}"),
    ]


# $5226: leitura de $CA/$CB e do id do gráfico (opcode $85 da lista de sprite).
graphic = [
    Ins("1b5800ca", "move.b (a0)+, $ca(a5)"),
    Ins("1b5800cb", "move.b (a0)+, $cb(a5)"),
    Ins("1a98", "move.b (a0)+, (a5)"),
    Ins("3815", "move.w (a5), d4"),
    Ins("1818", "move.b (a0)+, d4"),
    Ins("02840000ffff", "andi.l #$ffff, d4"),
    Ins(f"0c44{PORTRAIT_GRAPHICS[0]:04x}", f"cmpi.w #${PORTRAIT_GRAPHICS[0]:x}, d4"),
    Branch("bcs", "normal"),
    Ins(f"0c44{PORTRAIT_GRAPHICS[1]:04x}", f"cmpi.w #${PORTRAIT_GRAPHICS[1]:x}, d4"),
    Branch("bhi", "normal"),
    *_is_portrait(0x1E80),
    *_is_portrait(0x1F80),
    Label("normal"),
    JmpAbs(0x523A),
    Label("found"),
    LeaPc("graphic", 1),
    Ins("3b7c180000c6", "move.w #$1800, $c6(a5)"),     # formato $18
    Ins("7a08", "moveq #$8, d5"),
    Ins("7c08", "moveq #$8, d6"),
    Ins("4e75", "rts"),
    Label("graphic"),
    Raw(GRAPHIC),
]

PATCH = Patch(
    id="karate-mask-start",
    title="START na seleção: retrato do Mr. Karate (AOF1)",
    spec="src/backend/specs/SPEC-084-takuma-karate-mask-start.md",
    blocks=[Block("portrait_graphic", graphic),
            Block("select_portrait", start_portrait(TAKUMA_BLOCK, MAGIC, SELECT_PORTRAIT)),
            Block("enemy_portrait", start_portrait(TAKUMA_BLOCK, MAGIC, ENEMY_PORTRAIT)),
            Block("portrait_palette", start_portrait_palette(MAGIC, PALETTE_HEX))],
    hooks=[
        Hook(0x5226, "1b5800ca1b5800cb1a9838151818", to_block="portrait_graphic"),
        shared_hook(SELECT_PORTRAIT, "select_portrait"),
        shared_hook(ENEMY_PORTRAIT, "enemy_portrait"),
        shared_hook(PORTRAIT_PALETTE, "portrait_palette"),
    ],
    rom_data=_rom_data(),
)
