"""Takuma (Mr. Karate, START): Kohou com o corpo do Takuma — SPEC-086.

Só para o Takuma escolhido com START (cor 1 e flag `$3DA`,
global/start-select-flag). → ↓ ↘ + soco, como o Kohou do Ryo.

- Comando: o reconhecedor ($1DFC2) usa a linha de listas de passos do
  personagem em $25D04 + ($62-1)*$20 (word por comando $40-$4F, relativa a
  $25D04). Para o Mr. Karate a linha é COMMAND_ROW: a do Takuma com o comando
  $48 (livre) apontando para a lista $0250 (o → ↓ ↘ + soco do Kohou do Ryo).
- Conclusão ($1E0E0): a tabela $1E110 (byte por personagem e comando) não
  tem o $48 do Takuma; para o Mr. Karate o comando concluído vira $218 = $48.
- Golpe: no despacho de comandos ($1D41E, `charlib.KICK_SELECT`), o comando
  $48 do Mr. Karate vai para o handler de especial $1D4DC com o golpe $023
  (Kohou do Ryo; a força soma +0/+1/+2: $023/$024/$025, com o dano de cada um).
  Os patches do Ryo filtram pelo personagem e não agem no Takuma.
- Animação: as animações desses golpes ($17B, $17E, $145) trocam para $5F5
  (livre na faixa do Takuma) no tocador ($4A26), só no sprite do Mr. Karate.
  $5F5 é cópia byte a byte do Kohou original ($145, $535E2), mantendo listas
  de comandos (som, impulso $D2 com vy $000CC000, gravidade $FF70, vx
  $01800000, aterrissagem), com as peças do Ryo trocadas pelas do Takuma:
  preparação $9C9, soco para cima com ataque $9E1, no ar $9CF.
"""
from asm68k import Branch, Ins, JmpAbs, JmpNext, Label, LeaPc, Raw
from charlib import KICK_SELECT, START_FLAG as FLAG, shared_hook
from patchlib import Block, DataBlock, Data, Hook, Patch

TAKUMA = 0xA
COMMAND = 0x48               # comando livre no Takuma
KOHOU_STEPS = 0x0250         # lista de passos do Kohou do Ryo (relativa a $25D04)
KOHOU_MOVE = 0x023           # golpe base do Kohou (+0/+1/+2 pela força)
KOHOU_ANIMS = (0x145, 0x17B, 0x17E)
NEW_ANIM = 0x5F5
P1_RECORD, P2_RECORD = 0x109280, 0x109380
STEP_BASE = 0x25D04

# Linha de comandos do Takuma ($25E24) com $48 = Kohou.
COMMAND_ROW = [0x01A0, 0x02DC, 0x0238, 0x047C, 0x0552, 0x0966, 0x01E0, 0x02B6,
               KOHOU_STEPS, 0, 0, 0, 0, 0, 0, 0]

# $535E2-$5365F: quadros do Kohou ($145, 11 quadros) e as listas de comandos.
KOHOU_BYTES = bytes.fromhex(
    "8210114182101142851011430030005586000ae886000ae986000aec86000aea80000aeb"
    "06000052808006050210002a82101142051000270030002d86000ae886000ae986000aec"
    "86000aea80000aeb0600002680800605dadd1a1141e6c701401143deebdd01c7003ed20c"
    "000cc000ff70018000000ae8c70050060500")
PREP, UPPER, AIR = 0x9C9, 0x9E1, 0x9CF
# (deslocamento no bloco, peça do Ryo, peça do Takuma)
SWAPS = [
    (0x02, 0x1141, PREP), (0x06, 0x1142, PREP), (0x0A, 0x1143, UPPER),
    (0x12, 0x0AE8, UPPER), (0x16, 0x0AE9, AIR), (0x1A, 0x0AEC, AIR),
    (0x1E, 0x0AEA, AIR), (0x22, 0x0AEB, AIR), (0x2A, 0x0605, PREP),
    (0x76, 0x0AE8, UPPER),   # lista do impulso: 1ª pose no ar
    (0x7B, 0x0605, PREP),    # lista da aterrissagem
]


