"""spirit-charge-abc — SPEC-005.

Carregar a barra de espírito passa a exigir A+B+C segurados juntos
(no original bastava segurar A, B ou C).

$1B9FE é a condição de carga (Z=1 / d0=0 quando vale), lida do input bruto
$68(a6): nenhuma direção segurada e (original) qualquer bit de $70.
Usada em $1BA28 (20 frames na condição -> entra em carga) e $1B89E
(continua carregando enquanto vale). A rotina é reescrita no lugar.

Início instantâneo: o neutro ($1BA2C) soma 1 em $23E a cada frame na
condição e só entra na carga com $23E >= $14 (20 frames, $1BA30). O
limite passa a 1: a carga começa no 1º frame com A+B+C segurados.
"""
from asm68k import Branch, Ins, Label
from patchlib import Data, Hook, Patch

charge_condition = [
    # direções ($0F) e A/B/C ($70) do input bruto; D é ignorado como no original
    Ins("707f", "moveq #$7f, d0"),
    Ins("c02e0068", "and.b $68(a6), d0"),
    Ins("0c000070", "cmpi.b #$70, d0"),
    Branch("bne", "no"),
    Ins("7000", "moveq #$0, d0"),
    Ins("4e75", "rts"),
    Label("no"),
    Ins("7001", "moveq #$1, d0"),
    Ins("4e75", "rts"),
]

PATCH = Patch(
    id="spirit-charge-abc",
    title="Carregar a barra exige A+B+C segurados juntos",
    spec="src/backend/specs/SPEC-005-spirit-charge-abc.md",
    hooks=[
        # rotina original inteira ($1B9FE-$1BA15, 24 bytes)
        Hook(addr=0x1B9FE, expect="700fc02e0068660c7070c02e006867047000" "4e7570014e75",
             program=charge_condition),
    ],
    data=[
        # $1BA30: cmpi.b #$14,$23e(a6) -> #$01
        Data(0x1BA33, "14", "01"),
    ],
)
