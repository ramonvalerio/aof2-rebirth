"""overhead-kick (Ryo) — SPEC-016.

Chutes do Ryo em pé:
  frente + B  -> chute forte perto (golpe $00A), de qualquer distância,
                 overhead (só defende em pé) e com 1 hit só;
  trás + D    -> chute forte longe original (golpe $00B);
  D (neutro)  -> chute novo: o chute fraco com mais frames ativos, um pouco
                 mais lento e com mais dano;
  B           -> chute fraco, sem mudança.

Seleção do chute ($1DC9E -> $1DCD4 -> $1DD28): d4 = $20 em pé, +2 se perto
($41A(a5) < $20), +1 se forte, +$10 por ser chute -> $30 fraco longe,
$31 forte longe, $32 fraco perto, $33 forte perto. O hook fica depois desse
cálculo, antes de "jmp $1D41E" (que usa d4 na tabela de comandos do Ryo,
$1EA88, -> lista $1E8C8 -> golpe).

Frente/trás: $270 bits 2 (esquerda) e 3 (direita). O lado vem do $5E do
SPRITE (a5 + byte $3 do jogador << 8), como no dash ($1BBF0): bit 0 = 1
-> frente é a direita. (v1/v2 liam o $5E do jogador, que não acompanha a
troca de lado.)

D neutro usa o d4 livre $3F: a tabela de comandos ganha $3F -> entrada 11
(mesmo handler do chute forte longe). O golpe é lido só em $1D75C
($23BA4 + id*16); ali um hook troca o registro quando $20(a5) = $3F (o d4
gravado em $1D422) por um registro próprio, com a animação nova $17A.

Overhead: bytes 8-9 do golpe dizem como ele é defendido: em pé/meio $4F30,
baixo $4710 (só agachado), pulo $4B20 (só em pé). O $00A vira $4B20.
O 2º hit (pé descendo, q4 da $131, flags $08) sai com a flag zerada.
"""
from asm68k import Branch, Ins, JmpAbs, Label, LeaPc, Raw
from patchlib import Block, Data, DataBlock, Hook, Patch

RYO = 1
MOVE_TABLE = 0x023BA4
RYO_COMMANDS = 0x01EA88
ANIM_TABLE = 0x050000
CLOSE_HK = 0x00A            # chute forte perto
NEUTRAL_D = 0x3F            # d4 livre do Ryo
NEW_ANIM = 0x17A

kick_select = [
    Ins("4eb90001dd28", "jsr $1dd28.l"),           # +1 se forte (original)
    Ins("06440010", "addi.w #$10, d4"),             # chute (original)
    Ins(f"0c6e{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a6)"),
    Branch("bne", "done"),
    Ins("0c440030", "cmpi.w #$30, d4"),
    Branch("bcs", "done"),
    Ins("0c440033", "cmpi.w #$33, d4"),
    Branch("bhi", "done"),
    Ins("082e00010270", "btst.b #$1, $270(a6)"),   # baixo segurado: original
    Branch("bne", "done"),
    Ins("7000", "moveq #$0, d0"),
    Ins("102e0003", "move.b $3(a6), d0"),           # sprite do jogador
    Ins("e148", "lsl.w #$8, d0"),
    Ins("41f50000", "lea.l (a5, d0.w), a0"),
    Ins("7003", "moveq #$3, d0"),                   # frente = direita
    Ins("08280000005e", "btst.b #$0, $5e(a0)"),
    Branch("bne", "dir"),
    Ins("7002", "moveq #$2, d0"),                   # frente = esquerda
    Label("dir"),
    Ins("08040000", "btst.b #$0, d4"),
    Branch("bne", "strong"),
    # fraco: frente + B -> chute forte perto
    Ins("012e0270", "btst.l d0, $270(a6)"),        # (capstone escreve .l; é btst de byte)
    Branch("beq", "done"),
    Ins("7833", "moveq #$33, d4"),
    Branch("bra", "done"),
    Label("strong"),
    Ins("0a000001", "eori.b #$1, d0"),              # trás = o outro bit
    Ins("012e0270", "btst.l d0, $270(a6)"),
    Branch("bne", "back"),
    Ins(f"78{NEUTRAL_D:02x}", f"moveq #${NEUTRAL_D:x}, d4"),   # D neutro: chute novo
    Branch("bra", "done"),
    Label("back"),
    Ins("7831", "moveq #$31, d4"),                  # trás + D: chute forte longe
    Label("done"),
    JmpAbs(0x1D41E),
]

