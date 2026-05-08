"""Reusable dark-theme Ask dialog and button helper."""
from __future__ import annotations

import tkinter as tk
from features.i18n import t, ui_font

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_SAV = "#16825d"
_RED = "#c0392b"


def _btn(parent: tk.Widget, text: str, cmd, bg: str = _ACC) -> tk.Button:
    return tk.Button(parent, text=text, command=cmd, bg=bg, fg="white",
                     font=(ui_font(), 10), relief="flat",
                     padx=10, pady=4, cursor="hand2", activebackground=bg)


class _AskDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, title: str, prompt: str,
                 init: str = "", hint: str = "") -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=_BG)
        self.grab_set()
        self.attributes("-topmost", True)
        self._result: str | None = None

        tk.Label(self, text=prompt, bg=_BG, fg=_FG,
                 font=("Segoe UI", 11)).pack(padx=24, pady=(18, 6))

        self._var = tk.StringVar(value=init)
        entry = tk.Entry(self, textvariable=self._var,
                         bg=_BG2, fg="#ffffff", insertbackground="#ffffff",
                         font=("Segoe UI", 13), width=26, relief="flat", bd=6)
        entry.pack(padx=24, pady=4)
        entry.focus_set()
        entry.select_range(0, "end")
        entry.bind("<Return>", lambda _: self._ok())
        entry.bind("<Escape>", lambda _: self._cancel())

        if hint:
            tk.Label(self, text=hint, bg=_BG, fg="#555",
                     font=("Segoe UI", 9)).pack(pady=(2, 8))

        bf = tk.Frame(self, bg=_BG)
        bf.pack(pady=(4, 14))
        _btn(bf, t("btn.ok"),     self._ok,     bg=_SAV).pack(side="left", padx=6)
        _btn(bf, t("btn.cancel"), self._cancel, bg=_RED).pack(side="left", padx=6)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _ok(self) -> None:
        self._result = self._var.get().strip()
        self.destroy()

    def _cancel(self) -> None:
        self.destroy()

    @classmethod
    def ask(cls, parent: tk.Widget, title: str, prompt: str,
            init: str = "", hint: str = "") -> str | None:
        dlg = cls(parent, title, prompt, init, hint)
        parent.wait_window(dlg)
        return dlg._result if dlg._result else None
