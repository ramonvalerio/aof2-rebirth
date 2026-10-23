"""Gera rom/aof2r.zip a partir de rom/aof2.zip + patches/manifest.json.

Uso:  python tools/build_rom.py [--list]

Regras (SPEC-001):
  - a ROM original nunca é alterada; a saída é recriada do zero a cada build;
  - patches são aplicados na ordem do manifest: primeiro os globais
    (patches/global/<id>), depois os de personagem
    (patches/characters/<personagem>/<id>);
  - cada hook confere os bytes originais antes de gravar;
  - dois patches não podem tocar o mesmo byte (conflito = erro);
  - blocos novos são alocados sequencialmente na região livre FREE_START..FREE_END.
"""
import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from asm68k import assemble  # noqa: E402

SRC_ZIP = ROOT / "rom" / "aof2.zip"
OUT_ZIP = ROOT / "rom" / "aof2r.zip"
MANIFEST = ROOT / "patches" / "manifest.json"
P1_NAME = "056-p1.p1"
P1_SHA1 = "ee42f3ca4516226b0088d0303ed28e3ecdabcd71"

# Região zerada no fim da P-ROM original (0xFDDA0..0xFFF00), com margem.
FREE_START = 0xFE000
FREE_END = 0xFFE00

ZIP_DATE = (1996, 12, 24, 23, 32, 0)  # build determinístico


def swap16(data):
    """P1 do Neo Geo é armazenado com bytes trocados (word-swap)."""
    b = bytearray(data)
    b[0::2], b[1::2] = b[1::2], b[0::2]
    return b


def load_patch(key):
    """Carrega patches/<key>/patch.py; key = "global/<id>" ou "characters/<personagem>/<id>"."""
    path = ROOT / "patches" / key / "patch.py"
    name = "patch_" + key.replace("/", "__").replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    leaf = key.rsplit("/", 1)[-1]
    if mod.PATCH.id != leaf:
        raise ValueError(f"{path}: PATCH.id '{mod.PATCH.id}' difere da pasta '{leaf}'")
    return mod.PATCH


class BuildError(Exception):
    pass


def manifest_ids():
    """Chaves dos patches na ordem de aplicação: globais e depois personagens."""
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    keys = [f"global/{pid}" for pid in m.get("global", [])]
    for char, ids in m.get("characters", {}).items():
        keys += [f"characters/{char}/{pid}" for pid in ids]
    return keys


def scope_of(key):
    """("global", None) ou ("character", <personagem>)."""
    parts = key.split("/")
    return ("global", None) if parts[0] == "global" else ("character", parts[1])


def build(patch_ids, out_zip=OUT_ZIP, log=print):
    """Aplica `patch_ids` (na ordem do manifest) e grava `out_zip`."""
    order = manifest_ids()
    unknown = set(patch_ids) - set(order)
    if unknown:
        raise BuildError(f"patches fora do manifest: {sorted(unknown)}")
    keys = [k for k in order if k in patch_ids]
    patches = [load_patch(k) for k in keys]

    with zipfile.ZipFile(SRC_ZIP) as z:
        files = {i.filename: z.read(i) for i in z.infolist()}
    if hashlib.sha1(files[P1_NAME]).hexdigest() != P1_SHA1:
        raise BuildError(f"{P1_NAME} não é o dump esperado do aof2 (sha1 diferente)")

    rom = swap16(files[P1_NAME])
    owner = {}  # endereço -> patch que gravou

    def write(addr, data, who):
        for a in range(addr, addr + len(data)):
            if a in owner:
                raise BuildError(f"conflito em ${a:06x}: {who} x {owner[a]}")
            owner[a] = who
        rom[addr:addr + len(data)] = data

    cursor = FREE_START
    for p in patches:
        addrs = {}
        for name, size in p.block_sizes().items():
            addrs[name] = cursor
            cursor = (cursor + size + 15) & ~15
        if cursor > FREE_END:
            raise BuildError(f"{p.id}: espaço livre esgotado")

        for b in p.blocks:
            org = addrs[b.name]
            code = assemble(b.program, org)
            if any(rom[org:org + len(code)]):
                raise BuildError(f"{p.id}: região ${org:x} não está livre")
            write(org, code, p.id)
            log(f"  {p.id}: bloco {b.name} @ ${org:06x}")

        for h in p.hooks:
            expect = bytes.fromhex(h.expect)
            if bytes(rom[h.addr:h.addr + len(expect)]) != expect:
                raise BuildError(f"{p.id}: bytes originais em ${h.addr:06x} não conferem")
            write(h.addr, h.build(addrs), p.id)
            log(f"  {p.id}: hook @ ${h.addr:06x}")

        for e in p.data:
            expect, new = bytes.fromhex(e.expect), bytes.fromhex(e.new)
            if len(expect) != len(new):
                raise BuildError(f"{p.id}: dado em ${e.addr:06x} muda de tamanho")
            if bytes(rom[e.addr:e.addr + len(expect)]) != expect:
                raise BuildError(f"{p.id}: bytes originais em ${e.addr:06x} não conferem")
            write(e.addr, new, p.id)
        if p.data:
            log(f"  {p.id}: {len(p.data)} alteração(ões) de dados")

    files[P1_NAME] = bytes(swap16(rom))
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):
            z.writestr(zipfile.ZipInfo(name, ZIP_DATE), files[name], zipfile.ZIP_DEFLATED)
    log(f"OK -> {out_zip} ({len(patches)} patch(es))")
    return out_zip


def main():
    ids = manifest_ids()
    if "--list" in sys.argv:
        for k in ids:
            p = load_patch(k)
            scope, char = scope_of(k)
            print(f"[{char or scope}] {p.id:36} {p.title}")
        return
    try:
        build(ids)
    except BuildError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
