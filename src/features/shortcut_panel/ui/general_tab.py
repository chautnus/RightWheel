"""General Settings Tab — startup and language configuration."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import TYPE_CHECKING

from ..services import startup_service
from . import theme
from features.i18n import available, current, set_locale, t, ui_font

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic

_BG = theme.BG_CONTENT
_CARD_BG = theme.BG_CARD
_BORDER = theme.BORDER_SUBTLE
_FG = theme.FG_PRIMARY


class GeneralTab(tk.Frame):
    """Modern card-based settings for General system options."""

    def __init__(self, parent: tk.Widget, logic: PanelLogic) -> None:
        super().__init__(parent, bg=_BG)
        self._logic = logic
        self._startup_var = tk.BooleanVar(value=startup_service.is_enabled())
        self._build()

    def _build(self) -> None:
        font = ui_font()

        # ── Card 1: System Startup ──────────────────────────────────────────
        c_sys = self._make_card(self, "⚙ " + t("settings.header"))
        cb_start = tk.Checkbutton(
            c_sys, text=t("settings.run_on_startup"),
            variable=self._startup_var, command=self._on_startup_toggle,
            bg=_CARD_BG, fg=_FG, selectcolor=_BG, activebackground=_CARD_BG,
            activeforeground=_FG, font=(font, 10), cursor="hand2"
        )
        cb_start.pack(anchor="w", padx=14, pady=(0, 12))

        # ── Card 2: Language ────────────────────────────────────────────────
        c_lang = self._make_card(self, "🌐 " + t("settings.language"))
        l_row = tk.Frame(c_lang, bg=_CARD_BG)
        l_row.pack(anchor="w", padx=14, pady=(0, 12))

        langs = available()
        codes = [c for c, _ in langs]
        names = [n for _, n in langs]
        cur_name = dict(langs).get(current(), "English")
        lang_var = tk.StringVar(value=cur_name)

        cb = ttk.Combobox(
            l_row, textvariable=lang_var, values=names,
            state="readonly", width=14, font=(font, 10)
        )
        cb.pack(side="left")

        restart_lbl = tk.Label(l_row, text="", bg=_CARD_BG, fg="#f0a030", font=(font, 9))
        restart_lbl.pack(side="left", padx=(10, 0))

        def _on_lang_change(event=None):
            name = lang_var.get()
            code = codes[names.index(name)]
            if code != current():
                set_locale(code)
                restart_lbl.config(text=t("settings.restart_required"))

        cb.bind("<<ComboboxSelected>>", _on_lang_change)

    def _make_card(self, parent: tk.Widget, title: str) -> tk.Frame:
        """Create a card container with 1px border and title."""
        font = ui_font()
        wrap = tk.Frame(parent, bg=_BORDER, padx=1, pady=1)
        wrap.pack(fill="x", padx=16, pady=8)
        inner = tk.Frame(wrap, bg=_CARD_BG)
        inner.pack(fill="x")
        tk.Label(
            inner, text=title, bg=_CARD_BG, fg=_FG,
            font=(font, 11, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 6))
        return inner

    def _on_startup_toggle(self) -> None:
        (startup_service.enable if self._startup_var.get() else startup_service.disable)()
