"""kohou-impact-sound (Ryo) — SPEC-034.

Kohou forte com os 2 hits: os DOIS tocam o som de acerto "pesado" do Hien
Shippuukyaku ($0140, opcode e7 0140 da lista $533BC). Como o 2º hit ainda
não aconteceu no 1º, a regra é: 1º hit sem defesa = o 2º vem (o Kohou forte
emenda os 2) se estiver colado (origens a até CLOSE px). Longe, defendido ou
2º hit sozinho (antiaéreo): som original ($21E60).

Hook compartilhado no contato ($224BE, charlib.HIT_SOUND; a0 = atacante,
a6 = defensor). Atacante Ryo:
  - defendido ($7C & $F = 3, como $21872): som original; desmarca
  - Kohou ($230 = $47) com efeito $0B ($20A): 1º hit; se |X atacante - X
    defensor| <= CLOSE -> $0140 e marca $3A8; senão som original
  - Kohou com outro efeito ($01, 2º hit) e a marca: $0140; desmarca
  - outro golpe: desmarca
$3A8: livre no registro do jogador (ram_scan: nunca muda; o hit-counter
usa $3A0-$3A7, SPEC-013).
"""
from asm68k import Branch, Ins, JmpNext, Label
from charlib import HIT_SOUND, RYO, shared_hook
from patchlib import Block, Patch

KOHOU_CMD = 0x47
IMPACT_SOUND = 0x0140      # som de acerto do Hien Shippuukyaku
MARK = 0x3A8
# efeito de acerto atual ($20A): $0B no 1º hit (byte 6 do $023); o lançamento
# (dd 01 na lista $53645) troca para $01 no 2º. A altura ($18) não serve: de
# perto o 2º hit acerta no frame do lançamento, ainda com $18 = 0.
FIRST_HIT_EFFECT = 0x0B
# distância máxima entre as origens ($10) para o 2º hit pegar: caixa do 2º hit
# 0..42 px à frente do Ryo + frente do corpo do oponente ~34 px (anim $145 /
# peça $062A). O 1º hit alcança até ~114 px. Ajustável.
CLOSE = 80

impact = [
    Ins(f"0c68{RYO:04x}0062", f"cmpi.w #${RYO:x}, $62(a0)"),
    Branch("bne", "out"),
    # Animacao exclusiva do forte: medio $145 e fraco $17E usam som nativo.
    Ins("0c68017b006e", "cmpi.w #$17b, $6e(a0)"),
    Branch("bne", "unmark"),
    Ins("102e007c", "move.b $7c(a6), d0"),             # defesa ($21872: $7C & $F = 3)
    Ins("0200000f", "andi.b #$f, d0"),
    Ins("0c000003", "cmpi.b #$3, d0"),
    Branch("beq", "unmark"),
    Ins(f"0c28{FIRST_HIT_EFFECT:04x}020a", f"cmpi.b #${FIRST_HIT_EFFECT:x}, $20a(a0)"),
    Branch("bne", "second"),                           # efeito $01: 2º hit
    Ins("30280010", "move.w $10(a0), d0"),             # 1º hit: colado o bastante?
    Ins("906e0010", "sub.w $10(a6), d0"),
    Branch("bpl", "dist"),
    Ins("4440", "neg.w d0"),
    Label("dist"),
    Ins(f"0c40{CLOSE:04x}", f"cmpi.w #${CLOSE:x}, d0"),
    Branch("bhi", "unmark"),                           # longe: o 2º não pega
    Ins(f"117c0001{MARK:04x}", f"move.b #$1, ${MARK:x}(a0)"),   # 1º hit limpo e perto: o 2º vem
    Branch("bra", "sound"),
    Label("second"),
    Ins(f"4a28{MARK:04x}", f"tst.b ${MARK:x}(a0)"),
    Branch("beq", "out"),                              # 2º hit sem o 1º: original
    Ins(f"4228{MARK:04x}", f"clr.b ${MARK:x}(a0)"),
    Label("sound"),
    Ins(f"3d7c{IMPACT_SOUND:04x}0a5e", f"move.w #${IMPACT_SOUND:x}, $a5e(a6)"),
    Branch("bra", "out"),
    Label("unmark"),
    Ins(f"4228{MARK:04x}", f"clr.b ${MARK:x}(a0)"),
    Label("out"),
    JmpNext(HIT_SOUND),
]

PATCH = Patch(
    id="kohou-impact-sound",
    title="Ryo: som pesado apenas no Kohou forte; medio e fraco com som original",
    spec="src/backend/specs/SPEC-034-ryo-kohou-impact-sound.md",
    blocks=[Block("kohou_impact", impact)],
    hooks=[shared_hook(HIT_SOUND, "kohou_impact")],
)
