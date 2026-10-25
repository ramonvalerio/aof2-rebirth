"""Gera rom/aof2r.zip a partir de rom/aof2.zip + patches/manifest.json.

Uso:  python tools/build_rom.py [--list]

Regras (SPEC-001):
  - a ROM original nunca é alterada; a saída é recriada do zero a cada build;
  - patches são aplicados na ordem do manifest: primeiro os globais
    (patches/global/<id>), depois os de personagem
    (patches/characters/<personagem>/<id>);
  - cada hook confere os bytes originais antes de gravar;
  - dois patches não podem tocar o mesmo byte (conflito = erro), exceto
    hooks encadeados (Hook.chain), que o build liga em sequência;
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

from asm68k import JmpAbs, JmpNext, assemble, size_of  # noqa: E402
from patchlib import DataBlock, Hook  # noqa: E402

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

    def alloc(size, who):
        nonlocal cursor
        org = cursor
        cursor = (cursor + size + 15) & ~15
        if cursor > FREE_END:
            raise BuildError(f"{who}: espaço livre esgotado")
        return org

    # 1ª passagem: endereços dos blocos e cadeias de hooks compartilhados.
    addrs = {}  # id(patch) -> {bloco: endereço}; o id do patch pode repetir entre personagens
    for p in patches:
        addrs[id(p)] = {name: alloc(size, p.id) for name, size in p.block_sizes().items()}

    chains = {}  # endereço -> (hook de referência, [(patch, hook)])
    for p in patches:
        for h in p.hooks:
            if h.chain is None:
                continue
            if h.chain not in ("before", "after") or h.original is None:
                raise BuildError(f"{p.id}: hook ${h.addr:06x} encadeado sem chain/original válidos")
            ref, members = chains.setdefault(h.addr, (h, []))
            if (h.expect, h.chain, h.original) != (ref.expect, ref.chain, ref.original):
                raise BuildError(f"{p.id}: hook ${h.addr:06x} difere dos outros patches do mesmo endereço")
            members.append((p, h))

    next_of = {}   # (patch, endereço) -> destino do JmpNext
    entry = {}     # endereço -> destino do jmp gravado no jogo
    trampolines = []
    for addr, (ref, members) in chains.items():
        resume = addr + len(bytes.fromhex(ref.expect))
        heads = [addrs[id(p)][h.to_block] for p, h in members]
        tramp = alloc(size_of(ref.original) + 6, f"cadeia ${addr:06x}")
        if ref.chain == "before":
            targets, tail = heads[1:] + [tramp], resume
            entry[addr] = heads[0]
        else:
            targets, tail = heads[1:] + [resume], heads[0]
            entry[addr] = tramp
        for (p, _), t in zip(members, targets):
            next_of[(id(p), addr)] = t
        trampolines.append((addr, tramp, ref.original + [JmpAbs(tail)]))

    def resolve(program, p):
        out = []
        for item in program:
            if isinstance(item, JmpNext):
                if (id(p), item.hook) not in next_of:
                    raise BuildError(f"{p.id}: JmpNext(${item.hook:06x}) sem hook encadeado")
                item = JmpAbs(next_of[(id(p), item.hook)])
            out.append(item)
        return out

    # 2ª passagem: grava.
    for p in patches:
        for b in p.blocks:
            org = addrs[id(p)][b.name]
            code = b.build(org) if isinstance(b, DataBlock) else assemble(resolve(b.program, p), org)
            if len(code) != p.block_sizes()[b.name]:
                raise BuildError(f"{p.id}: bloco {b.name} com tamanho diferente do declarado")
            if any(rom[org:org + len(code)]):
                raise BuildError(f"{p.id}: região ${org:x} não está livre")
            write(org, code, p.id)
            log(f"  {p.id}: bloco {b.name} @ ${org:06x}")

        for h in p.hooks:
            if h.chain is not None and chains[h.addr][1][0][0] is not p:
                log(f"  {p.id}: hook @ ${h.addr:06x} (encadeado)")
                continue
            expect = bytes.fromhex(h.expect)
            if bytes(rom[h.addr:h.addr + len(expect)]) != expect:
                raise BuildError(f"{p.id}: bytes originais em ${h.addr:06x} não conferem")
            if h.chain is not None:
                code = Hook(h.addr, h.expect, [JmpAbs(entry[h.addr])]).build({})
                write(h.addr, code, f"cadeia ${h.addr:06x}")
            else:
                write(h.addr, h.build(addrs[id(p)]), p.id)
            log(f"  {p.id}: hook @ ${h.addr:06x}" + (" (encadeado)" if h.chain else ""))

        for e in p.data:
            new_hex = e.new(addrs[id(p)]) if callable(e.new) else e.new
            expect, new = bytes.fromhex(e.expect), bytes.fromhex(new_hex)
            if len(expect) != len(new):
                raise BuildError(f"{p.id}: dado em ${e.addr:06x} muda de tamanho")
            if bytes(rom[e.addr:e.addr + len(expect)]) != expect:
                raise BuildError(f"{p.id}: bytes originais em ${e.addr:06x} não conferem")
            write(e.addr, new, p.id)
        if p.data:
            log(f"  {p.id}: {len(p.data)} alteração(ões) de dados")

    for addr, org, program in trampolines:
        write(org, assemble(program, org), f"cadeia ${addr:06x}")
        log(f"  cadeia ${addr:06x}: original @ ${org:06x}")

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
