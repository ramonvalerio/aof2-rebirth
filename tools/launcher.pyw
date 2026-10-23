"""AOF2 Rebirth Launcher: escolhe patches, gera a ROM e abre no FBNeo.

Uso: duplo clique (pythonw) ou `python tools/launcher.pyw`.
"""
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_rom import OUT_ZIP, ROOT, BuildError, build, load_patch, manifest_ids  # noqa: E402

FBNEO_DIR = ROOT / "emulator" / "emulator" / "fbneo"
FBNEO_EXE = FBNEO_DIR / "fcadefbneo.exe"
BIOS_ZIP = ROOT / "bios" / "neogeo.zip"
FBNEO_INI = FBNEO_DIR / "config" / "fcadefbneo.ini"
# O Fightcade FBNeo só aceita o nome do driver na linha de comando (não um
# caminho), e procura cada arquivo da ROM em TODOS os rompaths, preferindo o
# de CRC original. Por isso, enquanto o emulador está aberto, a pasta do hack
# vira o único rompath; o aof2.zip original do emulador não é tocado.
RUN_DIR = ROOT / "build" / "run"
ROMPATHS_BACKUP = ROOT / "build" / "fbneo-rompaths.bak"
ROMPATH_PREFIX = b"szAppRomPaths["


def _rompath_lines():
    lines = FBNEO_INI.read_bytes().split(b"\r\n")
    idx = [i for i, line in enumerate(lines) if line.startswith(ROMPATH_PREFIX)]
    if not idx:
        raise OSError(f"szAppRomPaths não encontrado em {FBNEO_INI}")
    return lines, idx


def isolate_rompaths(path):
    """Deixa só `path` como rompath, guardando os originais em backup."""
    lines, idx = _rompath_lines()
    if not ROMPATHS_BACKUP.exists():
        ROMPATHS_BACKUP.write_bytes(b"\r\n".join(lines[i] for i in idx))
    for n, i in enumerate(idx):
        key = lines[i].split(b"]", 1)[0] + b"] "
        lines[i] = key + (path.encode() if n == 0 else b"")
    FBNEO_INI.write_bytes(b"\r\n".join(lines))


def restore_rompaths():
    """Recoloca os rompaths do backup (se houver) no ini do FBNeo."""
    if not ROMPATHS_BACKUP.exists():
        return
    saved = ROMPATHS_BACKUP.read_bytes().split(b"\r\n")
    lines, idx = _rompath_lines()
    for i, line in zip(idx, saved):
        lines[i] = line
    FBNEO_INI.write_bytes(b"\r\n".join(lines))
    ROMPATHS_BACKUP.unlink()


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AOF2 Rebirth")
        self.minsize(460, 320)

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Patches", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.vars = {}
        box = ttk.Frame(frm)
        box.pack(fill="x", pady=(4, 10))
        for pid in manifest_ids():
            p = load_patch(pid)
            var = tk.BooleanVar(value=True)
            self.vars[pid] = var
            ttk.Checkbutton(box, text=p.title, variable=var).pack(anchor="w")

        btns = ttk.Frame(frm)
        btns.pack(fill="x")
        self.btn_build = ttk.Button(btns, text="Criar ROM", command=self.on_build)
        self.btn_build.pack(side="left")
        self.btn_start = ttk.Button(btns, text="Start", command=self.on_start)
        self.btn_start.pack(side="left", padx=8)

        self.log = tk.Text(frm, height=8, state="disabled", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, pady=(10, 0))

    def write(self, msg):
        def append():
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.after(0, append)

    def selected(self):
        return [pid for pid, v in self.vars.items() if v.get()]

    def set_busy(self, busy):
        state = "disabled" if busy else "normal"
        self.btn_build.configure(state=state)
        self.btn_start.configure(state=state)

    def run_async(self, job):
        self.set_busy(True)

        def worker():
            try:
                job()
            except (BuildError, OSError) as e:
                self.write(f"ERRO: {e}")
                self.after(0, lambda: messagebox.showerror("AOF2 Rebirth", str(e)))
            finally:
                self.after(0, lambda: self.set_busy(False))
        threading.Thread(target=worker, daemon=True).start()

    def do_build(self):
        ids = self.selected()
        self.write(f"Criando ROM com {len(ids)} patch(es)...")
        build(ids, log=self.write)

    def on_build(self):
        self.run_async(self.do_build)

    def on_start(self):
        def job():
            self.do_build()
            RUN_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(OUT_ZIP, RUN_DIR / "aof2.zip")
            shutil.copyfile(BIOS_ZIP, RUN_DIR / "neogeo.zip")
            isolate_rompaths(str(RUN_DIR) + "\\")
            try:
                self.write("Iniciando FBNeo...")
                subprocess.run([str(FBNEO_EXE), "aof2"], cwd=FBNEO_DIR)
            finally:
                # O FBNeo regrava o ini ao sair, então restaura só depois.
                restore_rompaths()
                self.write("FBNeo fechado; rompaths originais restaurados.")
        self.run_async(job)


if __name__ == "__main__":
    # Se uma sessão anterior foi interrompida, devolve os rompaths originais.
    restore_rompaths()
    Launcher().mainloop()