def _anim_bytes(org):
    b = bytearray(KOHOU_BYTES)
    for off, old, new in SWAPS:
        assert b[off:off + 2] == old.to_bytes(2, "big"), hex(off)
        b[off:off + 2] = new.to_bytes(2, "big")
    return bytes(b)


def _is_karate(record):
    """Z=1 se o registro (a0) é um Takuma marcado com cor 1. Usa d0."""
    return [
        Ins(f"0c68{TAKUMA:04x}0062", f"cmpi.w #${TAKUMA:x}, $62(a0)"),
        Branch("bne", f"no_{record}"),
        Ins("0c6800010276", "cmpi.w #$1, $276(a0)"),
        Branch("bne", f"no_{record}"),
        Ins(f"4a28{FLAG:04x}", f"tst.b ${FLAG:x}(a0)"),
        Branch("beq", f"no_{record}"),
    ]


# $1DFC2: move.w $62(a6),d4 / lsl.w #5,d4 / lea $25d04(pc),a1 / lea -$20(a1,d4.w),a0
command_row = [
    Ins("382e0062", "move.w $62(a6), d4"),
    Ins("eb4c", "lsl.w #$5, d4"),
    Ins(f"43f9{STEP_BASE:08x}", f"lea.l ${STEP_BASE:x}.l, a1"),
    Ins("41f140e0", "lea.l -$20(a1, d4.w), a0"),
    Ins(f"0c6e{TAKUMA:04x}0062", f"cmpi.w #${TAKUMA:x}, $62(a6)"),
    Branch("bne", "done"),
    Ins("0c6e00010276", "cmpi.w #$1, $276(a6)"),
    Branch("bne", "done"),
    Ins(f"4a2e{FLAG:04x}", f"tst.b ${FLAG:x}(a6)"),
    Branch("beq", "done"),
    LeaPc("row", 0),
    Label("done"),
    JmpAbs(0x1DFD0),
    Label("row"),
    Raw("".join(f"{w:04x}" for w in COMMAND_ROW)),
]

# $1E0E6: continuação da conclusão do comando (d5 = comando, d0 já tem
# ($62-1) calculado pelo haoh-easy-input.keep_haoh ou pelo original).
# O hook cobre 8 bytes (lsl.w#4,d0 / add.w d5,d0 / subi.w #$40,d0):
# os 6 primeiros pertencem ao haoh-easy-input que reescreveu $1E0E0.
# Para o Mr. Karate com $48, grava $218=$48 e pula para $1E102.
# Para todos os outros, repõe lsl+add+subi e continua em $1E0EE.
#
# NOTA: o "original" $1E0E6 está disponível porque haoh-easy-input
# usa apenas $1E0E0..$1E0E5 (6 bytes: move.w $62(a6),d0 / subq #1,d0).
complete = [
    Ins("e948", "lsl.w #$4, d0"),
    Ins("d045", "add.w d5, d0"),
    Ins(f"0c45{COMMAND:04x}", f"cmpi.w #${COMMAND:x}, d5"),
    Branch("bne", "table"),
    Ins(f"0c6e{TAKUMA:04x}0062", f"cmpi.w #${TAKUMA:x}, $62(a6)"),
    Branch("bne", "table"),
    Ins("0c6e00010276", "cmpi.w #$1, $276(a6)"),
    Branch("bne", "table"),
    Ins(f"4a2e{FLAG:04x}", f"tst.b ${FLAG:x}(a6)"),
    Branch("beq", "table"),
    Ins(f"303c{COMMAND:04x}", f"move.w #${COMMAND:x}, d0"),
    JmpAbs(0x1E102),                                   # move.w d0,$218(a6)
    Label("table"),
    Ins("04400040", "subi.w #$40, d0"),                # original coberto pelo jmp
    JmpAbs(0x1E0EE),                                   # continua: move.b $20(pc,d0.w),d0
]

