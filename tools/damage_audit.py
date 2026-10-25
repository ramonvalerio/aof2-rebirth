"""Audita atributos de dano do Ryo na ROM gerada, sem estimar dano real.

Uso: python tools/damage_audit.py
Saidas: build/ryo-damage-audit.csv e specs/characters/ryo/damage-audit.md.
Nao altera a ROM. Executar build_rom.py antes para atualizar a entrada.
"""
import csv
import hashlib
from pathlib import Path
import zipfile

from build_rom import ROOT, OUT_ZIP, P1_NAME, load_patch, manifest_ids, swap16
from asm68k import Raw

TABLE = 0x23BA4
ROWS = [
    ("Normal", "Soco fraco em pe (perto/longe)", 0x000),
    ("Normal", "Soco forte longe", 0x002),
    ("Normal", "Soco forte perto", 0x007),
    ("Normal", "Uppercut (dois socos)", 0x001),
    ("Normal", "Soco fraco agachado", 0x003),
    ("Normal", "Soco forte agachado", 0x004),
    ("Normal", "Soco fraco aereo", 0x005),
    ("Normal", "Soco forte aereo", 0x006),
    ("Arremesso", "Arremesso: registro nativo (medir total)", 0x008),
    ("Normal", "Chute fraco em pe (perto/longe)", 0x009),
    ("Normal", "Overhead (frente + chute fraco)", 0x00A),
    ("Normal", "Chute forte longe (tras + chute forte)", 0x00B),
    ("Normal", "Chute baixo (soco forte + chute forte)", 0x00C),
    ("Normal", "Chute fraco agachado", 0x00D),
    ("Normal", "Chute forte agachado", 0x00E),
    ("Normal", "Chute fraco aereo", 0x00F),
    ("Normal", "Chute forte aereo", 0x010),
    ("Kou'ouken", "Terrestre forte", 0x011),
    ("Kou'ouken", "Terrestre medio", 0x012),
    ("Kou'ouken", "Terrestre fraco", 0x013),
    ("Kou'ouken aereo P", "Forte", 0x014),
    ("Kou'ouken aereo P", "Medio (sem botao dedicado)", 0x015),
    ("Kou'ouken aereo P", "Fraco", 0x016),
    ("Kou'ouken aereo K", "Forte", 0x017),
    ("Kou'ouken aereo K", "Medio (sem botao dedicado)", 0x018),
    ("Kou'ouken aereo K", "Fraco", 0x019),
    ("SUPER", "Haoh Shoukouken", 0x01A),
    ("Hien Shippuukyaku", "Forte", 0x01B),
    ("Hien Shippuukyaku", "Medio (sem botao dedicado)", 0x01C),
    ("Hien Shippuukyaku", "Fraco", 0x01D),
    ("Zanretsuken", "Forte", 0x01E),
    ("Zanretsuken", "Medio (usado pelo botao fraco)", 0x01F),
    ("Falha", "Zanretsuken: nao e versao fraca funcional", 0x020),
    ("Renbuken", "Sequencia (medir quatro contatos)", 0x021),
    ("DESPERATION", "Ryukou Ranbu", 0x022),
    ("Kohou", "Forte (dois hits)", 0x023),
    ("Kohou", "Fraco (um hit com SPEC-010)", 0x024),
    ("Falha", "Kohou: nao e terceira versao funcional", 0x025),
]


def audit(rom):
    result = []
    for kind, name, mid in ROWS:
        offset = TABLE + mid * 16
        result.append((kind, name, f"${mid:03X}", offset, bytes(rom[offset:offset + 16])))
    # Registro substituido por hook: o comando $3F nao usa os atributos
    # de $00B, apesar de o mapa de comandos apontar para essa entrada.
    patch = load_patch("characters/ryo/overhead-kick")
    records = [bytes.fromhex(item.hex) for block in patch.blocks
               if hasattr(block, "program") for item in block.program
               if isinstance(item, Raw) and len(bytes.fromhex(item.hex)) == 16]
    assert len(records) == 1
    offset = rom.find(records[0])
    if offset < 0:
        raise ValueError("ROM sem o registro customizado do chute neutro: gere com todos os patches")
    result.insert(10, ("Normal", "Chute forte neutro (registro proprio)", "$3F hook", offset, records[0]))
    return result


def main():
    with zipfile.ZipFile(OUT_ZIP) as z:
        rom = bytes(swap16(z.read(P1_NAME)))
    rows = audit(rom)
    out = ROOT / "build" / "ryo-damage-audit.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["grupo", "golpe", "id", "endereco", "acerto_0", "acerto_1",
                         "defesa_0", "defesa_1", "custo_tabela", "extras_tabela", "registro_hex"])
        for kind, name, mid, addr, record in rows:
            writer.writerow([kind, name, mid, f"${addr:06X}", *record[:4], record[4], record[7], record.hex()])
    text = ["# Auditoria dos danos do Ryo — ROM com patches ativos", "",
            "Gerado por `python tools/damage_audit.py`. Fonte: `rom/aof2r.zip`.",
            f"SHA-256 da P-ROM em ordem 68k: `{hashlib.sha256(rom).hexdigest()}`.", "",
            "**Valores base dos registros, antes das escalas do motor. Nao sao HP medidos.**",
            "As duas colunas de cada par sao mostradas se diferentes.",
            "Extras da tabela nao provam o total de hits: hooks, caixas e animacoes tambem contam.", "",
            "| Grupo | Golpe | ID | Base acerto | Base defesa | Extras (tabela) |",
            "|---|---|---|---:|---:|---:|"]
    pair = lambda a, b: str(a) if a == b else f"{a}/{b}"
    for kind, name, mid, addr, record in rows:
        text.append(f"| {kind} | {name} | {mid} | {pair(*record[:2])} | {pair(*record[2:4])} | {record[7]} |")
    text += ["", "## Patches considerados", ""]
    text += [f"- `{key}`" for key in manifest_ids()]
    target = ROOT / "src/backend/specs/characters/ryo/damage-audit.md"
    target.write_text("\n".join(text) + "\n", encoding="utf-8")
    print(f"OK: {len(rows)} registros auditados; CSV e tabela de referencia atualizados.")


if __name__ == "__main__":
    main()
