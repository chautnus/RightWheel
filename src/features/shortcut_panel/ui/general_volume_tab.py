"""General & Volume Settings Tab — startup, language, volume step size, and panel widget toggle."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import TYPE_CHECKING

from ..services import config_service, startup_service
from features.i18n import available, current, set_locale, t, ui_font

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic

_BG = "#18181b"
_CARD_BG = "#1e1e24"
_BORDER = "#27272a"
_FG = "#ffffff"
_FG_MUTED = "#a1a1aa"
_ACC = "#0078d4"


class GeneralVolumeTab(tk.Frame):
    """Modern card-based settings for General system options and Volume control."""

    def __init__(self, parent: tk.Widget, logic: PanelLogic) -> None:
        super().__init__(parent, bg=_BG)
        self._logic = logic
        self._startup_var = tk.BooleanVar(value=startup_service.is_enabled())
        self._panel_vol_var = tk.BooleanVar(value=config_service.get_show_panel_volume())
        self._step_var = tk.StringVar(value=f"{int(config_service.get_volume_step() * 100)}%")
        self._build()

    def _build(self) -> None:
        font = ui_font()

        # ── Card 1: Volume Control ──────────────────────────────────────────
        c_vol = self._make_card(self, "🔊 " + t("action.show_volume_slider"))
        tk.Label(
            c_vol,
            text=t("settings.volume_desc") if "settings.volume_desc" in t("settings.title") else "Adjust volume via mouse scroll on Shortcut Panel and Capsule HUD.",
            bg=_CARD_BG, fg=_FG_MUTED, font=(font, 9), wraplength=480, justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # Show on panel toggle
        cb_panel = tk.Checkbutton(
            c_vol, text="Show Volume Bar on Shortcut Panel",
            variable=self._panel_vol_var, command=self._on_panel_vol_toggle,
            bg=_CARD_BG, fg=_FG, selectcolor=_BG, activebackground=_CARD_BG,
            activeforeground=_FG, font=(font, 10), cursor="hand2"
        )
        cb_panel.pack(anchor="w", padx=14, pady=2)

        # Step size selector
        row_step = tk.Frame(c_vol, bg=_CARD_BG)
        row_step.pack(anchor="w", padx=14, pady=(8, 12))
        tk.Label(
            row_step, text="Volume step per scroll: ",
            bg=_CARD_BG, fg=_FG, font=(font, 10)
        ).pack(side="left")

        for step_val in ("2%", "5%", "10%"):
            rb = tk.Radiobutton(
                row_step, text=step_val, value=step_val,
                variable=self._step_var, command=self._on_step_change,
                bg=_CARD_BG, fg=_FG, selectcolor=_BG, activebackground=_CARD_BG,
                activeforeground=_FG, font=(font, 9), cursor="hand2"
            )
            rb.pack(side="left", padx=6)

        # ── Card 2: System Startup ──────────────────────────────────────────
        c_sys = self._make_card(self, "⚙ " + t("settings.header"))
        cb_start = tk.Checkbutton(
            c_sys, text=t("settings.run_on_startup"),
            variable=self._startup_var, command=self._on_startup_toggle,
            bg=_CARD_BG, fg=_FG, selectcolor=_BG, activebackground=_CARD_BG,
            activeforeground=_FG, font=(font, 10), cursor="hand2"
        )
        cb_start.pack(anchor="w", padx=14, pady=(0, 12))

        # ── Card 3: Language ────────────────────────────────────────────────
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

    def _on_panel_vol_toggle(self) -> None:
        d = config_service.load()
        d["show_panel_volume"] = self._panel_vol_var.get()
        config_service.save(d)

    def _on_step_change(self) -> None:
        val_str = self._step_var.get().replace("%", "")
        try:
            val = float(val_str) / 100.0
        except ValueError:
            val = 0.05
        d = config_service.load()
        d["volume_step"] = val
        config_service.save(d)
