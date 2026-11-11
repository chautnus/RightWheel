"""Dialog for selecting an action type (open_settings, toggle_pause)."""
from __future__ import annotations

import tkinter as tk
from features.i18n import t, ui_font

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_RED = "#c0392b"


class ActionPickerDialog(tk.Toplevel):
    """Modal dialog for picking an action."""

    ACTIONS: list[tuple[str, str]] = [
        ("open_settings", "action.open_settings"),
        ("toggle_pause", "action.toggle_pause"),
    ]

    def __init__(self, parent: tk.Widget, init: str = "") -> None:
        super().__init__(parent)
        self.title(t("dlg.select_action"))
        self.resizable(False, False)
        self.configure(bg=_BG)
        self.grab_set()
        self.attributes("-topmost", True)
        self._result: str | None = None

        font = ui_font()
        tk.Label(self, text=t("dlg.select_action"), bg=_BG, fg=_FG,
                 font=(font, 11, "bold")).pack(padx=24, pady=(16, 10))

        for act_id, i18n_key in self.ACTIONS:
            label = t(i18n_key)
            is_active = (act_id == init)
            bg_col = _ACC if is_active else _BG2
            btn = tk.Button(
                self, text=label, command=lambda a=act_id: self._select(a),
                bg=bg_col, fg="#ffffff", font=(font, 10),
                relief="flat", padx=16, pady=8, cursor="hand2",
                activebackground=_ACC, activeforeground="#ffffff",
                anchor="w", width=26
            )
            btn.pack(padx=24, pady=4, fill="x")

        cancel_btn = tk.Button(
            self, text=t("btn.cancel"), command=self._cancel,
            bg=_RED, fg="white", font=(font, 9), relief="flat",
            padx=10, pady=4, cursor="hand2", activebackground=_RED
        )
        cancel_btn.pack(pady=(12, 14))

        self.bind("<Escape>", lambda _: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _select(self, action: str) -> None:
        self._result = action
        self.destroy()

    def _cancel(self) -> None:
        self.destroy()

    @classmethod
    def ask(cls, parent: tk.Widget, init: str = "") -> str | None:
        dlg = cls(parent, init)
        parent.wait_window(dlg)
        return dlg._result
