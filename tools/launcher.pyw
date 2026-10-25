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

from build_rom import (  # noqa: E402
    OUT_ZIP, ROOT, BuildError, build, load_patch, manifest_ids, scope_of,
)

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
    """Categorias à esquerda (Globais + um item por personagem, com a contagem
    de marcados); patches da categoria escolhida à direita, com rolagem e
    busca. A janela não cresce com o número de patches."""

    def __init__(self):
        super().__init__()
        self.title("AOF2 Rebirth")
        self.geometry("820x560")
        self.minsize(640, 420)

        self.vars = {}     # chave do patch -> BooleanVar
        self.titles = {}   # chave do patch -> título sem o prefixo "Personagem: "
        self.groups = {}   # nome da categoria -> [chaves]
        for k in manifest_ids():
            scope, char = scope_of(k)
            group = "Globais" if scope == "global" else char.capitalize()
            self.groups.setdefault(group, []).append(k)
            title = load_patch(k).title
            prefix = group + ": "
            if title.startswith(prefix):
                title = title[len(prefix)].upper() + title[len(prefix) + 1:]
            self.titles[k] = title
            var = tk.BooleanVar(value=True)
            var.trace_add("write", lambda *_: self.refresh_counts())
            self.vars[k] = var

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(0, weight=1)

        # ---- categorias
        side = ttk.Frame(frm)
        side.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        ttk.Label(side, text="Categorias", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.cats = ttk.Treeview(side, show="tree", selectmode="browse", height=12)
        self.cats.column("#0", width=170)
        self.cats.pack(fill="y", expand=True, pady=(4, 0))
        for g in self.groups:
            self.cats.insert("", "end", iid=g)
        self.cats.bind("<<TreeviewSelect>>", lambda _: self.show_patches())

        # ---- patches da categoria
        main = ttk.Frame(frm)
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        bar = ttk.Frame(main)
        bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(bar, text="Buscar:").pack(side="left")
        self.query = tk.StringVar()
        self.query.trace_add("write", lambda *_: self.show_patches())
        ttk.Entry(bar, textvariable=self.query, width=28).pack(side="left", padx=(4, 10))
        ttk.Button(bar, text="Marcar todos", command=lambda: self.set_visible(True)).pack(side="left")
        ttk.Button(bar, text="Desmarcar todos", command=lambda: self.set_visible(False)).pack(side="left", padx=4)

        box = ttk.Frame(main, relief="sunken", borderwidth=1)
        box.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(box, highlightthickness=0)
        scroll = ttk.Scrollbar(box, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.list = ttk.Frame(self.canvas, padding=6)
        win = self.canvas.create_window((0, 0), window=self.list, anchor="nw")
        self.list.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(win, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-e.delta // 120, "units"))

        # ---- ações e log
        btns = ttk.Frame(frm)
        btns.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.btn_build = ttk.Button(btns, text="Criar ROM", command=self.on_build)
        self.btn_build.pack(side="left")
        self.btn_start = ttk.Button(btns, text="Start", command=self.on_start)
        self.btn_start.pack(side="left", padx=8)
        self.total = ttk.Label(btns, foreground="gray")
        self.total.pack(side="right")

        self.log = tk.Text(frm, height=7, state="disabled", font=("Consolas", 9))
        self.log.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.refresh_counts()
        self.cats.selection_set(next(iter(self.groups)))

    def current_keys(self):
        sel = self.cats.selection()
        q = self.query.get().strip().lower()
        if q:   # a busca vale para todas as categorias
            return [k for ks in self.groups.values() for k in ks
                    if q in self.titles[k].lower() or q in k.lower()]
        return self.groups[sel[0]] if sel else []

    def show_patches(self):
        for w in self.list.winfo_children():
            w.destroy()
        keys = self.current_keys()
        searching = bool(self.query.get().strip())
        for k in keys:
            text = self.titles[k]
            if searching:
                scope, char = scope_of(k)
                text = f"[{'Globais' if scope == 'global' else char.capitalize()}] {text}"
            ttk.Checkbutton(self.list, text=text, variable=self.vars[k]).pack(anchor="w", pady=1)
        if not keys:
            ttk.Label(self.list, text="(nenhum patch)", foreground="gray").pack(anchor="w")
        self.canvas.yview_moveto(0)

    def set_visible(self, value):
        for k in self.current_keys():
            self.vars[k].set(value)

    def refresh_counts(self):
        for g, ks in self.groups.items():
            on = sum(self.vars[k].get() for k in ks)
            self.cats.item(g, text=f"{g}  ({on}/{len(ks)})")
        on = sum(v.get() for v in self.vars.values())
        self.total.configure(text=f"{on} de {len(self.vars)} patches marcados")

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
