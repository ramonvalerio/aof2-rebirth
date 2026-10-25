"""desperation-ryo-command — SPEC-028.

O DESPERATION de Robert, Takuma e Yuri sai com o mesmo comando do Ryo:
baixo, baixo-frente, frente, baixo-frente, baixo, baixo-trás, trás + C.

Tabela de comandos ($1DFC2): linha = $25D04 + ($62 - 1) * $20, uma word
por comando $40-$4F com o offset da lista de passos. O DESPERATION é o
comando cujo handler é $1D460 (vida <= $20 e barra >= $60):
  Ryo    $46 -> +$A0E  v v> -> v> v <v <- + C
  Robert $46 -> +$A4E  igual ao Ryo (nada a mudar)
  Takuma $45 -> +$966  v v> -> <- -> + A+B
  Yuri   $45 -> +$5D8  -> <- -> v> v <v <- + B+C   (Hien Hou'oukyaku)
Takuma e Yuri passam a apontar para a lista do Ryo. As listas originais
não mudam (outras linhas podem usar).
"""
from patchlib import Data, Patch

COMMANDS = 0x025D04
RYO_DESPERATION = 0xA0E


def slot(char, cmd):
    return COMMANDS + (char - 1) * 0x20 + (cmd - 0x40) * 2


# (personagem $62, comando, offset original)
CHANGES = [
    (10, 0x45, 0x966),   # Takuma
    (11, 0x45, 0x5D8),   # Yuri: Hien Hou'oukyaku
]

PATCH = Patch(
    id="desperation-ryo-command",
    title="DESPERATION de Robert, Takuma e Yuri com o comando do Ryo",
    spec="src/backend/specs/SPEC-028-desperation-ryo-command.md",
    data=[
        Data(slot(char, cmd), f"{old:04x}", f"{RYO_DESPERATION:04x}")
        for char, cmd, old in CHANGES
    ],
)
