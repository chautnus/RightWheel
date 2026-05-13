"""Import template dialog — file picker, mode selector, preview, confirm."""
from __future__ import annotations

import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb

from ..services import import_service
from features.i18n import ui_font

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_BG3 = "#3a3a3a"
_FG  = "#cccccc"
_DIM = "#888888"
_ACC = "#0078d4"
_GRN = "#16825d"
_RED = "#c0392b"


def _btn(parent: tk.Widget, text: str, cmd, bg: str) -> tk.Button:
    return tk.Button(parent, text=text, command=cmd, bg=bg, fg="white",
                     font=(ui_font(), 10), relief="flat", cursor="hand2",
                     padx=12, pady=6, bd=0, activebackground=bg,
                     activeforeground="white")


class ImportDialog(tk.Toplevel):
    """Modal dialog for importing shortcuts from a JSON template file."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.title("Import Shortcuts")
        self.configure(bg=_BG)
        self.resizable(False, False)
        self.grab_set()

        self._items: list[dict] = []
        self._mode  = tk.StringVar(value="append")
        self._path  = tk.StringVar()

        self._build()
        self._center(parent)

    # ── layout ────────────────────────────────────────────────────────────

    def _build(self) -> None:
        pad = {"padx": 16, "pady": 8}

        # File picker row
        ff = tk.Frame(self, bg=_BG)
        ff.pack(fill="x", **pad)
        tk.Label(ff, text="Template file (.json)", bg=_BG, fg=_FG,
                 font=(ui_font(), 10)).pack(anchor="w")
        row = tk.Frame(ff, bg=_BG)
        row.pack(fill="x", pady=(4, 0))
        self._path_entry = tk.Entry(row, textvariable=self._path, bg=_BG2,
                                    fg=_FG, relief="flat", font=(ui_font(), 9),
                                    state="readonly", readonlybackground=_BG2)
        self._path_entry.pack(side="left", fill="x", expand=True, ipady=5,
                              padx=(0, 6))
        _btn(row, "Browse…", self._browse, _BG3).pack(side="right")

        # Template info
        self._info = tk.Label(self, text="No file selected.", bg=_BG,
                              fg=_DIM, font=(ui_font(), 9), anchor="w")
        self._info.pack(fill="x", padx=16)

        # Mode selector
        mf = tk.Frame(self, bg=_BG)
        mf.pack(fill="x", **pad)
        tk.Label(mf, text="Import mode", bg=_BG, fg=_FG,
                 font=(ui_font(), 10)).pack(anchor="w", pady=(0, 4))
        for label, val in [("Append to existing shortcuts", "append"),
                            ("Replace all shortcuts",        "replace")]:
            tk.Radiobutton(mf, text=label, variable=self._mode, value=val,
                           bg=_BG, fg=_FG, selectcolor=_BG2,
                           activebackground=_BG, activeforeground=_FG,
                           font=(ui_font(), 10)).pack(anchor="w")

        # Preview
        pf = tk.Frame(self, bg=_BG)
        pf.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        tk.Label(pf, text="Preview", bg=_BG, fg=_FG,
                 font=(ui_font(), 10)).pack(anchor="w", pady=(0, 4))
        self._preview = tk.Listbox(pf, bg=_BG2, fg=_FG, height=8,
                                   font=(ui_font(), 9), relief="flat", bd=0,
                                   activestyle="none", selectbackground=_ACC)
        sb = tk.Scrollbar(pf, orient="vertical", command=self._preview.yview)
        self._preview.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._preview.pack(fill="both", expand=True)

        # Buttons
        bf = tk.Frame(self, bg=_BG)
        bf.pack(fill="x", padx=16, pady=(0, 16))
        _btn(bf, "Cancel", self.destroy, _BG3).pack(side="right", padx=(6, 0))
        self._import_btn = _btn(bf, "Import", self._do_import, _GRN)
        self._import_btn.pack(side="right")
        self._import_btn.configure(state="disabled")

    # ── logic ─────────────────────────────────────────────────────────────

    def _browse(self) -> None:
        path = fd.askopenfilename(
            parent=self,
            title="Select template file",
            filetypes=[("JSON template", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        self._path.set(path)
        self._load_preview(path)

    def _load_preview(self, path: str) -> None:
        name, desc, items, err = import_service.load_template(path)
        self._preview.delete(0, "end")
        if err:
            self._info.configure(text=f"⚠ {err}", fg=_RED)
            self._items = []
            self._import_btn.configure(state="disabled")
            return

        info = f'"{name}"'
        if desc:
            info += f" — {desc}"
        info += f"  ({len(items)} shortcuts)"
        self._info.configure(text=info, fg=_FG)
        self._items = items

        for it in items:
            itype = it.get("type", "shortcut")
            label = it.get("label", "")
            if itype == "folder":
                n = len(it.get("children", []))
                self._preview.insert("end", f"  📁 {label}  ({n} items)")
            elif itype == "app":
                self._preview.insert("end", f"  🚀 {label}")
            elif itype == "url":
                self._preview.insert("end", f"  🌐 {label}")
            else:
                self._preview.insert("end",
                    f"  ⌨ {label}  →  {it.get('keys','')}")

        self._import_btn.configure(
            state="normal",
            text=f"Import {len(items)} shortcuts",
        )

    def _do_import(self) -> None:
        if not self._items:
            return
        n = import_service.apply(self._items, self._mode.get())
        mb.showinfo("Import complete",
                    f"Successfully imported {n} shortcuts.",
                    parent=self)
        self.destroy()

    def _center(self, parent: tk.Widget) -> None:
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width()  // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w // 2}+{ph - h // 2}")

    # ── entry point ───────────────────────────────────────────────────────

    @classmethod
    def open(cls, parent: tk.Widget) -> None:
        cls(parent).wait_window()
