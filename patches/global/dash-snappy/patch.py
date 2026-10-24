"""dash-snappy — SPEC-011.

Dash para frente / para trás (dois toques) mais ágil, para todo o elenco:
os quadros PARADOS do dash passam a durar 1 frame.

O dash dispara os comandos 4 (frente) e 5 (trás) em $1BC98/$1BCA2; os
handlers $1E290/$1E2E0 usam o id da lista como animação e põem o jogador no
estado 16/17 ($1BCAC/$1BCE4). Nesse estado:
  - ataques e especiais já podem sair a qualquer momento (jsr $1D808);
  - soltar/trocar a direção ou o fim da animação encerra o dash (comando 1);
  - a velocidade ($1BD2C, tabela $1BD5C por personagem, ex.: 8,5 px/f) é
    ZERO nos quadros com flag $40.
As animações têm quadros $40 de 4 frames no início e no fim (ex.: Ryo
4+24+4), que deixavam o dash travado. Aqui todo quadro $40 dura 1 frame;
a parte em movimento (distância/velocidade) não muda.

Detector de dois toques ($1CCDA) reescrito. O original (máquina de estados
em $212) só armava com TODO o input bruto $68 zerado (nenhuma direção e
nenhum botão) e exigia o 1º toque exato em <- ou ->. Vindo da direção
oposta (ou com botão segurado) o 1º toque era ignorado e o dash não saía.
O novo usa as bordas de aperto ($69), que já implicam ter soltado antes:
  - toque <- ou -> (sem cima/baixo) = 1º toque, pendente por 16 frames
  - 2º toque na mesma direção dentro do prazo = dash (d0 = 1, como antes)
  - diagonal, outra direção ou fim do prazo = recomeça
$212 = pendente, $213 = direção (lida pelo estado de dash), $210 = prazo.
"""
from asm68k import Branch, Ins, Label
from patchlib import Block, Data, Hook, Patch

TAP_WINDOW = 16   # frames entre o 1º e o 2º toque (como o original)

# Substitui a máquina de estados inteira em $1CCDA (moveq #0,d0 / move.b $212(a6),d0).
# Devolve d0 = 1 (Z=0) quando o dash deve sair, d0 = 0 (Z=1) caso contrário.
double_tap = [
    Ins("2f01", "move.l d1, -(a7)"),
    Ins("7000", "moveq #$0, d0"),
    Ins("122e0069", "move.b $69(a6), d1"),        # bordas de aperto
    Ins("0201000c", "andi.b #$c, d1"),            # só <- / ->
    Branch("beq", "tick"),
    Ins("0c01000c", "cmpi.b #$c, d1"),            # os dois de uma vez
    Branch("beq", "reset"),
    Ins("082e00000068", "btst.b #$0, $68(a6)"),   # cima segurado (diagonal)
    Branch("bne", "reset"),
    Ins("082e00010068", "btst.b #$1, $68(a6)"),   # baixo segurado (meia-lua)
    Branch("bne", "reset"),
    Ins("4a2e0212", "tst.b $212(a6)"),
    Branch("beq", "first"),
    Ins("b22e0213", "cmp.b $213(a6), d1"),
    Branch("bne", "first"),
    # 2º toque na mesma direção: dash
    Ins("422e0212", "clr.b $212(a6)"),
    Ins("7001", "moveq #$1, d0"),
    Branch("bra", "exit"),
    Label("first"),
    Ins("1d410213", "move.b d1, $213(a6)"),
    Ins("1d7c00010212", "move.b #$1, $212(a6)"),
    Ins(f"3d7c{TAP_WINDOW:04x}0210", f"move.w #${TAP_WINDOW:x}, $210(a6)"),
    Branch("bra", "exit"),
    Label("tick"),
    Ins("4a2e0212", "tst.b $212(a6)"),
    Branch("beq", "exit"),
    Ins("536e0210", "subq.w #$1, $210(a6)"),
    Branch("bpl", "exit"),
    Label("reset"),
    Ins("422e0212", "clr.b $212(a6)"),
    Label("exit"),
    Ins("221f", "move.l (a7)+, d1"),
    Ins("4a80", "tst.l d0"),
    Ins("4e75", "rts"),
]

