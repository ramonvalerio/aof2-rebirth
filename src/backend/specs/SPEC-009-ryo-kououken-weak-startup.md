# SPEC-009: Ryo: Kou'ouken fraco com startup de 11 frames

- **Status:** Implementada, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/kououken-weak-startup` (personagem)
- **Combina com:** SPEC-004 (botão fraco → `$013`), SPEC-007 (formato de animação), SPEC-008 (special cancel)

## Motivo

Com o special cancel (SPEC-008), chute forte perto → Kou'ouken fraco conecta pela distância, mas o oponente se recupera antes. A conta, com dados da ROM:

| Etapa | Frames |
|---|---|
| Reação do oponente a golpe leve (ex.: Robert, anims `$01D0–$01D3`) | 16–19 |
| Projétil do Kou'ouken (anim `$0140`) | nasce no frame 23 |

O oponente fica livre uns 4 a 7 frames antes de o projétil existir. Reduzir o pushback não resolve; reduzir o startup resolve.

## Comportamento desejado

| Versão | Antes | Depois |
|---|---|---|
| Kou'ouken fraco (A, `$013`) | projétil no frame 23, total 61 | **projétil no frame 11**, total 49 |
| Kou'ouken forte (C, `$011`) | projétil no frame 23 | igual |

Só a preparação encurta. Dano, tamanho do projétil (SPEC-004) e recuperação após o projétil (38 frames) não mudam.

## Implementação

| Alteração | Onde | Original | Novo |
|---|---|---|---|
| Lista de quadros nova (12 × 4 bytes) | `$51F00` | zeros (entradas dos ids `$7C0–$7CB`, sem uso) | cópia da `$0140` com q1–q4 = 2 frames cada |
| Entrada da animação `$17F` | `$050000 + $17F*4` | `$00000000` (id livre) | `$0C051F00` |
| Animação do `$013` | `$23BA4 + $13*16 + 10` | `$0140` | `$017F` |

Duração dos quadros de preparação: q0 3 + q1 8 + q2 4 + q3 4 + q4 4 = 23 → 3 + 2 + 2 + 2 + 2 = **11**.

**Por que `$51F00`:** os quadros de comando (q0 e q5, com o comando que cria o projétil) apontam para a lista de comandos com um offset relativo de 16 bits (`adda.w`, `$4A6E`). Por isso a nova lista precisa ficar a até 32 KB das listas originais (`$531D4`/`$531DB`). A área livre de código (`$FExxx`) não alcança. As entradas zeradas no fim da tabela de animações estão no alcance e não são usadas por nenhuma animação.

## Pendências / riscos

- **IA:** quando a CPU usa a versão fraca (barra baixa, SPEC-004), o Kou'ouken dela também fica rápido.
- **Visual:** a preparação passa de 20 para 8 frames, com os mesmos sprites e menos tempo em cada um.
- **Alcance:** o projétil fraco continua pequeno e de alcance curto. De longe pode não chegar.

## Critérios de aceite (teste manual no FBNeo, com `frame_data.lua`)

- [ ] Kou'ouken com A: `proj` = 11; com C: `proj` = 23
- [ ] Chute forte perto → Kou'ouken fraco (cancel) acerta antes de o oponente se recuperar
- [ ] Soco forte perto → Kou'ouken fraco (cancel) idem
- [ ] Kou'ouken forte continua igual
