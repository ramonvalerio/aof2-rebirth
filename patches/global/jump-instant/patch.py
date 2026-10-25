"""jump-instant — SPEC-023.

Pulo (neutro, frente e trás) sai na hora, para todo o elenco, e o pulo na
diagonal não anda antes de sair do chão.

O pulo dispara em $1DA66 (borda de cima, $271 bit 0): d4 = $B neutro,
9 frente, $D trás -> handler $1E3B6 (estado 4, $60 bit 4 = no ar), que usa
o id da lista como animação. O q0 das animações de pulo é um quadro de
comando com flag $40 (parado) de 2-3 frames: a lista dele toca o som e dá a
velocidade do pulo ($D2), mas o personagem só decola depois do quadro.
Nesses frames a velocidade de andar ($20, gravada em $1BB9A quando anda)
continua valendo: vindo de "andar para frente", ele anda antes de pular.

Patch:
  - todo quadro $40 das animações de pulo passa a durar 1 frame
    (Geese já tinha 1 no q0; os q1/q2 dele também são $40);
  - hook em $1E3B6: zera a velocidade de andar ($20) ao começar o pulo.
"""
from asm68k import Ins, JmpAbs
from patchlib import Block, Data, Hook, Patch

# (endereço do quadro, duração original) dos quadros $40 dos pulos.
# Gerado de $1E888/$1E848 (comandos 9, $B, $D; handler $1E3B6).
STOPPED_FRAMES = [
    (0x052C32, 0x03),  # Ryo frente anim 109 q0
    (0x052C5A, 0x03),  # Ryo neutro anim 10a q0
    (0x052C7E, 0x03),  # Ryo tras anim 10b q0
    (0x053D4E, 0x03),  # Robert frente anim 189 q0
    (0x053D76, 0x03),  # Robert neutro anim 18a q0
    (0x053D92, 0x03),  # Robert tras anim 18b q0 (= neutro q7)
    (0x054EA4, 0x03),  # Eiji frente anim 209 q0
    (0x054ED0, 0x03),  # Eiji neutro anim 20a q0
    (0x054EF8, 0x03),  # Eiji tras anim 20b q0
    (0x055E02, 0x03),  # Jack frente anim 289 q0
    (0x055E22, 0x03),  # Jack neutro anim 28a q0
    (0x055E3A, 0x03),  # Jack tras anim 28b q0
    (0x056D66, 0x03),  # Lee frente anim 309 q0
    (0x056D8A, 0x03),  # Lee neutro anim 30a q0
    (0x056DAE, 0x03),  # Lee tras anim 30b q0
    (0x057CDA, 0x02),  # King frente anim 389 q0
    (0x057D06, 0x02),  # King neutro anim 38a q0
    (0x057D1E, 0x02),  # King tras anim 38b q0
    (0x058B8C, 0x02),  # Micky frente anim 409 q0
    (0x058BBC, 0x02),  # Micky neutro anim 40a q0
    (0x058BDC, 0x03),  # Micky tras anim 40b q0
    (0x059C3E, 0x02),  # John frente anim 489 q0
    (0x059C66, 0x02),  # John neutro anim 48a q0
    (0x059C86, 0x02),  # John tras anim 48b q0
    (0x05AD32, 0x02),  # MrBig frente anim 509 q0
    (0x05AD4A, 0x02),  # MrBig neutro anim 50a q0
    (0x05AD62, 0x02),  # MrBig tras anim 50b q0
    (0x05BAC6, 0x03),  # Takuma frente anim 589 q0
    (0x05BAEE, 0x03),  # Takuma neutro anim 58a q0
    (0x05BB12, 0x03),  # Takuma tras anim 58b q0
    (0x05CAA2, 0x03),  # Yuri frente anim 609 q0
    (0x05CACA, 0x03),  # Yuri neutro anim 60a q0
    (0x05CAE6, 0x03),  # Yuri tras anim 60b q0
    (0x05DD06, 0x02),  # Temjin frente anim 689 q0
    (0x05DD26, 0x02),  # Temjin neutro anim 68a q0
    (0x05DD42, 0x02),  # Temjin tras anim 68b q0
    (0x05ECC2, 0x82),  # Geese frente anim 709 q1
    (0x05ECC6, 0x82),  # Geese frente anim 709 q2
    (0x05ECFA, 0x82),  # Geese neutro anim 70a q1
    (0x05ECFE, 0x82),  # Geese neutro anim 70a q2
    (0x05ED2A, 0x82),  # Geese tras anim 70b q1
    (0x05ED2E, 0x82),  # Geese tras anim 70b q2
]

jump_start = [
    Ins("42ae0020", "clr.l $20(a6)"),               # sem velocidade de andar
    Ins("1d7c00000077", "move.b #$0, $77(a6)"),     # original
    JmpAbs(0x1E3BC),
]

PATCH = Patch(
    id="jump-instant",
    title="Pulo sai na hora e não anda antes de pular (todo o elenco)",
    spec="src/backend/specs/SPEC-023-jump-instant.md",
    blocks=[Block("jump_start", jump_start)],
    hooks=[
        # $1E3B6: move.b #0,$77(a6)  (handler do pulo; segue em $1E3BC)
        Hook(addr=0x1E3B6, expect="1d7c00000077", to_block="jump_start"),
    ],
    data=[
        Data(addr, f"{dur:02x}", f"{(dur & 0x80) | 1:02x}")
        for addr, dur in STOPPED_FRAMES
    ],
)
