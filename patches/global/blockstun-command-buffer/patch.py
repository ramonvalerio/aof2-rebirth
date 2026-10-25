"""blockstun-command-buffer — SPEC-042.

Comando de especial feito durante o blockstun é reconhecido e sai no 1º
frame livre (como nos jogos modernos), sem cancelar a defesa.

Blockstun = estado 15 ($1C604; rastreio command_trace.lua: 27 frames com o
leitor parado e as direções certas em $270). O handler:
  - nunca chama o leitor de comandos ($1DF7E): os slots $A10 + 4*(cmd-$40)
    não avançam com as direções da defesa;
  - começa com clr.w $218(a6): apaga o especial pendente em todo frame.
Na saída ($1C656 -> $1C542 -> $1C580) o jogo já executa $218 no 1º frame
livre, mas ele sempre chegava vazio.

Hook em $1C604 (clr.w $218 / clr.b $253):
  1. $218 continua apagado se veio de antes da defesa ($A77 > WINDOW);
  2. jsr $1DF7E: os slots acompanham as direções da defesa;
  3. especial reconhecido neste frame ($A77 = $3C, $1E106) -> $A77 = WINDOW:
     só sai se a defesa acabar em até WINDOW frames ($1B7F2 decrementa e apaga).
Nada é executado durante a defesa (o estado 15 não chama $1D808); a
duração do blockstun não muda.
"""
from asm68k import Branch, Ins, JmpAbs, Label
from patchlib import Block, Hook, Patch

WINDOW = 12     # frames de vida do especial reconhecido na defesa (= prazo entre passos, SPEC-008)

block_reader = [
    Ins(f"0c2e{WINDOW:04x}0a77", f"cmpi.b #${WINDOW:x}, $a77(a6)"),
    Branch("bls", "keep"),                            # reconhecido na defesa: mantém
    Ins("426e0218", "clr.w $218(a6)"),                # original: apaga o pendente antigo
    Label("keep"),
    Ins("4eb90001df7e", "jsr $1df7e.l"),             # leitor de comandos
    Ins("0c2e003c0a77", "cmpi.b #$3c, $a77(a6)"),     # reconhecido agora ($1E106)?
    Branch("bne", "done"),
    Ins("4a6e0218", "tst.w $218(a6)"),
    Branch("beq", "done"),
    Ins(f"1d7c{WINDOW:04x}0a77", f"move.b #${WINDOW:x}, $a77(a6)"),
    Label("done"),
    Ins("422e0253", "clr.b $253(a6)"),                # original
    JmpAbs(0x1C60C),
]

PATCH = Patch(
    id="blockstun-command-buffer",
    title="Comando de especial feito durante a defesa sai no 1º frame livre",
    spec="src/backend/specs/SPEC-042-blockstun-command-buffer.md",
    blocks=[Block("block_reader", block_reader)],
    hooks=[
        # $1C604: clr.w $218(a6) / clr.b $253(a6)  (segue em $1C60C)
        Hook(addr=0x1C604, expect="426e0218422e0253", to_block="block_reader"),
    ],
)
