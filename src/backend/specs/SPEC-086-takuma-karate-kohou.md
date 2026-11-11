# SPEC-086: Takuma (Mr. Karate, START) — Kohou com o corpo do Takuma

- Patch de personagem: `characters/takuma/karate-kohou`.
- Depende de: `global/start-select-flag` (START confirma como B / cor 1 e liga `$3DA` no registro do jogador).
- Status: implementado, conferido no build, verificado no `hook_check` e sincronizado na MiSTer.

O Takuma escolhido com **START** (Mr. Karate) ganha o **Kohou** ($\to \downarrow \searrow$ + soco), golpe clássico do estilo Kyokugenryu que o Takuma não possui na versão padrão de AoF2.

---

## 1. Mapeamento de Engenharia Reversa

| Componente | Endereço / Registro | Descrição |
|---|---|---|
| **Comando** | `$48` | ID livre na faixa `$40`–`$4F` do Takuma (`$62 = 10 / 0xA`). |
| **Linha de Comandos** | `$01DFC2` | O leitor carrega a linha de passos em `$25D04 + ($62-1)*$20`. Para o Mr. Karate, usa linha customizada apontando `$48` para o offset `$0250` ($\to \downarrow \searrow$ + soco do Kohou do Ryo). |
| **Leitor de Passos** | `$01E062` | `charlib.CMD_STEP`: percorre os passos com decremento de prazo por frame. |
| **Conclusão** | `$01E0E6` | Hook encadeado após `haoh-easy-input` (`$01E0E0`): identifica Takuma + START + comando `$48` e grava `$218 = $48`. |
| **Gravação do Comando** | `$01E102` | `move.w d0, $218(a6)` e arma a vida do comando (`$A77 = $3C`). |
| **Despacho** | `$01D41E` (`KICK_SELECT`) | Bloco `dispatch` (`$0F5E16`): intercepta `$48`, seta `$20(a5) = $48` e desvia para o handler de especial `$1D4DC` com o golpe base `$023`. |
| **Força do Golpe** | Handler `$1D4DC` | Soma `+0`, `+1` ou `+2` pelo botão/Spirit: `$023` (fraco), `$024` (médio) e `$025` (forte). |
| **Animação** | `$004A26` | Tocador de animação: se for Mr. Karate com uma das animações `$145`, `$17B` ou `$17E`, substitui pela animação exclusiva `$5F5`. |

---

## 2. Animação `$5F5`

- Montada a partir dos dados do Kohou original (`$145` em `$535E2`, 11 quadros) com listas de comandos de impulso ($D2, vy = `$000CC000`, gravidade = `$FF70`, vx = `$01800000`, som e aterrissagem).
- Peças do Ryo substituídas pelas peças do Takuma:
  - Preparação: `$9C9`
  - Soco para cima com caixa de ataque: `$9E1`
  - No ar: `$9CF`

---

## 3. Validação

- [x] Build da ROM com 81 patches ativos sem colisões.
- [x] Verificação com `hook_check.py`: nenhum desvio para o meio de hooks.
- [x] Testes de regressão de desperations e Zanretsuken 100% PASS.
- [x] Sincronização direta no MiSTer FPGA (`/media/fat/games/NEOGEO/1 World A-Z/Art of Fighting 2 Rebirth (aof2r).neo`).
- [ ] Validação prática no emulador/hardware real com script `tools/lua/karate_kohou_trace.lua`.