# Registro do chute novo: o chute fraco ($009: 0c 0c 00 00 00 0c 00 00 4f30
# 0130 0000 0100) com dano $12 (fraco $0C, forte longe $1C) e animação $17A.
NEUTRAL_D_RECORD = "1212" "0000" "000c" "0000" "4f30" f"{NEW_ANIM:04x}" "0000" "0100"

record_select = [
    Ins(f"0c6d{NEUTRAL_D:04x}0020", f"cmpi.w #${NEUTRAL_D:x}, $20(a5)"),
    Branch("bne", "original"),
    Ins(f"0c6e{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a6)"),
    Branch("bne", "original"),
    LeaPc("record", 0),
    JmpAbs(0x1D770),
    Label("original"),
    Ins("41f900023ba4", "lea.l $23ba4.l, a0"),
    Ins("322d0010", "move.w $10(a5), d1"),
    Ins("e949", "lsl.w #$4, d1"),
    Ins("41f01000", "lea.l (a0, d1.w), a0"),
    JmpAbs(0x1D770),
    Label("record"),
    Raw(NEUTRAL_D_RECORD),
]

# Animação $17A: cópia da $130 (chute fraco longe) mais longa. O q0 é um
# quadro de comando (offset relativo de 16 bits); a lista dele ($52FDC: som,
# som, peça $062C) vai copiada logo depois dos quadros.
FRAMES = [   # (duração, flags, peça) ; peça None = quadro de comando
    (2, 0x10, None),
    (2, 0x18, 0x062D),
    (11, 0x18, 0x062E),   # ativo: era 8
    (6, 0x00, 0x062D),    # era 4
    (5, 0x00, 0x062C),    # era 4
    (0, 0x80, 0x062C),
]
CMD_STREAM = bytes.fromhex("c70046c70172062c")


def anim_block(org):
    out = bytearray()
    cmd = org + len(FRAMES) * 4
    for k, (dur, flags, piece) in enumerate(FRAMES):
        if piece is None:
            out += bytes([dur, flags]) + (cmd - (org + k * 4 + 2)).to_bytes(2, "big")
        else:
            out += bytes([dur | 0x80, flags]) + piece.to_bytes(2, "big")
    return bytes(out + CMD_STREAM)


PATCH = Patch(
    id="overhead-kick",
    title="Ryo: overhead em frente + B, chute forte em trás + D, D neutro novo",
    spec="src/backend/specs/SPEC-016-ryo-overhead-kick.md",
    blocks=[
        Block("kick_select", kick_select),
        Block("record_select", record_select),
        DataBlock("neutral_d_anim", len(FRAMES) * 4 + len(CMD_STREAM), anim_block),
    ],
    hooks=[
        # $1DCAC: jsr $1dd28(pc) / addi.w #$10,d4 / jmp $1d41e(pc)
        Hook(addr=0x1DCAC, expect="4eba007a064400104efaf768", to_block="kick_select"),
        # $1D762: lea $23ba4(pc),a0 / move.w $10(a5),d1 / lsl.w #4,d1 / lea (a0,d1.w),a0
        Hook(addr=0x1D762, expect="41fa6440322d0010e94941f01000", to_block="record_select"),
    ],
    data=[
        Data(MOVE_TABLE + CLOSE_HK * 16 + 8, "4f30", "4b20"),   # overhead
        Data(0x052FE8 + 4 * 4 + 1, "08", "00"),                 # $131 q4: sem 2º hit
        Data(RYO_COMMANDS + NEUTRAL_D, "ff", "0b"),             # d4 $3F -> entrada 11
        Data(ANIM_TABLE + NEW_ANIM * 4, "00000000",
             lambda addrs: (len(FRAMES) << 24 | addrs["neutral_d_anim"]).to_bytes(4, "big").hex()),
    ],
)
