"""special-cancel-input-buffer — SPEC-008.

1. Special cancel global: qualquer golpe normal em pé que conectou (hit ou
   block, ver SPEC-008) pode ser cancelado em qualquer especial.
   O motor original já tem a janela ($1C064, estado de ataque): ela abre
   quando o golpe conecta ($21B zerado em $1D0C4) e executa o especial
   pendente em $218 via $1D808. O que impedia eram duas listas por
   personagem, aqui zeradas:
     $1C126 + char*2  (word) especiais PROIBIDOS de cancelar (bit = cmd - $40)
     $1C160 + char*4  (long) normais NÃO canceláveis (bit = cmd do normal - $20)
2. Input buffer: prazo entre passos de comando de 10 -> 12 frames.
   Tabela de comandos $25D04 (por personagem, $20 bytes: offsets dos
   comandos $40-$4F); passo = [máscara][valor][prazo][?][próximo].
   O prazo é recarregado a cada passo e decrementado por frame ($1E04E).

3. Cancel também no ar: $1C064 descartava golpes aéreos com dois testes
   ($3F bit 4 = pulo iniciado, $60 bit 4 = no ar); os dois desvios viram NOP.
   Especial só de chão no ar cai no soco aéreo do handler, que é recusado
   por $240 ("um ataque por pulo"), então o cancel não acontece.

4. Caixa de ataque "rearmada" no cancel: cada caixa de ataque é um objeto
   filho do sprite (filhos 5 e 6). Ao acertar, a colisão ($F6BC6) liga o
   bit 7 de $70 do objeto ("já acertou") e não o testa mais ($F6B78). O
   jogo só limpa esse bit no objeto do jogador ($1DF76/$1DEE8), nunca nos
   filhos. No cancel o especial reaproveita o filho 5 do normal ainda
   marcado, e o golpe atravessa o oponente. O hook em $1C0B4 executa o
   especial e, só se ele começou, limpa o bit 7 dos filhos 5 e 6. (Limpar
   antes fazia o normal acertar 2 vezes quando o especial era recusado, e o
   2º acerto durante a reação derruba o oponente.)

5. Buffer na aterrissagem para golpes aéreos: durante um golpe, o que é
   apertado fica em $274 ($1BFE4) e sai no frame da aterrissagem ($1C39E ->
   $1D808), mas só para os golpes marcados em $1C0BA + char*4 (bit = comando
   - $20). O original marcava só fracos em pé/agachado ($20,$22,$28,$38); os
   aéreos ($2A/$2B socos, $3A/$3B chutes) entram na máscara. O buffer guarda
   o mesmo tipo de botão do último ataque ($235: soco após soco, chute após
   chute), como no original.

6. Sem "sujeira" de buffer: o buffer de golpe ($274, acumulado em $1BFDE e
   disparado quando o golpe termina) fica só para os golpes aéreos (buffer
   de aterrissagem do item 5).
   - especiais: o original acumulava SEMPRE ($1C076: $230 >= $40 -> $1C0A2);
     agora sai sem acumular E descarta o comando pendente $218 a cada frame:
     o leitor de comandos re-detectava o especial com o movimento ainda no
     histórico e ele saía sozinho depois da recuperação
   - hitstop de especial: o congelamento do impacto também acumulava
     ($1CA66); em especiais que sobem (Kohou, Hien) o buffer disparava na
     aterrissagem. Agora só acumula fora de especial
   - normais de chão: saem da máscara $1C0BA (o original tinha
     $20/$22/$28/$38, socos e chutes fracos de pé e agachado)
   O special cancel usa o comando pendente ($218), não esse buffer.

Leitura durante o hitstop: já é nativa (o estado de congelamento
$41 = 2 chama o leitor de comandos em $1CA08); nada a alterar.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Data, Hook, Patch

CANCEL_FORBIDDEN_SPECIALS = 0x1C126
CANCEL_FORBIDDEN_NORMALS = 0x1C160
OLD_STEP_WINDOW = 10
NEW_STEP_WINDOW = 12

# (personagem $62, máscara original) — só as não zeradas
FORBIDDEN_SPECIALS = [
    ( 1, 0x000F),  # Ryo
    ( 2, 0x4240),  # Robert
    ( 3, 0x000F),  # Eiji
    ( 4, 0x4240),  # Jack
    ( 5, 0x0001),  # Lee
    ( 6, 0x86A0),  # King
    ( 7, 0x0010),  # Micky
    ( 8, 0xC8E0),  # John
    ( 9, 0x0001),  # Mr.Big
    (10, 0x86A0),  # Takuma
    (12, 0x03E8),  # Temjin
]
FORBIDDEN_NORMALS = [
    ( 4, 0x0C000C00),  # Jack
    (12, 0x00000400),  # Temjin
]

# endereço do byte de prazo de cada passo de comando (todos valem 10)
STEP_WINDOW_BYTES = [
    0x25EA6, 0x25EAE, 0x25EB6, 0x25EBE, 0x25EC6, 0x25ECE, 0x25ED6, 0x25EDE,
    0x25EE6, 0x25EEE, 0x25EF6, 0x25EFE, 0x25F06, 0x25F0E, 0x25F16, 0x25F1E,
    0x25F2E, 0x25F36, 0x25F46, 0x25F4E, 0x25F56, 0x25F5E, 0x25F66, 0x25F6E,
    0x25F96, 0x25F9E, 0x25FBC, 0x25FC4, 0x25FEA, 0x25FF2, 0x25FFA, 0x26002,
    0x2600A, 0x26012, 0x26092, 0x2609A, 0x260A2, 0x260AA, 0x260BA, 0x260C2,
    0x260CA, 0x260DA, 0x260E2, 0x260EA, 0x260FA, 0x26102, 0x2610A, 0x2611A,
    0x26218, 0x26220, 0x26228, 0x26230, 0x26238, 0x26240, 0x26248, 0x26250,
    0x26258, 0x26260, 0x26268, 0x26270, 0x26278, 0x26280, 0x262EE, 0x262F6,
    0x262FE, 0x26306, 0x2630E, 0x26316, 0x2631E, 0x26326, 0x2632E, 0x26336,
    0x2633E, 0x26346, 0x2634E, 0x26356, 0x26366, 0x2636E, 0x26376, 0x2637E,
    0x26386, 0x2638E, 0x26396, 0x2639E, 0x263A6, 0x263AE, 0x263B6, 0x263BE,
    0x263F6, 0x263FE, 0x26406, 0x2640E, 0x26416, 0x2641E, 0x26426, 0x2642E,
    0x2643E, 0x26446, 0x2644E, 0x26456, 0x2645E, 0x26466, 0x26496, 0x2649E,
    0x264A6, 0x264AE, 0x264B6, 0x264BE, 0x264C6, 0x264CE, 0x2652C, 0x26534,
    0x2653C, 0x2654C, 0x26554, 0x2655C, 0x26564, 0x2656C, 0x26604, 0x2660C,
    0x26614, 0x2661C, 0x26624, 0x2663C, 0x26644, 0x2664C, 0x26654, 0x2665C,
    0x26664, 0x2666C, 0x26674, 0x2668C, 0x26694, 0x2669C, 0x266A4, 0x266AC,
    0x266B4, 0x266BC, 0x266C4, 0x266CC, 0x266D4, 0x266DC, 0x266E4, 0x266EC,
    0x266F4, 0x26704, 0x2670C, 0x26714, 0x2671C, 0x26724, 0x2672C, 0x26734,
    0x2673C, 0x26744, 0x2674C, 0x26754, 0x2675C, 0x26764, 0x2676C, 0x26774,
    0x2677C, 0x26784, 0x2678C,
]

LANDING_BUFFER_MASK = 0x1C0BA   # long por personagem: normais com buffer ($1C08A)
AIR_NORMALS = 0x0C000C00        # bits $2A,$2B (socos aéreos) e $3A,$3B (chutes aéreos): única máscara
ORIGINAL_BUFFER_MASKS = {c: 0x01000105 for c in range(1, 13)} | {13: 0x00000105}
# Exceção (normais que mantêm o buffer do original): Ryo ($62 = 1), chute
# fraco agachado ($38, bit 24), para baixo B -> baixo D (normal-chains,
# SPEC-018). Os outros personagens ficam só com os aéreos.
CROUCH_LK = 1 << (0x38 - 0x20)
KEEP_BUFFER = {1: CROUCH_LK}

CANCEL_EXEC = 0x1D808          # executa o especial pendente ($218)
CANCEL_DONE = 0x1C0BA          # cancel aconteceu (addq #4,a7 / rts)
CANCEL_NONE = 0x1C0B2          # nada executado (rts)


def clear_child_hit(offset, skip):
    """Limpa o bit 7 de $70 do filho cujo id está em sprite+offset (a0 = sprite)."""
    return [
        Ins("7000", "moveq #$0, d0"),
        Ins(f"1028{offset:04x}", f"move.b ${offset:x}(a0), d0"),
        Branch("beq", skip),
        Ins("e148", "lsl.w #$8, d0"),
        Ins("43f50000", "lea.l (a5, d0.w), a1"),
        Ins("08a900070070", "bclr.b #$7, $70(a1)"),
    ]


# Substitui: jsr $1d808(pc) / beq.b $1c0b2  em $1C0B4
# Rearma só se o especial realmente começou ($1D808 devolve d0 != 0). Se ele
# for recusado, o normal continua com a caixa marcada (sem 2º acerto).
rearm_and_cancel = [
    Ins("4eb90001d808", "jsr $1d808.l"),
    Branch("beq", "none"),
    Ins("48e780c0", "movem.l d0/a0-a1, -(a7)"),
    Ins("010e0003", "movep.w $3(a6), d0"),       # objeto de sprite do jogador
    Ins("4200", "clr.b d0"),
    Ins("41f50000", "lea.l (a5, d0.w), a0"),
    *clear_child_hit(2 + 5, "child6"),           # filho 5
    Label("child6"),
    *clear_child_hit(2 + 6, "done"),             # filho 6
    Label("done"),
    Ins("4cdf0301", "movem.l (a7)+, d0/a0-a1"),
    JmpAbs(CANCEL_DONE),
    Label("none"),
    JmpAbs(CANCEL_NONE),
]

# Durante um especial ($230 >= $40) o original acumulava o buffer de botão
# ($1C0A2). Agora: não acumula e descarta o comando de especial pendente
# ($218), que o leitor de comandos re-detectava com o movimento ainda no
# histórico e que saía sozinho depois da recuperação ("especial fantasma").
during_special = [
    Ins("0c6e00400230", "cmpi.w #$40, $230(a6)"),
    Branch("bcc", "special"),
    JmpAbs(0x1C07E),                                  # normal: segue o original
    Label("special"),
    Ins("426e0218", "clr.w $218(a6)"),
    Ins("4e75", "rts"),                               # sai de $1C064 sem acumular
]

# Congelamento do impacto (hitstop, $1CA00) em estado de ataque: o original
# acumulava o buffer de botão SEMPRE ($1CA66: jsr $1BFDE). Em especiais que
# sobem e acertam várias vezes (Kohou, Hien) o buffer disparava na
# aterrissagem ($1C39E). Agora só acumula se o golpe atual não é especial.
hitstop_buffer = [
    Ins("0c2e00030040", "cmpi.b #$3, $40(a6)"),      # (original) só no estado de ataque
    Branch("bne", "skip"),
    Ins("0c6e00400230", "cmpi.w #$40, $230(a6)"),
    Branch("bcc", "skip"),
    Ins("4eb90001bfde", "jsr $1bfde.l"),
    Label("skip"),
    Ins("4e75", "rts"),
]

PATCH = Patch(
    id="special-cancel-input-buffer",
    title="Special cancel global (chão e ar) e buffer de comandos de 12 frames",
    spec="src/backend/specs/SPEC-008-special-cancel-input-buffer.md",
    blocks=[
        Block("rearm_and_cancel", rearm_and_cancel),
        Block("during_special", during_special),
        Block("hitstop_buffer", hitstop_buffer),
    ],
    hooks=[
        # $1C0B4: jsr $1d808(pc) / beq.b $1c0b2  -> jmp rearm_and_cancel
        Hook(addr=0x1C0B4, expect="4eba175267f8", to_block="rearm_and_cancel"),
        # $1C06C: bne.b $1c08a  ($3F bit 4: pulo)  -> nop
        Hook(addr=0x1C06C, expect="661c", program=[Ins("4e71", "nop")]),
        # $1C074: bne.b $1c08a  ($60 bit 4: no ar) -> nop
        Hook(addr=0x1C074, expect="6614", program=[Ins("4e71", "nop")]),
        # $1C076: cmpi.w #$40,$230(a6) / bcc.b $1c0a2  ->  jmp during_special
        Hook(addr=0x1C076, expect="0c6e004002306424", to_block="during_special"),
        # $1CA5E..$1CA69: cmpi.b #3,$40(a6) / bne $1ca6a / jsr $1bfde(pc)
        # O rts em $1CA6A fica intacto: $1CA34 e $1CA64 desviam para ele.
        Hook(addr=0x1CA5E, expect="0c2e000300406604" "4ebaf576", to_block="hitstop_buffer"),
    ],
    data=(
        [Data(CANCEL_FORBIDDEN_SPECIALS + c * 2, f"{m:04x}", "0000") for c, m in FORBIDDEN_SPECIALS]
        + [Data(CANCEL_FORBIDDEN_NORMALS + c * 4, f"{m:08x}", "00000000") for c, m in FORBIDDEN_NORMALS]
        + [Data(a, f"{OLD_STEP_WINDOW:02x}", f"{NEW_STEP_WINDOW:02x}") for a in STEP_WINDOW_BYTES]
        + [Data(LANDING_BUFFER_MASK + c * 4, f"{m:08x}", f"{AIR_NORMALS | KEEP_BUFFER.get(c, 0):08x}")
           for c, m in ORIGINAL_BUFFER_MASKS.items()]
    ),
)
