"""Takuma: START na seleção mostra o Mr. Karate (AOF1) no retrato — SPEC-084.

`global/start-select-flag` confirma START como B (cor 1) e liga `$3DA`.
O retrato grande do Takuma é o gráfico $0DF2 (8x8 tiles, formato $18 em
$7EAA: atributo, 1º tile, 1 byte de máscara por coluna, tiles em sequência
pulando os que terminam em $00); a animação alterna $0DF2-$0E03.

Com flag e cor 1, o retrato do cursor confirmado usa GRAPHIC abaixo: o retrato
do Mr. Karate do AOF1 (C-ROM do aof, tiles $3510-$354F, 6x8), centralizado,
em tiles novos da C-ROM a partir de $DEA0 (sequência zerada $DE9C-$DEFF).
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

# Retrato do Mr. Karate (AOF1 $3510-$354F), 96x128, índices da paleta abaixo.
ART = [
    "................................................................................................",
    "................................................................................................",
    ".................................2...................d..........................................",
    "........................11d.......21d.....2211.......1..........................................",
    ".........................2211dd.....21dd....221d.....1d.........................................",
    "............................22211df...21ddf...221d...21.........................................",
    ".................32111dddd11...222211dff221df..221d..22d........................................",
    "..............3222222111ddddddd111222222fff21dff221d.221f....d..................................",
    ".............3211133222221111111ddddddddddddf221df21f.221f...d..................................",
    "...........32ddddd11133322222221111111111111ddf221ff1f2221f..1d.................................",
    "..........32ddd11dddd1133333322222222222222111df221df1f221d..2d.................................",
    ".........221111111111dd11dff3331111dddff3322211df221f1df221f.21d................................",
    ".......3211ddddd1222111ddddddff33322211ddf32221df221df1f221f.22d................................",
    "......3231dd11111122222111111dddff3332221df32211df221f21f21d1321d...............................",
    ".....2232d111222221122222222221111dff33321f33221df221f21f221d321d...............................",
    "....223311222222222222222222dddf2211ddd321d33221dd121d22df21d322d...............................",
    "...23332122333333333322ddddddddddff2211d22133221d2121d221d21d3321...............................",
    ".2333321223333333ddddddddd1111111ddf3211d213321dd21212221d2113321...............................",
    "....3222333331111111122222222222211d3321d233221d21221322112123321...............................",
    "...32233333112222222223333333333221dd3211232212221212322132123222...............................",
    "...323333312223333333333333333333221d3221332123212212321231233211dd.............................",
    "..2333333322333322222211d33333333321d321233323213212321232123212211dd...........................",
    ".233333332333333333332211dd333333322133233333323212332232123333333221d..........................",
    "233233333333333333333333211d333333333333333333333333233212333322....21d.........................",
    "3323323333333333333333333221333333332aaaaaaabbb333333133333322........1d........................",
    "3.2323333333332211dd13333332333332aaa76666666677222321d23333332111.....1........................",
    ".232333333332233333221133333333aaa777766669999967213321d333333322221....1.......................",
    ".33233333322333333333221765577aa777777666699ff99672d321d32123321...22...2.......................",
    ".323333333333333322211765557aaa7777777666699ffff962d7321d32123221....2..........................",
    ".3233333333333333dfd2265447aaaa77777d7766699fffff6217731d332123221....2.........................",
    ".23333333333331dd222116547aa7aa7777add7d6699fffff6216731da32121.221.............................",
    ".23333333332213331d117657aa767a7777a1fdfd6999ffff62166321a321.21.21.............................",
    "233333332223331ddd111766aa7666aa77a21dfddd6f9fff921666321aa32.21.221............................",
    "2323333333311dd11121d766aa76667a77a321fdfd7f9fff62196632aaa321.2..21............................",
    ".233333332222333221dd776ba76666aa77b32dffffff9f9216966327aa321.21.22............................",
    ".23333322333332221dd1776ba76666aba7ab311dffff9f6269962277aa3.2.22..2............................",
    "233333233322221112111777ba76666aaa77ab321ddff9d669f962967aa3.2..2..21...........................",
    "233333332233333233221777ba76667aaba7b233ddffddd99ff626f677a1.2..2...2...........................",
    "333333333354c56322dffd133ba7667a7abaaabb211dffd69ff669f967ad2...2....2..........................",
    "3.23333335c44cc5332111223ba766a767aba7a233321ddd69f999ff67a11...................................",
    "..23333354c5554c533338887ba767a7996aba7abb231dfdf9f9999f67a12...................................",
    "..2333334c677754c63318776baa77a79996abaaabb332d1d69f699f6a122...................................",
    "..23333344678885442127765bba7aa769996abbaaab331dd16976997a22....................................",
    ".233333354566776543216654bbbaaa7699997abbbaabb31df7676697a23....................................",
    ".233333365467888652165544a76996a769996aa655bab311d77a7667233....................................",
    ".23333337547888885825544a69fff96a769967a5ccc3bb321aab777a23.....................................",
    ".23333333647756786735447669ffff9aa76667a5cc333bb32bbaa7ab3......................................",
    ".233333334466668844c4447669fffff96a777aa6cc3333bb2bbbaab33......................................",
    ".2333333365558884cc455aa679ffffff999699975cc333cbbbbbbb336......................................",
    "23333333375588784c4565ba6a69fff9969fffff9755cccbbaabbbb33.......................................",
    "2333333333645877445666b76a79fff96699ffffff97557667799fff999.....................................",
    "233333233375c767856676b76b769ff97699fffffff977699996999ffff9999.................................",
    "323333232336c566866776b77ba69f9676999ffffff9769fff99669999fffff9999.............................",
    "3.23332323375c56766777b7aba76f96a76999999996769fff9976669999999fffff999.........................",
    "..2333232233654c567777babba77666aa7699999997a76fff99a7776666999999ffff66........................",
    "1e233323213337544577777bbbaa7777aaa776666677aa766667aaa77776666666666677........................",
    "e2333333213233655677677baabaaa77aaaaa77777abbaa77b33aaaaaaa7777777777776........................",
    "22333333213233376787666ba7bbaaa77baaaaaaaabbbbaaa3333aaaaaaaaaaaaaaaa776........................",
    "22333333213233333387655ba7abbbbbbbbbaaaabbbbbbbbbbbaa7...7aaaaaaaaaaa76.........................",
    "233332323133323333b76556b77abbbaaabbbbbbbbbbb2221177661......7aaaaa77...........................",
    "23333232322b323233b76655b77abba7777aaabbbb2121211b76996d........................................",
    "23333232321b332232b76665b77abb7666677aaa12d1d112baaaaa7de.1e....................................",
    "e3333232b31b332232b87666ba7aba769996777adf1d212333322321de1e....................................",
    "1e333232b31b333221bb7666bb7aba7699776671f1121232699996322dee2...................................",
    "d1e33232b321b332b1bb8767bb77ba769776933d121323a6669996332de22...................................",
    "dd1e3232bb32b331b1bbb8777b77ba766a7923d12123baa7766666e32e12....................................",
    "1dd1e333bb32b331b1bb8b877ba7bba77a791273123bbbaaa77777232e12777.................................",
    "1ddd1eebbb3bbb31b2b888b87bb7bbbaab766673232abbbaaaaaa2e22e1e66777...............................",
    "e1ddd11ebb3bbb32b2b8878b8bb7abbbbba777a22ba77abbbbbb333ee1176554466.............................",
    "2e11dfd1eb3b8332b3b87778bbbb7abbbbbbbbbbba6667aaaabb332e11e755444446............................",
    "3ee11dfd1eb8832b8388876788bbb7abbbbbbba7766667aa77aa1e3e11e1111e4ccc66..........................",
    "33e11111dde8832b8b887656788bbbaaabbb1bba6667aab1bbba1de21e11eee4cccccc66........................",
    "223e111dffdeebbb888876567888bbbab1bb21bbaaabdbbdb11b21de323ee124cccccccc6.......................",
    "322eee11ddffdeb88888765567888bbb12bb211bbbbb1bd122d131dd332e1e44ccccccccc6......................",
    "e32121e11dddd1e888877655678888bb13b2321b1b1b2122312d311d332e1244ccccccccc56.....................",
    "22122de1111e1111e887766556788888233232121b1b22d2311d321fd32e12e4ccccccccc4c6....................",
    "23232d2e21ee1dddd188766556788888213323333221b2d311f1231fd32e12e44cccccccc4c46...................",
    "32322d2e2122e1dffd1e7765556788882123132321f21211d1df2f1dfd212eee44ccccccccc446..................",
    "232321e2312e11ddffdd176555678888221312d31d1f2222d2df2f21fd21e11e444cccccccc4456.................",
    "533232323212e11ddffdd176556788872212d1d31ddd21d2d3df2df1dde1e11244444ccccc44456.................",
    "c553332333122e11ddffdd16555678877211d1d21dfdf1d2131dfdf2dfd11e125444444444444556................",
    "fc553333332d22ee11ddffd1665678778211d1d11df1f1dd231dfdf2dfd1ee265554444444444556................",
    "ffc4553333212222e111dffd1166777782211dd11df1f1df131dfddd2d11e22255554c44444455557...............",
    "fffcc4533321d2222ee11dfffd16777882221dd11df1f1dfd311dfdf2d21e2e26555c754445555557...............",
    "ffffcc453332112222e1e1dfffd1777888321d111df2d1ddf311dfdf2121121ee6554755555555557...............",
    "ffffccc45333221222e21e1dfffd177788321d111df2111df231df1df3111211e76656555555555667..............",
    "ffffcccc453332211e2212e1dfffd11778232d211dd2121df231df1df32e22111e7656655555556667..............",
    "fffccccc44533322323212ee1dfffdd1788321211d12121df331df21d31e2221d1e7756666666666677.............",
    "ffcccccc445333332321222ee1dffffd178321121d12221dd331dd31d3123ee1dd17776666665556777.............",
    "cccccccc44453333323d2222ee1dffffd183231311212311d331dd31131232ee1d11777766555555567.............",
    "ccccccc444456333232d2e222ee1ddfffd13231311312321d321d133131233e1e1dd1777665544444456............",
    "cccccc44444553333221e2e222eee1dfffd13323213123211321d13323d132e1111d11766554cccccc4466..........",
    "ccccc4444445563333221e2ee222ee1dfffd1333213223311321122331d13ede1d111e766554ccccccccc466........",
    "444444444445563333221ee11e222ee1dfffd133223223312311131331dd12ed11d1eee66554ccccccccccc46.......",
    "4444444444555673333221ee11e222ee1dfffd1332323231322123133e1d12eed1dd1e116554cccccccccccc46......",
    "4444444445556673333322deee1e222ee1dfffd13233323132123133e2e1d12edf1fde1d15544cccccccccccc46.....",
    "44444444555566673333322ed21e2222ee1dfffd133332323322332bb2e1d12eef1df1e1d65544cccccccccccc46....",
    "44444445555666673333232121e1e2e22ee1dfffd1333322232332bbbb2e1d12eddedd1ed1655cc4cccccccc4c446...",
    "5555555555666677333332323d1de21e22ee1dfffd13332133232bbaabbe1dd2eed1ed1ede665c5cccccccccf5c446..",
    "5555555666667777333333233d1d1e11e22ee1dfffd133223332bbbbaab2e1de2edd1e1e1d165644cccccccccf7cc6..",
    "6666566666677777733332333d1fd11d1e22ee1dfffd1333322bbb797abbe1d12eed12ee1de16654444cccccc466c56.",
    "655555566655677773333323e1dfd1f1d1e22ee1dfffd13332ba79967aabe1d1e2e1d12e11e165544444444445c46556",
    "5ccc44556544557773333333e1ddfdfd1d1e22ee1dfffd1b2bbbaaaaa6ab2edd12ee111ee1ee6655444444444c444656",
    "cccccc44544ccc5566333333ee1dfdffd1d1e22e11dffffbbbbbbbba967bbe1d122ee112e12e26555544444444555556",
    "fffccc4444ccffcc45563333321dffdffd1d1ee2e11dfffd1a776699677bb2ed1e2ee112ee2e26655555555555555566",
    "fffffc4444ccfffccc45633332edff1dffdfd1e22ee1dfffd1aa7777bbbbabed1e2e2e12ee2ee2666555555555555666",
    "cfffffc444cccffcccc4563332e1fde1dffddd1e222e11dfddbbbbbbbbaabbe11e3e2e12e232e2666666665566666666",
    "cfffffcc444ccffc4ccc4563332ed1e1ddfd1dd1e22ee11dfd1bbbaaaaa67b2e1e322212e23222666666666666666666",
    "cccccffcc44ccffcc4ccc4665667ee2e1df111dd1e222ee1dddea7669967bbbeee3322e32333aa777777666666666666",
    "44ccccfcc444ccfcc4ccc65cc4456722e1d1e11d1ee2222e11d1ebb7777baab2e233222333a776699996677666666666",
    "4444cccccc44ccfc44c565cc44567777777e3ee1d1e22222e111ebabbbbabab2223332333a7699997767666776666777",
    "544444cccc444ccc44564cc44566775cc45733ee1d1e2322ee2e1ebaaaaaabb2333333aa7766677666a777667aa77777",
    "5554444ccc4544cc4564cc44567774ccc4567322e11ee33e1211eebb776655556677aa7777777aaa7766aa767aaa8877",
    "55544444c4455444564ccc4567774ccc456777332ee1e2322eee17665555444444455554445577aaaaa76aba77baa888",
    "655554444445554564ccc4567774ccc45677777772e1ee333222765444ccccccccc444ccc4445577abba77abaa7bab88",
    "66555554444455464cc44567774ccc4567775cc4572e2e233376544cccfffffffcccccc4444445577abbaa7bbaabbab8",
    "7766655554445556ccc4567784ccc4567775ccc44572332376544cccffffffffffcccc45677455557aabbbaabbaababb",
    "7777666555444566444567784ccc4567775cccc4567773335544ccffffffffffccccc4cccc66555557aabbbabbaabbbb",
    "677777665554447555667785ccc4567775ccc4566756673654ccfffffffffffccc44444444446555557abbbaabbabbbb",
    "667777766555457555667785cc4567775ccc45677545676544ccccfffffffcccc444444455555556557bbbbbabbbbbbb",
    "56677777665556755567786444567785ccc456775cc457544ccccccccccccccc444444455555566554aabbbbabbbbbbb",
    "5666777776655777556787665567785ccc456775cc45676444cccccccccccc444444455556666654445aabbbbbbbbb76",
    "5566677777665765677786556777884cc456775ccc5677755444ccccccc4444444455566777765544456abbbbbbbb765",
    "555667777776675556778655567786644567754cc4567775555444444444444445555677777654444566aabbbbbb654c",
    "65556677777767556678876567788656666774ccc56778766555554444444555556667777765444456768abbbb7654cc",
    "6655667777777765677865566778655556776644467788766666555555555555666777766654445567768abbb7654c44",
    "6655667777777777778865567788655567775566677888877777666666555666677777665555556667788bbb76544445",
    "7666667777777777888866677788665677765555677888877777777766666677777766655556666677888bb765444555",
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
        Hook(0x5226, "1b5800ca1b5800cb1a983815181802840000ffff", to_block="portrait_graphic"),
        shared_hook(SELECT_PORTRAIT, "select_portrait"),
        shared_hook(ENEMY_PORTRAIT, "enemy_portrait"),
        shared_hook(PORTRAIT_PALETTE, "portrait_palette"),
    ],
    rom_data=_rom_data(),
)
