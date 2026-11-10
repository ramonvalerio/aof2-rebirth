"""Spirit: LP+LK+HK segurados sem direcao — SPEC-005.

Le $68 apos o remapeamento: LP=$10, LK=$20, HK=$80, total $B0.
O tradutor de controles prioriza a combinacao sobre grab/break.
O limiar de inicio continua em 1 frame. Mantem taxa e limite nativos.
"""
from asm68k import Branch, Ins, Label
from patchlib import Data, Hook, Patch

charge_condition = [
    # Funcoes apos o remapeamento: LP=$10, LK=$20, HK=$80.
    # Exige os tres e nenhuma direcao/soco forte adicional.
    Ins("102e0068", "move.b $68(a6), d0"),
    Ins("0c0000b0", "cmpi.b #$b0, d0"),
    Branch("bne", "no"),
    Ins("7000", "moveq #$0, d0"),
    Ins("4e75", "rts"),
    Label("no"),
    Ins("7001", "moveq #$1, d0"),
    Ins("4e75", "rts"),
]

PATCH = Patch(
    id="spirit-charge-abc",
    title="Carregar Spirit: soco fraco + chute fraco + chute forte",
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
