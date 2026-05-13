"""Settings window — orchestrates Default tab, Profiles tab, License tab, footer."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import TYPE_CHECKING

from ..services import config_service, startup_service
from .ask_dialog import _AskDialog, _btn  # re-export for backward-compat
from features.i18n import t, available, set_locale, current, ui_font

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic

VERSION = "2.10.2"

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_SAV = "#16825d"


class SettingsWindow:
    def __init__(self, root: tk.Tk, logic: PanelLogic) -> None:
        self._root  = root
        self._logic = logic
        self._win:  tk.Toplevel | None = None
        self._startup_var: tk.BooleanVar | None = None

    # ── lifecycle ─────────────────────────────────────────────────────────

    def show(self) -> None:
        if self._win and self._win.winfo_exists():
            self._win.deiconify()
            self._win.lift()
            return
        self._win = tk.Toplevel(self._root)
        self._win.title(t("settings.title", v=VERSION))
        self._win.geometry("720x600")
        self._win.configure(bg=_BG)
        self._win.resizable(False, False)
        self._win.protocol("WM_DELETE_WINDOW", self._save)
        self._build()

    def _save(self) -> None:
        if self._startup_var is not None:
            (startup_service.enable
             if self._startup_var.get()
             else startup_service.disable)()
        if self._win and self._win.winfo_exists():
            self._win.withdraw()

    # ── layout ────────────────────────────────────────────────────────────

    def _build(self) -> None:
        w    = self._win
        font = ui_font()

        # Header
        hdr = tk.Frame(w, bg=_BG)
        hdr.pack(fill="x", padx=16, pady=(14, 2))
        tk.Label(hdr, text=t("settings.header"), bg=_BG, fg="#fff",
                 font=(font, 14, "bold")).pack(side="left")
        tk.Label(hdr, text=f"v{VERSION}", bg=_BG, fg="#555",
                 font=(font, 10)).pack(side="right", pady=4)

        # Notebook — "clam" theme so dark colors aren't overridden by Windows
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",     background=_BG,  borderwidth=0, tabmargins=0)
        style.configure("TNotebook.Tab", background=_BG2, foreground=_FG,
                        padding=[14, 6], font=(font, 10))
        style.map("TNotebook.Tab",
                  background=[("selected", _ACC), ("active", "#3a3a3a")],
                  foreground=[("selected", "#fff"), ("active", "#fff")])

        nb = ttk.Notebook(w)
        nb.pack(fill="both", expand=True, padx=16, pady=8)

        self._build_default_tab(nb, font)
        self._build_profiles_tab(nb, font)
        self._build_license_tab(nb, font)

        # Footer
        bot = tk.Frame(w, bg=_BG)
        bot.pack(fill="x", padx=16, pady=10)

        self._startup_var = tk.BooleanVar(value=startup_service.is_enabled())
        tk.Checkbutton(bot, text=t("settings.run_on_startup"),
                       variable=self._startup_var,
                       bg=_BG, fg=_FG, selectcolor=_BG2,
                       font=(font, 10)).pack(side="left")

        # Language selector
        self._build_lang_selector(bot, font)

        _btn(bot, t("settings.save_close"), self._save,
             bg=_SAV).pack(side="right")

    def _build_lang_selector(self, parent: tk.Frame, font: str) -> None:
        """Compact language dropdown in the footer."""
        frame = tk.Frame(parent, bg=_BG)
        frame.pack(side="left", padx=(20, 0))

        tk.Label(frame, text=t("settings.language"), bg=_BG, fg=_FG,
                 font=(font, 10)).pack(side="left")

        langs = available()
        codes  = [c for c, _ in langs]
        names  = [n for _, n in langs]

        var = tk.StringVar(value=dict(langs).get(current(), "English"))
        cb  = ttk.Combobox(frame, textvariable=var, values=names,
                           state="readonly", width=12,
                           font=(font, 10))
        cb.pack(side="left", padx=(4, 0))

        restart_lbl = tk.Label(frame, text="", bg=_BG, fg="#f0a030",
                               font=(font, 9))
        restart_lbl.pack(side="left", padx=(6, 0))

        def _on_change(event=None) -> None:
            name = var.get()
            code = codes[names.index(name)]
            if code != current():
                set_locale(code)
                restart_lbl.config(text=t("settings.restart_required"))

        cb.bind("<<ComboboxSelected>>", _on_change)

    def _build_default_tab(self, nb: ttk.Notebook, font: str) -> None:
        from .default_tab import DefaultTab
        frame = tk.Frame(nb, bg=_BG)
        nb.add(frame, text=t("settings.tab.default"))
        tab = DefaultTab(frame, self._logic)
        tab.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_profiles_tab(self, nb: ttk.Notebook, font: str) -> None:
        from .profile_editor import ProfileEditor
        frame = tk.Frame(nb, bg=_BG)
        nb.add(frame, text=t("settings.tab.profiles"))
        ProfileEditor(frame).pack(fill="both", expand=True)

    def _build_license_tab(self, nb: ttk.Notebook, font: str) -> None:
        from features.licensing.ui.license_window import LicenseFrame
        frame = tk.Frame(nb, bg=_BG)
        nb.add(frame, text=t("settings.tab.license"))
        LicenseFrame(frame).pack(fill="both", expand=True)
