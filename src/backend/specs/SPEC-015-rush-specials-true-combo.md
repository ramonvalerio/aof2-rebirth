# SPEC-015: Especiais de sequência (Renbuken e similares) com todos os hits em combo

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/global/rush-specials-true-combo` (global; antes `characters/ryo/renbuken-true-combo`)
- **Combina com:** SPEC-013 (contador: deve mostrar "4 HIT COMBO"), SPEC-007 (formato de animação)

## Comportamento desejado

Depois que o 1º soco do Renbuken (meia-lua para trás + soco) acerta, os outros 3 pegam garantido, sem chance de defesa. O contador mostra **4 HIT COMBO**.

## Mapa de engenharia reversa

| Item | Valor |
|---|---|
| Golpe | id `$021`, comando `$45`, handler `$1D644` |
| Atributos | dano `$0C`, efeito de acerto `$2E` (age só no último hit), **hits extras `$03`** (byte 7 → `$247`, decrementado por hit em `$21338`) |
| Animação | `+10 = $8024` (bit 15 = **sequência**): `$1D73A` → tabela `$233BE` + `$90` → lista em `$2385E` |
| Sequência | `$8120` → `$8122` → `$8120` → `$0121` (bit 15 = encadeia a próxima quando a atual chega ao quadro final `$80`, em `$4A90`) |
| `$120` | soco fraco longe: ataque em t=2–5, fim em 7 |
| `$122` | soco forte longe: ataque em t=4–9, **recuperação 8 + 8**, fim em 26 |
| `$121` | golpe final: ataque em t=6–14, fim em 29 |

## Medição (`frame_data.lua`, colado no Robert parado)

| Frame (após o 1º hit) | Evento |
|---|---|
| 0 | 1º hit (`$120`) |
| 9–14 | caixa do 2º hit (`$122`), acerta em 10 |
| 15–33 | Ryo sem caixa de ataque (recuperação da `$122` + preparação da `$120`) |
| **27–33** | **oponente livre** (animação `$0580`) |
| 35 | 3º hit; 45: 4º hit |

A distância ficou constante (47–51 px): não há recuo. O problema é só o buraco de tempo entre o 2º e o 3º hit, quando o oponente fica livre e pode defender.

## Generalização (v2: global)

O mesmo tipo de golpe existe em outros personagens: sequência de animações + hits extras, com um trecho sem caixa de ataque longo demais.

| Personagem | Golpe | Sequência (lista) | Copiada | Encurtado |
|---|---|---|---|---|
| Ryo | `$021` | `$120 $122 $120 $121` (`$2385E`) | `$122` → `$17D` @ `$51F90` | recuperação 8+8 → 2+2 |
| Robert | `$046` | `$1A0 $1A2 $1A0 $1A1` (`$2386A`) | `$1A2` → `$177` @ `$51FA8` | recuperação 8+8 → 2+2 |
| Eiji | `$06B` | `$238 $231` (`$23710`) | `$238` → `$178` @ `$51FC0`; `$231` → `$271` (bloco) | entre hits 4+3+3+3+3 → 2+1+1+1+1; antes do 3º hit 6+3+3+3 → 1+1+1+1 |
| Takuma | `$163` | `$5A0 $5A2 $5A0 $5A1` (`$23876`) | `$5A2` → `$179` (bloco no espaço livre) | recuperação 8+8 → 2+2 |
| Yuri | `$186` (C para trás + chute) | `$620 $631 $62B $63A` (`$237E0`) | `$631/$62B/$63A` → `$272/$273/$274` (bloco) | buracos de 15 e 14 frames → ~7 |

O Takuma não tem área livre ao alcance de 16 bits da lista de comandos original (`$5BDC8`: `c7 0044`, `c7 0294`, peça `09dc`). Por isso esses 8 bytes são copiados junto dos quadros num `DataBlock`. Ryo, Robert e Takuma foram analisados pela estrutura (mesmo padrão do Ryo, que foi medido). Ryo, Robert e Takuma foram confirmados em jogo.

**v3:** o Eiji ainda dava só 2 hits. O 3º hit dele está na `$231`, aplicado pelo opcode `$DE` (zera os hits extras `$247`) junto com a peça de ataque `$3F6`, e chegava cerca de 13 frames depois do 2º. A Yuri (`$186`) tem o mesmo tipo de golpe. As listas de comandos dela e da `$231` não têm área livre ao alcance de 16 bits, então são copiadas para dentro dos blocos (opcodes `$C7` com 2 bytes, `$EC` com 1, `$DE` com 0; a lista termina numa peça).

Outros golpes do mesmo tipo, não alterados (sem relato de problema): Jack `$08C` (buracos 9 e 14), Lee `$0AA` (7 e 12), Micky `$0F2` (12 e 16).

## Implementação original (Ryo)

| Alteração | Onde | Original | Novo |
|---|---|---|---|
| Animação nova `$17D` (cópia da `$122`) | quadros em `$51F90` (ids livres `$7E4+`); entrada `$050000 + $17D*4` | `0` | 6 quadros, q3/q4 = **2 + 2** (eram 8 + 8) |
| Sequência do Renbuken | `$23860` (2º item) | `$8122` | `$817D` |

Novo tempo esperado: 3º hit em t ≈ 20, dentro da reação do oponente (que termina em t ≈ 27). O soco forte longe normal (`$122`) não muda. A sequência `$8024` é usada só pelo `$021`.

## Pendências

- **Visual:** a pausa depois do soco forte dentro do Renbuken fica bem mais curta.
- Confirmar o 4º hit (`$121`) com a nova cadência e o "4 HIT COMBO" no contador.

## Critérios de aceite

- [ ] Renbuken colado: 4 hits seguidos, o contador mostra "4 HIT COMBO"
- [ ] Depois do 1º hit, o oponente não consegue defender o resto
- [ ] Soco forte longe normal continua igual
- [ ] Robert, Takuma e Eiji: todos os hits do golpe equivalente em combo, sem defesa
