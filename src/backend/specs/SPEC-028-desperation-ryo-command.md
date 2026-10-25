# SPEC-028: DESPERATION de Robert, Takuma e Yuri com o comando do Ryo

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/takuma/desperation-ryo-command` e `patches/characters/yuri/desperation-ryo-command` (dados; o Robert já usa o comando do Ryo)

## Comportamento desejado

O DESPERATION de Robert, Takuma e Yuri (Hien Hou'oukyaku) sai com o mesmo comando do Ryo: **↓ ↘ → ↘ ↓ ↙ ← + C**. Os requisitos (vida ≤ `$20`, barra ≥ `$60`, handler `$1D460`) não mudam.

## Mapa de engenharia reversa

Tabela de comandos `$1DFC2`: linha = `$25D04 + ($62 − 1) × $20`, uma word por comando (`$40`–`$4F`) com o offset da lista de passos.

| Personagem | Comando | Slot | Lista original | Movimento original |
|---|---|---|---|---|
| Ryo | `$46` | `$25D10` | `+$A0E` | ↓ ↘ → ↘ ↓ ↙ ← + C |
| Robert | `$46` | `$25D30` | `+$A4E` | igual ao Ryo |
| Takuma | `$45` | `$25E2E` | `+$966` | ↓ ↘ → ← → + A+B |
| Yuri | `$45` | `$25E4E` | `+$5D8` | → ← → ↘ ↓ ↙ ← + B+C |

## Implementação

Os slots do Takuma e da Yuri passam a apontar para `+$A0E` (a lista do Ryo). Robert já tinha o mesmo movimento e não muda. As listas originais continuam no lugar.

## Critérios de aceite

- [ ] Robert, Takuma e Yuri: ↓ ↘ → ↘ ↓ ↙ ← + C, com vida piscando e barra cheia, sai o DESPERATION
- [ ] O comando antigo do Takuma e da Yuri não sai mais
- [ ] Os outros especiais deles não mudam
