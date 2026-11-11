"""Floating shortcut panel — Raycast-style command palette, always-on-top window."""
from __future__ import annotations

import queue, threading, tkinter as tk
from typing import TYPE_CHECKING

from .panel_volume_widget import PanelVolumeWidget
from .panel_item_renderer import PanelItemRenderer

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic
    from .volume_overlay import VolumeOverlay

_W = 264
_BG = "#121214"
_BORDER = "#27272a"
_FONT_BC = ("Segoe UI", 9)
_FONT_FOOTER = ("Segoe UI", 8)


class PanelWindow:
    """Raycast-style floating command palette window for mouse shortcuts."""

    def __init__(self, logic: PanelLogic) -> None:
        self._logic = logic
        self._q: queue.Queue = queue.Queue()
        self._root: tk.Tk | None = None
        self._win: tk.Toplevel | None = None
        self._overlay: tk.Toplevel | None = None
        self._volume_overlay: VolumeOverlay | None = None
        self._volume_widget: PanelVolumeWidget | None = None
        self._item_renderer: PanelItemRenderer | None = None

        logic.on_show = lambda: self._q.put("show")
        logic.on_hide = lambda: self._q.put("hide")
        logic.on_update = lambda: self._q.put("update")
        logic.on_show_volume_slider = lambda: self._q.put("volume")

        threading.Thread(target=self._run, daemon=True).start()

    def open_settings(self) -> None:
        self._q.put("settings")

    def open_volume_slider(self) -> None:
        self._q.put("volume")

    # ── tkinter thread lifecycle ───────────────────────────────────────────

    def _run(self) -> None:
        self._root = tk.Tk()
        self._root.withdraw()
        from .welcome_window import show_welcome
        show_welcome(self._root)
        self._root.after(30, self._pump)
        self._root.mainloop()

    def _pump(self) -> None:
        try:
            while True:
                cmd = self._q.get_nowait()
                {
                    "show": self._do_show,
                    "hide": self._do_hide,
                    "update": self._do_update,
                    "settings": self._do_settings,
                    "volume": self._do_volume,
                }.get(cmd, lambda: None)()
        except queue.Empty:
            pass
        if self._root:
            self._root.after(30, self._pump)

    # ── window display & interactions ──────────────────────────────────────

    def _do_show(self) -> None:
        if self._overlay:
            self._overlay.destroy()
        if self._win:
            self._win.destroy()

        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()

        # Fullscreen transparent backdrop for outside-click dismiss
        self._overlay = tk.Toplevel(self._root)
        self._overlay.overrideredirect(True)
        self._overlay.attributes("-topmost", True)
        self._overlay.attributes("-alpha", 0.01)
        self._overlay.geometry(f"{sw}x{sh}+0+0")
        self._overlay.bind("<ButtonPress>", lambda _: self._logic.hide())

        # Main Command Palette Window
        self._win = tk.Toplevel(self._root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.configure(bg=_BG, highlightbackground=_BORDER, highlightthickness=1)

        self._win.bind("<Escape>", lambda _: self._logic.hide())
        self._win.bind("<BackSpace>", lambda _: self._logic.go_back())
        self._win.bind("<Return>", lambda _: self._logic.select_current())
        self._win.bind("<Up>", lambda _: self._logic.navigate(-1))
        self._win.bind("<Down>", lambda _: self._logic.navigate(1))
        self._win.bind("<MouseWheel>", lambda e: self._logic.navigate(-1 if e.delta > 0 else 1))
        for k in "0123456789":
            self._win.bind(k, lambda _, c=k: self._jump(int(c)))

        self._render()
        self._win.lift()
        self._win.focus_force()
        self._position()

    def _do_hide(self) -> None:
        if self._overlay:
            self._overlay.destroy()
            self._overlay = None
        if self._win:
            self._win.destroy()
            self._win = None

    def _do_update(self) -> None:
        if self._win:
            self._render()

    def _do_settings(self) -> None:
        from .settings_window import SettingsWindow
        SettingsWindow(self._root, self._logic).show()

    def _do_volume(self) -> None:
        if not self._volume_overlay:
            from .volume_overlay import VolumeOverlay
            self._volume_overlay = VolumeOverlay(self._root)
        self._volume_overlay.show()

    # ── rendering ──────────────────────────────────────────────────────────

    def _render(self) -> None:
        if not self._win:
            return
        for w in self._win.winfo_children():
            w.destroy()

        st = self._logic.state

        # Paused banner
        if self._logic.paused:
            tk.Label(self._win, text="⏸ MouseHook Paused", bg="#3a1a1a", fg="#f48771",
                     font=_FONT_BC, anchor="w", padx=10, pady=4).pack(fill="x")
            tk.Frame(self._win, bg="#6a2020", height=1).pack(fill="x")

        # Active Profile banner
        profile = self._logic.active_profile
        if profile != "Default" and not st.breadcrumb:
            tk.Label(self._win, text=f"◈ Profile: {profile}", bg="#162032", fg="#60a5fa",
                     font=_FONT_BC, anchor="w", padx=10, pady=4).pack(fill="x")
            tk.Frame(self._win, bg="#1e3a5f", height=1).pack(fill="x")

        # Breadcrumb folder navigation
        if st.breadcrumb:
            tk.Label(self._win, text=" › ".join(st.breadcrumb), bg=_BG, fg="#a1a1aa",
                     font=_FONT_BC, anchor="w", padx=10, pady=4).pack(fill="x")
            tk.Frame(self._win, bg=_BORDER, height=1).pack(fill="x")

        # Inline Volume Slider Card (at root level)
        if not st.breadcrumb:
            self._volume_widget = PanelVolumeWidget(self._win)
            self._volume_widget.pack(fill="x", padx=6, pady=(6, 4))

        # Items list
        self._item_renderer = PanelItemRenderer(self._win, on_select=self._logic.select_at)
        self._item_renderer.render_items(st.items, st.index)

        # Footer status bar
        self._render_footer(profile)
        self._win.update_idletasks()

    def _render_footer(self, profile: str) -> None:
        tk.Frame(self._win, bg=_BORDER, height=1).pack(fill="x", pady=(4, 0))
        footer = tk.Frame(self._win, bg=_BG, padx=8, pady=4)
        footer.pack(fill="x")
        prof_txt = f"◈ {profile}" if profile != "Default" else "◈ Ready"
        tk.Label(footer, text=prof_txt, bg=_BG, fg="#71717a", font=_FONT_FOOTER).pack(side="left")
        tk.Label(footer, text="↑↓ Move • ↵ Open • Esc", bg=_BG, fg="#71717a",
                 font=_FONT_FOOTER).pack(side="right")

    def _position(self) -> None:
        if not self._win:
            return
        px = self._root.winfo_pointerx()
        py = self._root.winfo_pointery()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._win.update_idletasks()
        h = self._win.winfo_reqheight()
        x = min(px + 10, sw - _W - 10)
        y = min(py - h // 2, sh - h - 40)
        self._win.geometry(f"{_W}x{h}+{max(x, 0)}+{max(y, 0)}")

    def _jump(self, n: int) -> None:
        if n < len(self._logic.state.items):
            self._logic.select_at(n)
