# SPEC-032: Ryo: chute fraco em pé com o tempo do soco fraco em pé

- **Status:** Implementado, aguardando teste em emulador
- **Patch:** `patches/characters/ryo/standing-lk-frames` (personagem, dados)

## Comportamento desejado

O chute fraco em pé do Ryo (B, longe e perto) tem o mesmo startup, ativo e recovery do soco fraco em pé.

| Golpe | Anim | Startup | Ativo | Recovery | Total |
|---|---|---|---|---|---|
| Soco fraco em pé (referência) | `$120` | 2 | 4 | 1 | 7 |
| Chute fraco em pé (original) | `$130` | 4 | 8 | 8 | 20 |
| Chute fraco em pé (novo) | `$130` | 2 | 4 | 1 | 7 |

## Implementação

A animação `$130` (lista de quadros em `$52FAC`) só é usada pelo golpe `$009` (o mesmo para longe e perto). Durações (byte 0 de cada quadro; bit 7 = quadro simples):

| Quadro | Original | Novo |
|---|---|---|
| q0 (lista de comandos) | 2 | 1 |
| q1 | 2 | 1 |
| q2 (caixa de ataque) | 8 | 4 |
| q3 (recuperação) | 4 | 1 |
| q4 (recuperação) | 4 | vira o quadro final (`$80`, mesma peça `$62C` do q5) |

Dano, hitstop e reação do golpe não mudam.

## Pendências / riscos

- **Visual:** o chute fica mais rápido; a pose de recolher a perna aparece por 1 frame.
- **Hitstun:** a reação do oponente não muda. Como o recovery cai de 8 para 1, a vantagem sobe bastante (igual à do soco fraco).

## Critérios de aceite

- [ ] `python tools/anim_dump.py cmd 1 30 32` mostra startup 2, ativo 4, recovery 1, total 7
- [ ] Chute fraco em pé, longe e perto, sai e acerta normalmente
- [ ] Frame data igual à do soco fraco em pé no `hitbox_viewer.lua` / `frame_data.lua`
