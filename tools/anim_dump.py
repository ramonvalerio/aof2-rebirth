"""Decodifica animações e frame data da P-ROM do AOF2 (SPEC-007).

Uso:
  python tools/anim_dump.py anim 140 122        # linha do tempo de animações
  python tools/anim_dump.py move 1 11 13        # golpes por id (personagem 1 = Ryo)
  python tools/anim_dump.py cmd 1 21 23 31 33   # golpes por comando ($20 soco, +$10 chute, +1 forte, +2 perto)

Formato (engenharia reversa, ver SPEC-007):
  $0000FC          -> tabela de animações ($050000), 1 long por id:
                      byte alto = nº de quadros, 24 bits = lista de quadros
  quadro (4 bytes) = [duração][flags][offset word]
                      duração bit 7 = quadro simples (offset = índice da peça de sprite);
                      sem bit 7 = lista de comandos em (quadro + 2 + offset)
                      flags -> $A69 do jogador (bit 7 = quadro final; $10/$18 = golpe; $00 = recuperação)
  peças de sprite  = $0CE000 (1 long por índice); word alta: tipo = (hi & $70) >> 4;
                      tipo 3: bits 15..8 = filhos 0..7 do sprite que recebem caixa
  filhos 2,3,4     = caixas de corpo; filhos 5,6 = caixa de ataque
  atributos golpe  = $23BA4 + id*16: +0 dano, +4 custo, +5 hitstop(?), +10 animação, +14 tipo de reação
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_rom import P1_NAME, SRC_ZIP, swap16  # noqa: E402

with zipfile.ZipFile(SRC_ZIP) as z:
    ROM = bytes(swap16(z.read(P1_NAME)))

L = lambda a: int.from_bytes(ROM[a:a + 4], "big")
W = lambda a: int.from_bytes(ROM[a:a + 2], "big")

ANIM_TABLE = L(0xFC)
PIECES = 0x0CE000
MOVE_ATTR = 0x23BA4
MOVE_LISTS = 0x1E848
CMD_MAPS = 0x1E888
ATTACK_CHILDREN = 0b00000110   # filhos 5 e 6 (bit 7 = filho 0)


def timeline(aid):
    """[(quadro, t_inicial, duração, flags, ataque?)]"""
    e = L(ANIM_TABLE + aid * 4)
    count, ptr = e >> 24, e & 0xFFFFFF
    rows, t = [], 0
    for k in range(count):
        f = ptr + k * 4
        dur, flags, off = ROM[f], ROM[f + 1], W(f + 2)
        attack = None
        if dur & 0x80:
            hi = L(PIECES + off * 4) >> 16
            attack = (hi & 0x70) >> 4 == 3 and bool((hi >> 8) & ATTACK_CHILDREN)
        rows.append((k, t, dur & 0x7F, flags, attack))
        t += dur & 0x7F
    return rows


def frame_data(aid):
    rows = timeline(aid)
    active = [(t, d) for _, t, d, _, a in rows if a]
    end = next((t for _, t, _, fl, _ in rows if fl & 0x80), None)
    if not active:
        return {"startup": None, "active": None, "recovery": None, "total": end}
    first = active[0][0]
    last_end = max(t + d for t, d in active)
    return {"startup": first, "active": last_end - first,
            "recovery": end - last_end if end is not None else None, "total": end}


def move(char, mid):
    a = MOVE_ATTR + mid * 16
    return {"id": mid, "anim": W(a + 10), "damage": ROM[a], "cost": ROM[a + 4],
            "byte5": ROM[a + 5], "reaction": ROM[a + 14]}


def cmd_to_move(char, cmd):
    lst, cmap = L(MOVE_LISTS + char * 4), L(CMD_MAPS + char * 4)
    return W(lst + ROM[cmap + cmd] * 8 + 4)


def main(argv):
    mode, *args = argv
    if mode == "anim":
        for a in args:
            print(f"anim {int(a, 16):04X}")
            for k, t, d, fl, atk in timeline(int(a, 16)):
                tag = "ATAQUE" if atk else ("cmd" if atk is None else "")
                print(f"  q{k:<2} t={t:<3} dur={d:<3} flags={fl:02X} {tag}")
        return
    char = int(args[0])
    ids = [int(x, 16) for x in args[1:]]
    if mode == "cmd":
        ids = [cmd_to_move(char, c) for c in ids]
    print("id   anim  startup ativo recup total dano byte5 reação")
    for mid in ids:
        m = move(char, mid)
        fd = frame_data(m["anim"])
        print(f"{mid:03X}  {m['anim']:04X}  {fd['startup']!s:>7} {fd['active']!s:>5} "
              f"{fd['recovery']!s:>5} {fd['total']!s:>5} {m['damage']:>4} {m['byte5']:>5} {m['reaction']:>6}")


if __name__ == "__main__":
    main(sys.argv[1:])