# KICK_SELECT ($1D41E, antes do original): d4 = comando, a6 = registro do jogador.
dispatch = [
    Ins(f"0c6e{TAKUMA:04x}0062", f"cmpi.w #${TAKUMA:x}, $62(a6)"),
    Branch("bne", "pass"),
    Ins("0c6e00010276", "cmpi.w #$1, $276(a6)"),
    Branch("bne", "pass"),
    Ins(f"4a2e{FLAG:04x}", f"tst.b ${FLAG:x}(a6)"),
    Branch("beq", "pass"),
    Ins("3004", "move.w d4, d0"),
    Ins("0240007f", "andi.w #$7f, d0"),
    Ins(f"0c40{COMMAND:04x}", f"cmpi.w #${COMMAND:x}, d0"),
    Branch("bne", "pass"),
    Ins("3b400020", "move.w d0, $20(a5)"),
    LeaPc("entry", 0),
    JmpAbs(0x1D4DC),                                   # handler de especial
    Label("entry"),
    Raw(f"{KOHOU_MOVE:04x}0008"),
    Label("pass"),
    JmpNext(KICK_SELECT),
]

# $4A26: move.w $54(a6),d1 / add.w d1,d1  (tocador de animação; a6 = sprite)
def _sprite_check(record, label):
    return [
        Ins(f"41f9{record:08x}", f"lea.l ${record:x}.l, a0"),
        *_is_karate(label),
        Ins("7000", "moveq #$0, d0"),
        Ins("10280003", "move.b $3(a0), d0"),
        Ins("e148", "lsl.w #$8, d0"),
        Ins("d08d", "add.l a5, d0"),
        Ins("b08e", "cmp.l a6, d0"),
        Branch("beq", "remap"),
        Label(f"no_{label}"),
    ]


anim = [
    Ins("322e0054", "move.w $54(a6), d1"),
    *[x for a in KOHOU_ANIMS for x in (Ins(f"0c41{a:04x}", f"cmpi.w #${a:x}, d1"), Branch("beq", "check"))],
    Branch("bra", "out"),
    Label("check"),
    Ins("48e78080", "movem.l d0/a0, -(a7)"),
    *_sprite_check(P1_RECORD, "p1"),
    *_sprite_check(P2_RECORD, "p2"),
    Ins("4cdf0101", "movem.l (a7)+, d0/a0"),
    Branch("bra", "out"),
    Label("remap"),
    Ins("4cdf0101", "movem.l (a7)+, d0/a0"),
    Ins(f"323c{NEW_ANIM:04x}", f"move.w #${NEW_ANIM:x}, d1"),
    Label("out"),
    Ins("d241", "add.w d1, d1"),
    JmpAbs(0x4A2C),
]

PATCH = Patch(
    id="karate-kohou",
    title="Mr. Karate (START): Kohou com o corpo do Takuma",
    spec="src/backend/specs/SPEC-086-takuma-karate-kohou.md",
    blocks=[Block("command_row", command_row), Block("complete", complete), Block("dispatch", dispatch), Block("anim_remap", anim),
            DataBlock("kohou_anim", len(KOHOU_BYTES), _anim_bytes)],
    hooks=[
        Hook(0x1DFC2, "382e0062eb4c43fa7d3a41f140e0", to_block="command_row"),
        # $1E0E6: lsl.w #4,d0 / add.w d5,d0 / subi.w #$40,d0 (os 6 bytes anteriores
        # pertencem ao haoh-easy-input que reescreveu $1E0E0; este hook usa os 8
        # bytes seguintes para caber o jmp.l + 1 nop, cobrindo as instruções
        # completas lsl+add+subi sem partir instruções ao meio).
        Hook(0x1E0E6, "e948d04504400040", to_block="complete"),
        shared_hook(KICK_SELECT, "dispatch"),
        Hook(0x4A26, "322e0054d241", to_block="anim_remap"),
    ],
    data=[Data(0x50000 + NEW_ANIM * 4, "00000000",
               lambda addrs: ((11 << 24) | addrs["kohou_anim"]).to_bytes(4, "big").hex())],
)
