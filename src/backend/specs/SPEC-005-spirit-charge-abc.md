# SPEC-005: Carregar a barra com A+B+C

- **Status:** Implementada, aguardando teste em emulador
- **Patch:** `patches/global/spirit-charge-abc` (global)
- **Combina com:** SPEC-002 (ver interação com o arremesso A+B)

## Comportamento desejado

| Entrada | Original | Novo |
|---|---|---|
| Segurar A, **ou** B, **ou** C (sem direção) | Carrega a barra de espírito | Não carrega |
| Segurar A **+** B **+** C juntos (sem direção) | Carrega | Carrega |

O resto da mecânica não muda: são 20 frames na condição para começar a carregar, a carga continua enquanto a condição vale, e direção ou D não contam.

## Mapa de engenharia reversa

| Endereço | O que é |
|---|---|
| `$1B9FE` | Condição de carga: `d0 = 0` (Z) se nenhuma direção (`$0F`) e algum de A/B/C (`$70`) está segurado em `$68` (input bruto) |
| `$1BA16` | Estado neutro: conta 20 frames (`$23E`) na condição e inicia a carga (golpe `$12`) |
| `$1B89A` | Estado de carga: continua enquanto a condição vale; A/B recém-pressionados (`$69 & $30`) interrompem |
| `$1B904` | Soma a taxa de carga (`$1B974`, por personagem) à barra `$224`, até o máximo `$256` |

## Implementação

A rotina `$1B9FE` é reescrita no lugar (24 bytes, sem bloco novo). Ela passa a exigir `($68 & $7F) == $70`: A, B e C segurados e nenhuma direção.

## Interação com a SPEC-002 (pendência)

No patch de controles, A+B é o arremesso. Ao apertar A+B+C, o tradutor de input vê o par A+B e gera o pedido de arremesso:
- **longe do oponente:** o pedido é ignorado e, depois de 20 frames segurando, a barra carrega normalmente;
- **perto do oponente:** sai o arremesso em vez de começar a carga.

Possível ajuste (a decidir): no tradutor da SPEC-002, tratar A+B+C como "sem evento", com o custo de mais latência no arremesso.

## Critérios de aceite (teste manual no FBNeo)

- [ ] Segurar só A, só B ou só C não carrega a barra
- [ ] Segurar A+B+C (longe do oponente) carrega a barra
- [ ] Soltar qualquer um dos três interrompe a carga
- [ ] Segurar A+B+C com uma direção não carrega
