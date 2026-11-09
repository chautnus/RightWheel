"""Settings window — modern two-column sidebar layout hosting settings tabs."""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from ..services import config_service
from .ask_dialog import _AskDialog, _btn  # re-export for backward-compat
from features.i18n import t, ui_font

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic

VERSION = "2.10.8"

_BG_SIDEBAR = "#121214"
_BG_CONTENT = "#18181b"
_BG_NAV_ACT = "#27272a"
_FG         = "#a1a1aa"
_FG_ACT     = "#ffffff"
_ACC        = "#0078d4"
_BORDER     = "#27272a"
_SAV        = "#16825d"


class SettingsWindow:
    def __init__(self, root: tk.Tk, logic: PanelLogic) -> None:
        self._root   = root
        self._logic  = logic
        self._win:   tk.Toplevel | None = None
        self._active_tab = "general"
        self._nav_btns: dict[str, tk.Button] = {}
        self._frames: dict[str, tk.Frame] = {}

    def show(self) -> None:
        if self._win and self._win.winfo_exists():
            self._win.deiconify()
            self._win.lift()
            return
        self._win = tk.Toplevel(self._root)
        self._win.title(t("settings.title", v=VERSION))
        self._win.geometry("760x600")
        self._win.configure(bg=_BG_CONTENT)
        self._win.resizable(False, False)
        self._win.protocol("WM_DELETE_WINDOW", self._save)
        self._build()

    def _save(self) -> None:
        if self._win and self._win.winfo_exists():
            self._win.withdraw()

    def _build(self) -> None:
        w = self._win
        font = ui_font()

        # ── Sidebar (Left) ────────────────────────────────────────────────
        sb = tk.Frame(w, bg=_BG_SIDEBAR, width=190)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # App branding header
        hdr = tk.Frame(sb, bg=_BG_SIDEBAR)
        hdr.pack(fill="x", padx=16, pady=(18, 16))
        tk.Label(
            hdr, text="RightWheel", bg=_BG_SIDEBAR, fg="#ffffff",
            font=(font, 13, "bold")
        ).pack(anchor="w")
        tk.Label(
            hdr, text=f"v{VERSION} • Minimalist", bg=_BG_SIDEBAR, fg="#71717a",
            font=(font, 9)
        ).pack(anchor="w", pady=(2, 0))

        tk.Frame(sb, bg=_BORDER, height=1).pack(fill="x", padx=12, pady=(0, 10))

        # Navigation items
        nav_items = [
            ("general",   "⚙  General & Volume"),
            ("default",   "⌨  " + t("settings.tab.default")),
            ("profiles",  "◈  " + t("settings.tab.profiles")),
            ("gestures",  "🖱  " + t("tray.gestures")),
            ("reference", "📖  Reference"),
            ("license",   "🔑  " + t("settings.tab.license")),
        ]

        self._nav_btns.clear()
        for tab_id, label in nav_items:
            btn = tk.Button(
                sb, text=label, anchor="w", relief="flat", bd=0,
                padx=14, pady=8, font=(font, 10), cursor="hand2",
                command=lambda tid=tab_id: self._switch_tab(tid),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._nav_btns[tab_id] = btn

        # Bottom Save button in sidebar
        bot_sb = tk.Frame(sb, bg=_BG_SIDEBAR)
        bot_sb.pack(side="bottom", fill="x", padx=12, pady=16)
        _btn(bot_sb, "✓ " + t("settings.save_close"), self._save, bg=_SAV).pack(fill="x")

        # ── Content Area (Right) ──────────────────────────────────────────
        content_wrap = tk.Frame(w, bg=_BG_CONTENT)
        content_wrap.pack(side="right", fill="both", expand=True)

        self._build_tabs(content_wrap, font)
        self._switch_tab("general")

    def _switch_tab(self, tab_id: str) -> None:
        font = ui_font()
        self._active_tab = tab_id
        for tid, btn in self._nav_btns.items():
            if tid == tab_id:
                btn.configure(
                    bg=_BG_NAV_ACT, fg=_FG_ACT, font=(font, 10, "bold"),
                    activebackground=_BG_NAV_ACT, activeforeground=_FG_ACT
                )
            else:
                btn.configure(
                    bg=_BG_SIDEBAR, fg=_FG, font=(font, 10),
                    activebackground=_BG_NAV_ACT, activeforeground=_FG_ACT
                )

        for tid, frame in self._frames.items():
            if tid == tab_id:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    def _build_tabs(self, parent: tk.Frame, font: str) -> None:
        self._frames.clear()

        # 1. General & Volume tab
        from .general_volume_tab import GeneralVolumeTab
        f_gen = tk.Frame(parent, bg=_BG_CONTENT)
        GeneralVolumeTab(f_gen, self._logic).pack(fill="both", expand=True)
        self._frames["general"] = f_gen

        # 2. Default shortcuts tab
        from .default_tab import DefaultTab
        f_def = tk.Frame(parent, bg=_BG_CONTENT)
        DefaultTab(f_def, self._logic).pack(fill="both", expand=True, padx=8, pady=8)
        self._frames["default"] = f_def

        # 3. Profiles tab
        from .profile_editor import ProfileEditor
        f_prof = tk.Frame(parent, bg=_BG_CONTENT)
        ProfileEditor(f_prof).pack(fill="both", expand=True, padx=8, pady=8)
        self._frames["profiles"] = f_prof

        # 4. Gestures tab
        from .gestures_tab import GesturesTab
        f_gest = tk.Frame(parent, bg=_BG_CONTENT)
        GesturesTab(f_gest).pack(fill="both", expand=True, padx=8, pady=8)
        self._frames["gestures"] = f_gest

        # 5. Reference tab
        from .reference_tab import ReferenceTab
        f_ref = tk.Frame(parent, bg=_BG_CONTENT)
        ReferenceTab(f_ref).pack(fill="both", expand=True, padx=8, pady=8)
        self._frames["reference"] = f_ref

        # 6. License tab
        from features.licensing.ui.license_window import LicenseFrame
        f_lic = tk.Frame(parent, bg=_BG_CONTENT)
        LicenseFrame(f_lic).pack(fill="both", expand=True, padx=8, pady=8)
        self._frames["license"] = f_lic
