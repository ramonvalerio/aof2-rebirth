"""hien-weak-startup (Ryo) — SPEC-022.

Hien Shippuukyaku fraco (comando $43, golpe $01D, botão B; SPEC-004) com
startup instantâneo.

O $01D usa a sequência $8006 -> anim $13E, que tem um quadro só: um quadro
de comando de 12 frames cuja lista ($533BC) toca os sons, dá a velocidade do
salto ($D2: vy $00048000, gravidade $FFD0, vx $0600), pede a próxima
animação ($CF 00 $4144: o voo do forte, $144) e mostra a peça $068B. Os
chutes (caixas de ataque) só começam na $144. Esses 12 frames parados na
peça de arranque são o startup.

Patch: o quadro passa a durar 1 frame. O Hien forte ($01B, anim $144, o
mesmo arranque de 12 frames no q0) não muda.
"""
from patchlib import Data, Patch

WEAK_HIEN_Q0 = 0x053340        # anim $13E, quadro 0: [duração][flags][offset]

PATCH = Patch(
    id="hien-weak-startup",
    title="Ryo: Hien Shippuukyaku fraco com startup instantâneo",
    spec="src/backend/specs/SPEC-022-ryo-hien-weak-startup.md",
    data=[
        Data(WEAK_HIEN_Q0, "0c", "01"),   # 12 -> 1 frame (quadro de comando, sem bit 7)
    ],
)