# (endereço do byte de duração do quadro, original, novo)
#   duração bit 7 = quadro simples (mantido); bits 0-6 = frames
STOP_FRAMES = [
    (0x052C02, 0x84, 0x81),  # Ryo frente anim 104 q0
    (0x052C12, 0x84, 0x81),  # Ryo frente anim 104 q4
    (0x052C1A, 0x84, 0x81),  # Ryo tras anim 105 q0
    (0x052C2A, 0x84, 0x81),  # Ryo tras anim 105 q4
    (0x053D2E, 0x84, 0x81),  # Robert frente anim 184 q0
    (0x053D36, 0x84, 0x81),  # Robert frente anim 184 q2
    (0x053D3E, 0x84, 0x81),  # Robert tras anim 185 q0
    (0x053D46, 0x84, 0x81),  # Robert tras anim 185 q2
    (0x054E7C, 0x84, 0x81),  # Eiji frente anim 204 q0
    (0x054E88, 0x84, 0x81),  # Eiji frente anim 204 q3
    (0x054E90, 0x84, 0x81),  # Eiji tras anim 205 q0
    (0x054E9C, 0x84, 0x81),  # Eiji tras anim 205 q3
    (0x055DEE, 0x83, 0x81),  # Jack tras anim 285 q0
    (0x055DFA, 0x87, 0x81),  # Jack tras anim 285 q3
    (0x056D36, 0x84, 0x81),  # Lee frente anim 304 q0
    (0x056D42, 0x84, 0x81),  # Lee frente anim 304 q3
    (0x056D46, 0x84, 0x81),  # Lee frente anim 304 q4
    (0x056D4E, 0x84, 0x81),  # Lee tras anim 305 q0
    (0x056D5A, 0x84, 0x81),  # Lee tras anim 305 q3
    (0x056D5E, 0x84, 0x81),  # Lee tras anim 305 q4
    (0x057CB6, 0x84, 0x81),  # King frente anim 384 q0
    (0x057CC2, 0x84, 0x81),  # King frente anim 384 q3
    (0x057CCA, 0x84, 0x81),  # King tras anim 385 q0
    (0x057CD2, 0x84, 0x81),  # King tras anim 385 q2
    (0x058B68, 0x84, 0x81),  # Micky frente anim 404 q0
    (0x058B74, 0x84, 0x81),  # Micky frente anim 404 q3
    (0x058B7C, 0x84, 0x81),  # Micky tras anim 405 q0
    (0x058B84, 0x84, 0x81),  # Micky tras anim 405 q2
    (0x059C0E, 0x82, 0x81),  # John frente anim 484 q0
    (0x059C12, 0x82, 0x81),  # John frente anim 484 q1
    (0x059C1E, 0x84, 0x81),  # John frente anim 484 q4
    (0x059C26, 0x82, 0x81),  # John tras anim 485 q0
    (0x059C2A, 0x82, 0x81),  # John tras anim 485 q1
    (0x059C36, 0x84, 0x81),  # John tras anim 485 q4
    (0x05ACE6, 0x04, 0x01),  # MrBig frente anim 504 q0
    (0x05ACF2, 0x04, 0x01),  # MrBig frente anim 504 q3
    (0x05ACF6, 0x84, 0x81),  # MrBig frente anim 504 q4
    (0x05ACFA, 0x84, 0x81),  # MrBig frente anim 504 q5
    (0x05BA96, 0x84, 0x81),  # Takuma frente anim 584 q0
    (0x05BAA6, 0x84, 0x81),  # Takuma frente anim 584 q4
    (0x05BAAE, 0x84, 0x81),  # Takuma tras anim 585 q0
    (0x05BABE, 0x84, 0x81),  # Takuma tras anim 585 q4
    (0x05CA76, 0x84, 0x81),  # Yuri frente anim 604 q0
    (0x05CA82, 0x84, 0x81),  # Yuri frente anim 604 q3
    (0x05CA8A, 0x84, 0x81),  # Yuri tras anim 605 q0
    (0x05CA9A, 0x84, 0x81),  # Yuri tras anim 605 q4
    (0x05DCD6, 0x84, 0x81),  # Temjin frente anim 684 q0
    (0x05DCE6, 0x84, 0x81),  # Temjin frente anim 684 q4
    (0x05DCEE, 0x82, 0x81),  # Temjin tras anim 685 q0
    (0x05DCF2, 0x82, 0x81),  # Temjin tras anim 685 q1
    (0x05DCFE, 0x84, 0x81),  # Temjin tras anim 685 q4
    (0x05EC82, 0x84, 0x81),  # Geese frente anim 704 q0
    (0x05EC92, 0x84, 0x81),  # Geese frente anim 704 q4
    (0x05EC96, 0x84, 0x81),  # Geese frente anim 704 q5
    (0x05EC9A, 0x84, 0x81),  # Geese frente anim 704 q6
]

PATCH = Patch(
    id="dash-snappy",
    title="Dash ágil: sem quadros parados e dois toques sem precisar passar pelo neutro",
    spec="src/backend/specs/SPEC-011-dash-snappy.md",
    blocks=[Block("double_tap", double_tap)],
    hooks=[Hook(addr=0x1CCDA, expect="7000102e0212", to_block="double_tap")],
    data=[Data(addr, f"{old:02x}", f"{new:02x}") for addr, old, new in STOP_FRAMES],
)
