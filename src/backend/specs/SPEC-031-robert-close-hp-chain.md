# SPEC-031: Robert: soco forte perto cancela em B + D

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/global/normal-chains` (linha do Robert na tabela `CHAINS`)
- **Referência:** SPEC-020 (o mesmo chain no Ryo)

## Comportamento desejado

O soco forte perto do Robert, ao conectar (acerto ou defesa), cancela em **B + D** (chute baixo).

## Implementação

O patch `normal-chains` virou global com uma tabela `CHAINS` de linhas `(personagem $62, golpe atual $230, botões)`, porque o hook (`$1C066`) é um só:

| Personagem | Golpe (`$230`) | Botões (byte alto de `$270`/`$274`) | Resultado |
|---|---|---|---|
| Ryo | `$38` baixo B | `$20` chute | baixo B / baixo D |
| Ryo | `$23` soco forte perto | `$60` B+D | chute baixo |
| **Robert** | **`$23` soco forte perto** (golpe `$02E`, anim `$1A7`) | **`$60` B+D** | **chute baixo (`$34` → `$033`)** |

O resto do chain é o da SPEC-020: depois do contato (`$21B = 0`), `$274 & $7070` → `$270`, `jsr $1D808`; se começou, rearma os filhos 5/6 e sai como o special cancel (`$1C0BA`). As linhas do Ryo não mudaram; o buffer do baixo B e o byte 14 continuam só do Ryo.

## Critérios de aceite

- [ ] Robert: soco forte perto acerta → B+D sai na hora (2 HIT COMBO)
- [ ] Defendido: também cancela
- [ ] Sem contato: não cancela
- [ ] Ryo: chains iguais
