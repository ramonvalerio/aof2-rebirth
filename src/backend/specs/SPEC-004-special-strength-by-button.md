# SPEC-004: Força do especial definida pelo botão

- **Status:** Implementada, aguardando teste em emulador
- **Patch:** `patches/global/special-strength-by-button` (global)
- **Decisão relacionada:** [ADR-0004](../adr/ADR-0004-special-strength-tag-in-command.md)
- **Combina com:** SPEC-002 (C/D marcam "forte" em `$271`) e SPEC-003 (especiais sem custo)

## Comportamento desejado

Independente do nível da barra de espírito (Rage):

| Botão usado no comando | Versão do especial |
|---|---|
| Soco fraco (A) / chute fraco (B) | Fraca, igual à de barra vermelha. Se nessa versão o golpe "falha" (não sai), usa a versão média |
| Soco forte (C) / chute forte (D) | Forte, igual à de barra cheia |

**Versão de falha:** em 10 especiais (Ryo, Robert, Lee, King, Micky, Takuma e Yuri), a versão de barra vermelha (id+2) não é um golpe fraco, e sim a animação de falha que o original mostra quando falta barra. Exemplos: Zanretsuken e Kohou do Ryo. Ela é identificada pelo bit 7 no byte de custo da tabela `$23BA4` (`$A0`, `$A4`, `$B0`...). Nesses golpes, o botão fraco usa a versão média (id+1), para que o golpe sempre saia. SUPER e DESPERATION não passam por essa regra e continuam como no original.

## Comportamento original (referência)

`$1D53E`, rotina comum dos especiais com níveis:

| Barra (`$224`) | Nível (`$5C(a4)`) | Variante (`$10(a5)`) |
|---|---|---|
| ≥ `$40` | 3 | id + 0 (forte) |
| ≥ `$20` | 2 | id + 1 |
| < `$20` (vermelha) | 1 | id + 2 (fraca) |

Os limites ficam em `$22AF0` (`$20`, `$40`).

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| `$1DFA0` | Leitor de comandos de especial (só para jogador humano, ver `$1DF7E`). Compara o histórico com `$270` |
| `$1E102` | Grava o comando detectado em `$218(a6)` e arma o buffer `$A77` = 60 frames |
| `$1B7F2` | Apaga `$218` quando o buffer expira |
| `$1D82A` | Executa o `$218` pendente quando o jogador pode agir → `$1D41E` (`andi.w #$7f`) |
| `$1D53E` | Escolhe o nível/variante pela barra (ponto do segundo hook) |
| `$1D676` | Continuação comum depois do nível; `$1D69A` apaga `$218` |
| `$1D7DE` | Copia a barra para `$23F(a6)` antes de descontar o custo |
| `$22A5C` | Criação do projétil: o **tamanho** (`$3C`, sprite `$54`) sai de `$23F` com os mesmos limites `$20`/`$40` |

## Implementação

1. **Na detecção (`$1E102`)**: o comando ganha o bit 9 (`$200`, "veio do jogador"). Se `$271` tem o bit 4 ou 5 (botão forte no frame do aperto), ganha também o bit 8 (`$100`).
2. **Na escolha do nível (`$1D548`)**:
   - sem bit 9 → regra original pela barra (IA)
   - bit 9 e bit 8 → nível 3 / id + 0
   - bit 9 sem bit 8 → nível 1 / id + 2; se `$23BA4[(id+2)*16 + 4]` tem o bit 7 (versão de falha) → nível 2 / id + 1

3. **Tamanho do projétil**: a escolha também grava em `$23F` uma barra equivalente ao botão, com o bit 7 como marca (forte `$C0`, médio `$A0`, fraco `$80`). O hook em `$1D7DE` mantém esse valor (sem o bit 7) em vez de copiar a barra. Sem marca (IA e golpes fora de `$1D53E`), a cópia da barra é a original. A barra real vai no máximo até `$78`, então o bit 7 nunca aparece nela.

O patch `free-special-moves` só zera custos abaixo de `$80`, então o bit 7 das versões de falha continua na tabela para essa checagem.

Outros leitores de `$218` não são afetados pelos bits 8/9:
- `$1D41E` mascara com `$7F`.
- `$1C104` usa `btst.l` com registrador, que no 68000 é módulo 32.
- `$2707A` e `$28AD8` só comparam "≥ `$40`/`$41`".
- `$27FB2` e `$28A78` são da IA, que não passa pelo detector.

A força vem de `$271` bits 4/5. Na SPEC-002 isso corresponde a C/D. Sem o patch de controles, corresponde ao A/B segurado do original. Os dois patches funcionam juntos ou separados.

## Pendências / riscos

- **IA**: segue a regra da barra. Se a CPU também passar pelo detector em algum modo (por exemplo, a demo), passa a usar a regra do botão.
- **Especiais sem os 3 níveis**: o original sempre soma 0/1/2 ao id nessa rotina, então todos os golpes que passam por ela têm as 3 variantes.

## Critérios de aceite (teste manual no FBNeo)

- [ ] Bola de fogo com A, com barra cheia: sai a versão fraca (de barra vermelha), com projétil pequeno
- [ ] Bola de fogo com C, com barra vermelha: sai a versão forte (de barra cheia)
- [ ] Especial de chute: B sai fraco e D sai forte
- [ ] Zanretsuken e Kohou do Ryo saem com A (versão média), sem gastar barra
- [ ] Especial feito durante uma animação (buffer) mantém a força do botão usado
- [ ] CPU continua soltando especiais normalmente

## Histórico

- **Kou'ouken com A saía forte com a barra cheia.** A versão do golpe (id+2) estava certa, como mostrou a gravação Lua (`LEVEL $11` → `CHOSEN $13`). Mas o tamanho do projétil é recalculado em `$22A5C` a partir da cópia da barra (`$23F`), que continuava cheia. Corrigido com o terceiro hook (`$1D7DE`).

## Specs relacionadas

Pares de chutes: o detector guarda bit 11 de $218 a partir de $68 & $A0.
Pares de socos usam bit 10. Os marcadores selecionam versões conforme
as specs de cada personagem, sem mudar a regra global padrão.
Índice de exceções: [personagens e globais](README.md).

Atualização: o custo dos fortes com dois botões segue [SPEC-063](SPEC-063-two-button-strong-spirit-cost.md).
