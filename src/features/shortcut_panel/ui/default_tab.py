"""Default tab — shortcut/folder/app/url management with modern master-detail toolbar."""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from ..services import config_service
from .ask_dialog import _AskDialog, _btn
from .default_tab_crud import _DefaultTabCRUDMixin
from .key_recorder_dialog import KeyRecorderDialog
from . import theme
from features.i18n import t, ui_font

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic

_BG  = theme.BG_CONTENT
_BG2 = theme.BG_CARD
_FG  = theme.FG_SECONDARY
_ACC = theme.ACCENT_BLUE
_RED = theme.COLOR_DANGER
_GRN = theme.COLOR_SUCCESS
_BTN_NEUTRAL = theme.BORDER_INPUT


class DefaultTab(tk.Frame, _DefaultTabCRUDMixin):
    """Modern full-width shortcut list with top creation toolbar and bottom actions."""

    def __init__(self, parent: tk.Widget, logic: PanelLogic) -> None:
        super().__init__(parent, bg=_BG)
        self._logic = logic
        self._dialog_open = False
        self._build()
        self._refresh()

    # ── build ─────────────────────────────────────────────────────────────

    def _build(self) -> None:
        font = ui_font()

        # ── 1. Top Header & Add Toolbar ──────────────────────────────────────
        top_bar = tk.Frame(self, bg=_BG)
        top_bar.pack(fill="x", padx=4, pady=(0, 8))

        # Title + count label on the left
        left_hdr = tk.Frame(top_bar, bg=_BG)
        left_hdr.pack(side="left", anchor="w")
        tk.Label(
            left_hdr, text=t("settings.tab.default"),
            bg=_BG, fg=theme.FG_PRIMARY, font=(font, 11, "bold")
        ).pack(side="left")
        self._count_lbl = tk.Label(
            left_hdr, text="",
            bg=_BG, fg=theme.FG_MUTED, font=(font, 9)
        )
        self._count_lbl.pack(side="left", padx=(8, 0))

        # Action creation buttons on the right
        btn_box = tk.Frame(top_bar, bg=_BG)
        btn_box.pack(side="right", anchor="e")

        _btn(btn_box, t("btn.shortcut"), self._add_shortcut, bg=_ACC).pack(side="left", padx=2)
        _btn(btn_box, t("btn.app"), self._add_app, bg=_BTN_NEUTRAL).pack(side="left", padx=2)
        _btn(btn_box, t("btn.url"), self._add_url, bg=_BTN_NEUTRAL).pack(side="left", padx=2)
        _btn(btn_box, t("btn.folder"), self._add_folder, bg=_BTN_NEUTRAL).pack(side="left", padx=2)

        # More dropdown for Command and Sequence
        more_mb = tk.Menubutton(
            btn_box, text="+ More ▾", bg=_BTN_NEUTRAL, fg="white",
            font=(font, 9), relief="flat", padx=8, pady=4, cursor="hand2"
        )
        menu = tk.Menu(
            more_mb, tearoff=0, bg=theme.BG_CARD, fg=theme.FG_PRIMARY,
            activebackground=theme.BG_CARD_HOVER, activeforeground=theme.FG_PRIMARY
        )
        menu.add_command(label="▶ Command Script", command=self._add_command)
        menu.add_command(label="⛓ Step Sequence", command=self._add_sequence)
        more_mb.configure(menu=menu)
        more_mb.pack(side="left", padx=2)

        _btn(btn_box, "⬇ Import", self._import, bg=_GRN).pack(side="left", padx=2)

        # ── 2. Full-Width Central List Frame ─────────────────────────────────
        list_wrap = tk.Frame(self, bg=theme.BORDER_SUBTLE, padx=1, pady=1)
        list_wrap.pack(fill="both", expand=True, padx=4)

        lf = tk.Frame(list_wrap, bg=_BG2)
        lf.pack(fill="both", expand=True)

        self._lb = tk.Listbox(
            lf, bg=_BG2, fg=_FG, font=(font, 10),
            selectbackground=_ACC, selectforeground="#ffffff",
            relief="flat", bd=0, activestyle="none", highlightthickness=0
        )
        sb = tk.Scrollbar(lf, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._lb.pack(fill="both", expand=True, padx=4, pady=4)
        self._lb.bind("<Double-Button-1>", lambda _: self._edit())

        # ── 3. Bottom Row Action Bar ─────────────────────────────────────────
        bot_bar = tk.Frame(self, bg=_BG)
        bot_bar.pack(fill="x", padx=4, pady=(8, 0))

        tk.Label(
            bot_bar, text="Double-click to edit • Select to reorder",
            bg=_BG, fg=theme.FG_MUTED, font=(font, 9)
        ).pack(side="left")

        act_box = tk.Frame(bot_bar, bg=_BG)
        act_box.pack(side="right")

        _btn(act_box, "↑ " + t("btn.up"), lambda: self._move(-1), bg=_BTN_NEUTRAL).pack(side="left", padx=2)
        _btn(act_box, "↓ " + t("btn.down"), lambda: self._move(1), bg=_BTN_NEUTRAL).pack(side="left", padx=2)
        _btn(act_box, t("btn.edit"), self._edit, bg=_BTN_NEUTRAL).pack(side="left", padx=2)
        _btn(act_box, t("btn.delete"), self._delete, bg=_RED).pack(side="left", padx=2)

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
        items = config_service.load().get("default", [])
        self._count_lbl.configure(text=f"• {len(items)} items")

        for i, it in enumerate(items):
            itype = it.get("type", "shortcut")
            lbl = it.get("label", "Untitled")

            if itype == "folder":
                n = len(it.get("children", []))
                self._lb.insert("end", f" [Folder]   {lbl}  ({n} items)")
                self._lb.itemconfigure(i, foreground="#4ec9b0")
            elif itype == "app":
                path = it.get("path", "")
                self._lb.insert("end", f" [App]      {lbl}   →   {path}")
                self._lb.itemconfigure(i, foreground="#c586c0")
            elif itype == "url":
                url = it.get("url", "")
                self._lb.insert("end", f" [Web]      {lbl}   →   {url}")
                self._lb.itemconfigure(i, foreground="#4fc1ff")
            elif itype == "command":
                cmd = it.get("cmd", "")
                self._lb.insert("end", f" [Cmd]      {lbl}   →   {cmd}")
                self._lb.itemconfigure(i, foreground="#ce9178")
            elif itype == "sequence":
                n_steps = len(it.get("steps", []))
                self._lb.insert("end", f" [Seq]      {lbl}  ({n_steps} steps)")
                self._lb.itemconfigure(i, foreground="#d7ba7d")
            elif itype == "action":
                self._lb.insert("end", f" [Action]   {lbl}")
                self._lb.itemconfigure(i, foreground="#dcdcaa")
            else:
                keys = it.get("keys", "")
                self._lb.insert("end", f" [Keys]     {lbl}   →   {keys}")
                self._lb.itemconfigure(i, foreground=theme.FG_PRIMARY)
