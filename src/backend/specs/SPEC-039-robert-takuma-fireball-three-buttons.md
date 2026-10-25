# SPEC-039: Robert e Takuma: projétil com três versões pelo botão

- **Status:** Implementado, aguardando teste em emulador
- **Patches:** `patches/characters/robert/ryugekiken-three-buttons`, `patches/characters/takuma/kououken-three-buttons` (personagem)
- **Mecanismo:** `charlib.fireball_three_buttons` (o mesmo do Ryo, SPEC-033)

## Comportamento desejado

| Comando | Versão | Robert (Ryugekiken) | Takuma (Kou'ouken) | Derruba |
|---|---|---|---|---|
| ↓↘→ + C + D (soco fraco + soco forte) | Fraco | `$03B` | `$157` | **Sim** (cancel e combos) |
| ↓↘→ + C (soco fraco) | Médio | `$03A` | `$156` | Não |
| ↓↘→ + D (soco forte) | Forte | `$039` | `$155` | Não |

Os três golpes de cada um usam a mesma animação (Robert `$1C0`, total 62; Takuma `$5C0`, total 50): mudam dano e tamanho do projétil. Nenhum tem versão de "falha" (custo sem bit 7), então o fraco é o id+2.

## Implementação (`charlib.fireball_three_buttons`)

1. **Versão pelo botão** (hook compartilhado `$1D676`): comando do jogador (`$218` bit 9) e golpe do personagem → bit 10 (C+D, marcado pelo `special-strength-by-button`) = fraco, bit 8 = forte, senão médio. Grava `$10(a5)`, `$5C(a4)` e a barra equivalente `$23F` (tamanho do projétil em `$22A5C`).
2. **Comando com C+D** (hook compartilhado `$1E062`): o passo final do ↓↘→ + soco (`$1B8`, `f0 10`) recusa o par C+D (`$50`, bit 6 "C segurado"). Só para o personagem, a máscara perde o bit 6.
3. **Queda:** efeito de acerto (byte 6) do fraco `$00` → `$01`.

O patch do Ryo (`kououken-three-buttons`, SPEC-033) passou a usar o mesmo helper, sem mudar o comportamento.

## Pendências / riscos

- **Startup:** o fraco de Robert e Takuma tem o mesmo startup do médio/forte (o do Ryo foi acelerado à parte, SPEC-009). Para combar de cancel, pode precisar de um ajuste igual.
- **Queda pelo projétil** e **uppercut no C+D**: mesmos pontos da SPEC-033.

## Critérios de aceite

- [ ] Robert: ↓↘→ + C+D = Ryugekiken fraco (projétil pequeno, derruba); C = médio; D = forte
- [ ] Takuma: idem com o Kou'ouken
- [ ] C+D sem o movimento continua sendo o uppercut
- [ ] Ryo continua igual (SPEC-033)
