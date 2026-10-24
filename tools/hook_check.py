"""Verifica se algum código do jogo desvia para o MEIO de um hook (SPEC-001).

Um hook substitui N bytes da ROM original por "jmp bloco" + NOPs. Se um
desvio (bcc/bra/bsr/jmp/jsr) de fora do trecho apontar para um endereço
dentro dele (que não seja o início), o processador cai no meio do jmp e
executa lixo. Desvios que partem de dentro do próprio trecho (rotina
reescrita inteira) são ignorados.

Uso: python tools/hook_check.py   (varre a P-ROM original inteira; ~1 min)
"""
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import capstone  # noqa: E402

from build_rom import P1_NAME, SRC_ZIP, load_patch, manifest_ids, swap16  # noqa: E402


def main():
    with zipfile.ZipFile(SRC_ZIP) as z:
        rom = bytes(swap16(z.read(P1_NAME)))
    md = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_M68K_000)

    ranges = []
    for key in manifest_ids():
        for h in load_patch(key).hooks:
            ranges.append((h.addr, h.addr + len(bytes.fromhex(h.expect)), key))

    problems = []
    for a in range(0, len(rom), 2):
        ins = next(md.disasm(rom[a:a + 10], a), None)
        if not ins or not ins.mnemonic.startswith(("b", "jmp", "jsr", "db")):
            continue
        if ins.mnemonic.startswith(("btst", "bset", "bclr", "bchg")):
            continue
        m = re.search(r"\$([0-9a-f]+)", ins.op_str.split(",")[-1])
        if not m:
            continue
        target = int(m.group(1), 16)
        for lo, hi, key in ranges:
            if lo < target < hi and not lo <= a < hi:
                problems.append(f"{key}: ${a:06x} {ins.mnemonic} {ins.op_str} cai no meio de ${lo:06x}-${hi - 1:06x}")

    for p in problems:
        print(p)
    print("OK: nenhum desvio externo para o meio de um hook" if not problems else f"{len(problems)} problema(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
