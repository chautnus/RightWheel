"""Default tab — shortcut/folder/app/url listbox with full CRUD."""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from ..services import config_service
from .ask_dialog import _AskDialog, _btn
from .default_tab_crud import _DefaultTabCRUDMixin
from .key_recorder_dialog import KeyRecorderDialog
from features.i18n import t, ui_font

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_RED = "#c0392b"
_GRN = "#16825d"


class DefaultTab(tk.Frame, _DefaultTabCRUDMixin):
    """Listbox + CRUD buttons for the Default shortcuts list."""

    def __init__(self, parent: tk.Widget, logic: PanelLogic) -> None:
        super().__init__(parent, bg=_BG)
        self._logic = logic
        self._dialog_open = False
        self._build()
        self._refresh()

    # ── build ─────────────────────────────────────────────────────────────

    def _build(self) -> None:
        lf = tk.Frame(self, bg=_BG2)
        lf.pack(side="left", fill="both", expand=True)

        self._lb = tk.Listbox(lf, bg=_BG2, fg=_FG, font=(ui_font(), 11),
                              selectbackground=_ACC, relief="flat", bd=0,
                              activestyle="none")
        sb = tk.Scrollbar(lf, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._lb.pack(fill="both", expand=True, padx=4, pady=4)
        self._lb.bind("<Double-Button-1>", lambda _: self._edit())

        bf = tk.Frame(self, bg=_BG)
        bf.pack(side="right", padx=(8, 0), anchor="n", pady=4)
        for txt, cmd, c in [
            (t("btn.shortcut"), self._add_shortcut,    _ACC),
            (t("btn.app"),      self._add_app,          _ACC),
            (t("btn.url"),      self._add_url,          _ACC),
            (t("btn.folder"),   self._add_folder,       _ACC),
            ("▶ Command",       self._add_command,      "#6a5acd"),
            (t("btn.edit"),     self._edit,             "#404040"),
            (t("btn.delete"),   self._delete,           _RED),
            (t("btn.up"),       lambda: self._move(-1), "#404040"),
            (t("btn.down"),     lambda: self._move(1),  "#404040"),
            ("⬇ Import",        self._import,           _GRN),
        ]:
            _btn(bf, txt, cmd, c).pack(fill="x", pady=2)

    # ── helpers ───────────────────────────────────────────────────────────

    def _ask(self, *a, **kw) -> str | None:
        return _AskDialog.ask(self.winfo_toplevel(), *a, **kw)

    def _record_keys(self, init: str = "") -> str | None:
        return KeyRecorderDialog.ask(self.winfo_toplevel(), init)

    def _sel(self) -> int | None:
        s = self._lb.curselection()
        return s[0] if s else None

    def refresh(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        self._lb.delete(0, "end")
        for i, it in enumerate(config_service.load().get("default", [])):
            t = it.get("type", "shortcut")
            if t == "folder":
                n = len(it.get("children", []))
                self._lb.insert("end", f"  {it['label']}  ({n} items)")
                self._lb.itemconfigure(i, foreground="#4ec9b0")
            elif t == "app":
                self._lb.insert("end", f"  🚀  {it['label']}   →   {it.get('path','')}")
                self._lb.itemconfigure(i, foreground="#c586c0")
            elif t == "url":
                self._lb.insert("end", f"  🌐  {it['label']}   →   {it.get('url','')}")
                self._lb.itemconfigure(i, foreground="#4fc1ff")
            elif t == "command":
                self._lb.insert("end", f"  ▶  {it['label']}   →   {it.get('cmd','')}")
                self._lb.itemconfigure(i, foreground="#ce9178")
            elif t == "action":
                self._lb.insert("end", f"  ⚡  {it['label']}")
                self._lb.itemconfigure(i, foreground="#dcdcaa")
            else:
                self._lb.insert("end",
                    f"  ⌨  {it['label']}   →   {it.get('keys', '')}")
