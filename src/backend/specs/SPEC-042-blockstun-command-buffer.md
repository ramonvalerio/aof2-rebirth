# SPEC-042: Comando de especial durante o blockstun

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/global/blockstun-command-buffer` (global)
- **Ferramenta:** `tools/lua/command_trace.lua` (rastreio frame a frame do leitor de comandos)

## Comportamento desejado

Para todos os personagens: o comando de um especial (ex.: Kohou, →↓↘ + soco) feito **durante a defesa** é reconhecido e o especial sai no **1º frame livre**. A defesa não é cancelada, nada sai durante o blockstun e a duração dele não muda. Comando feito cedo demais na defesa (mais de 12 frames antes do fim) expira.

## Rastreio (command_trace.lua, Ryo, 6 defesas)

| | Neutro / andando | Blockstun (estado 15, 27 frames) |
|---|---|---|
| Direções em `$270` | corretas | **corretas** (← depois → ↓ ↘) |
| Leitor `$1DF7E` | todo frame | **não roda** (só no último frame, já fora do handler) |
| Slot do Kohou (`$A2C`) | avança (`$0258`, `$0260`) | **parado em `0000`** |
| Especial pendente `$218` | — | sempre 0 |

Depois da defesa o leitor volta, mas o →↓↘ já passou: o botão sai como golpe normal (estado 3).

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| `$9212` / `$9D24` | Joystick bruto → objeto de input do jogador (`$68` segurado, `$69` apertado, `$6A` solto) |
| `$1B69C` → `$1D87C` | Tradutor: gera `$270`/`$271` **todo frame, em qualquer estado** (antes do despacho do estado `$1B6D4`) |
| `$1DF7E` | Leitor de comandos: compara `$270` com os passos da tabela `$25D04`; progresso por comando em `$A10 + 4×(cmd−$40)` (word passo, byte prazo, byte espera); reconhecido → `$218` e `$A77 = $3C` (`$1E102`/`$1E106`) |
| `$1B7F2` | Todo frame: `$A77 − 1`; em 0 apaga `$218` |
| `$1B70E` | Tabela de estados (`$40`). Estado **15** = blockstun → `$1C604` |
| **`$1C604`** | **`clr.w $218(a6)`**: apaga o pendente em todo frame da defesa; o handler **não chama** `$1DF7E` |
| `$1C656` → `$1C542` → `$1C580` | Fim do blockstun: executa `$218` (`jsr $1D41E`) no 1º frame livre |
| `$1DF16` | Zera todos os slots (só depois de um especial reconhecido); entrar/sair da defesa não zera nada |

(Estados 6/7, reação a golpe, têm outra condição: o leitor só roda em quadros com flag `$02`, `$1C47C`. Não muda aqui.)

## Implementação

Hook em `$1C604` (`clr.w $218` / `clr.b $253`, segue em `$1C60C`):

1. `$218` é apagado como no original **se** `$A77 > 12` (pendente que veio de antes da defesa);
2. `jsr $1DF7E`: os slots acompanham as direções da defesa;
3. se o especial foi reconhecido neste frame (`$A77 = $3C` e `$218 ≠ 0`), `$A77 = 12`: só sai se a defesa acabar em até 12 frames.

## Pendências / riscos

- Pendente vindo de antes da defesa com `$A77 ≤ 12` (quase expirando) também é mantido.
- Hitstun (estados 6/7) não muda: reversal depois de apanhar continua como no original.

## Critérios de aceite

- [ ] Defender e fazer →↓↘ + soco no fim da defesa: o Kohou sai no 1º frame livre
- [ ] Comando feito no começo de uma defesa longa: expira, não sai
- [ ] Nada sai durante a defesa; a duração do blockstun não muda
- [ ] `command_trace.lua`: no estado 15 o slot do comando avança
