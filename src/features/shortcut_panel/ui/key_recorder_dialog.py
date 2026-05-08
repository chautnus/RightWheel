"""Key-recorder dialog — captures actual keypresses instead of typed text."""
from __future__ import annotations

import tkinter as tk
from features.i18n import t, ui_font

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_SAV = "#16825d"
_RED = "#c0392b"

# tkinter keysym → internal key name (must match VK map in shortcut_executor)
_SPECIAL: dict[str, str] = {
    "Left": "left", "Right": "right", "Up": "up", "Down": "down",
    "Return": "enter", "KP_Enter": "enter",
    "BackSpace": "backspace", "Delete": "del", "Insert": "ins",
    "Home": "home", "End": "end",
    "Prior": "pgup", "Next": "pgdn",
    "Tab": "tab", "space": "space",
    **{f"F{i}": f"f{i}" for i in range(1, 13)},
}

# keysyms that are pure modifiers (don't form the "main" key)
_MODS_SYMS = {
    "Control_L", "Control_R",
    "Shift_L",   "Shift_R",
    "Alt_L",     "Alt_R",
    "Super_L",   "Super_R",
    "Meta_L",    "Meta_R",
    "Caps_Lock", "Num_Lock",
}

_MOD_NAME: dict[str, str] = {
    "Control_L": "ctrl",  "Control_R": "ctrl",
    "Shift_L":   "shift", "Shift_R":   "shift",
    "Alt_L":     "alt",   "Alt_R":     "alt",
    "Super_L":   "win",   "Super_R":   "win",
    "Meta_L":    "win",   "Meta_R":    "win",
}

_MOD_ORDER = ["ctrl", "alt", "shift", "win"]


class KeyRecorderDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, init: str = "") -> None:
        super().__init__(parent)
        font = ui_font()
        self.title(t("recorder.title"))
        self.resizable(False, False)
        self.configure(bg=_BG)
        self.grab_set()
        self.attributes("-topmost", True)

        self._result: str | None = None
        self._held_mods: set[str] = set()
        self._combo = init

        tk.Label(self, text=t("recorder.prompt"), bg=_BG, fg=_FG,
                 font=(font, 11)).pack(padx=28, pady=(18, 8))

        self._preview = tk.Label(self, text=init or "—",
                                 bg=_BG2, fg="#ffffff",
                                 font=(font, 18, "bold"),
                                 width=22, pady=10)
        self._preview.pack(padx=28, pady=4)

        tk.Label(self, text=t("recorder.sub"),
                 bg=_BG, fg="#555", font=(font, 9)).pack(pady=(2, 8))

        bf = tk.Frame(self, bg=_BG)
        bf.pack(pady=(4, 16))
        tk.Button(bf, text=t("btn.ok"), command=self._ok,
                  bg=_SAV, fg="white", font=(font, 10),
                  relief="flat", padx=14, pady=4,
                  cursor="hand2", activebackground=_SAV).pack(side="left", padx=6)
        tk.Button(bf, text=t("btn.cancel"), command=self._cancel,
                  bg=_RED, fg="white", font=(font, 10),
                  relief="flat", padx=14, pady=4,
                  cursor="hand2", activebackground=_RED).pack(side="left", padx=6)

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<KeyPress>",   self._on_press)
        self.bind("<KeyRelease>", self._on_release)
        self.focus_force()

    # ── key capture ───────────────────────────────────────────────────────

    def _on_press(self, event: tk.Event) -> str:
        sym = event.keysym
        if sym in _MODS_SYMS:
            mod = _MOD_NAME.get(sym)
            if mod:
                self._held_mods.add(mod)
            return "break"

        key = _SPECIAL.get(sym) or (sym.lower() if len(sym) == 1 else sym.lower())
        mods = [m for m in _MOD_ORDER if m in self._held_mods]
        self._combo = "+".join(mods + [key])
        self._preview.config(text=self._combo)
        return "break"

    def _on_release(self, event: tk.Event) -> str:
        mod = _MOD_NAME.get(event.keysym)
        if mod:
            self._held_mods.discard(mod)
        return "break"

    # ── result ────────────────────────────────────────────────────────────

    def _ok(self) -> None:
        self._result = self._combo or None
        self.destroy()

    def _cancel(self) -> None:
        self.destroy()

    @classmethod
    def ask(cls, parent: tk.Widget, init: str = "") -> str | None:
        dlg = cls(parent, init)
        parent.wait_window(dlg)
        return dlg._result
