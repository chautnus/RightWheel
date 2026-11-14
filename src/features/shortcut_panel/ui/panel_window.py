"""Floating shortcut panel — Raycast-style command palette, always-on-top window."""
from __future__ import annotations

import queue, threading, tkinter as tk
from typing import TYPE_CHECKING

from .panel_item_renderer import PanelItemRenderer

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic
    from .settings_window import SettingsWindow

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
        self._item_renderer: PanelItemRenderer | None = None
        self._settings_window: SettingsWindow | None = None

        self._last_items: list = []
        self._last_breadcrumb: list[str] = []
        self._last_profile: str = ""
        self._last_paused: bool = False
        self._last_index: int = 0

        logic.on_show = lambda: self._q.put("show")
        logic.on_hide = lambda: self._q.put("hide")
        logic.on_update = lambda: self._q.put("update")

        threading.Thread(target=self._run, daemon=True).start()

    def open_settings(self) -> None:
        self._q.put("settings")

    # ── tkinter thread lifecycle ───────────────────────────────────────────

    def _run(self) -> None:
        self._root = tk.Tk()
        self._root.withdraw()
        self._root.after(30, self._pump)
        from .welcome_window import show_welcome
        show_welcome(self._root)
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

        self._last_items = []
        self._last_breadcrumb = []
        self._last_profile = ""
        self._last_paused = False
        self._last_index = 0

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
        if self._overlay:
            self._win.lift(self._overlay)
        else:
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
        if not self._win:
            return
        st = self._logic.state
        profile = self._logic.active_profile
        paused = self._logic.paused

        if (
            st.items != self._last_items
            or st.breadcrumb != self._last_breadcrumb
            or profile != self._last_profile
            or paused != self._last_paused
            or not self._item_renderer
        ):
            self._render()
        elif st.index != self._last_index:
            if self._item_renderer:
                self._item_renderer.update_selection(self._last_index, st.index)
            self._last_index = st.index

    def _do_settings(self) -> None:
        if (
            self._settings_window is not None
            and self._settings_window._win is not None
            and self._settings_window._win.winfo_exists()
        ):
            self._settings_window._win.deiconify()
            self._settings_window._win.lift()
            self._settings_window._win.focus_force()
            return

        from .settings_window import SettingsWindow
        self._settings_window = SettingsWindow(self._root, self._logic)
        self._settings_window.show()

    # ── rendering ──────────────────────────────────────────────────────────

    def _render(self) -> None:
        if not self._win:
            return
        for w in self._win.winfo_children():
            w.destroy()

        st = self._logic.state
        paused = self._logic.paused

        # Paused banner (no emoticon)
        if paused:
            tk.Label(self._win, text="[PAUSED] MouseHook Disabled", bg="#3a1a1a", fg="#f48771",
                     font=_FONT_BC, anchor="w", padx=10, pady=4).pack(fill="x")
            tk.Frame(self._win, bg="#6a2020", height=1).pack(fill="x")

        # Active Profile banner (no emoticon)
        profile = self._logic.active_profile
        if profile != "Default" and not st.breadcrumb:
            tk.Label(self._win, text=f"Profile: {profile}", bg="#162032", fg="#60a5fa",
                     font=_FONT_BC, anchor="w", padx=10, pady=4).pack(fill="x")
            tk.Frame(self._win, bg="#1e3a5f", height=1).pack(fill="x")

        # Breadcrumb folder navigation (clean slash separator)
        if st.breadcrumb:
            tk.Label(self._win, text=" / ".join(st.breadcrumb), bg=_BG, fg="#a1a1aa",
                     font=_FONT_BC, anchor="w", padx=10, pady=4).pack(fill="x")
            tk.Frame(self._win, bg=_BORDER, height=1).pack(fill="x")

        # Items list
        self._item_renderer = PanelItemRenderer(self._win, on_select=self._logic.select_at)
        self._item_renderer.render_items(st.items, st.index)

        # Update snapshot
        self._last_items = list(st.items)
        self._last_breadcrumb = list(st.breadcrumb)
        self._last_profile = profile
        self._last_paused = paused
        self._last_index = st.index

        # Footer status bar (no emoticon)
        self._render_footer(profile)
        self._win.update_idletasks()

    def _render_footer(self, profile: str) -> None:
        tk.Frame(self._win, bg=_BORDER, height=1).pack(fill="x", pady=(4, 0))
        footer = tk.Frame(self._win, bg=_BG, padx=8, pady=4)
        footer.pack(fill="x")
        prof_txt = f"Profile: {profile}" if profile != "Default" else "Ready"
        tk.Label(footer, text=prof_txt, bg=_BG, fg="#71717a", font=_FONT_FOOTER).pack(side="left")
        tk.Label(footer, text="↑↓ Move • Enter Open • Esc Close", bg=_BG, fg="#71717a",
                 font=_FONT_FOOTER).pack(side="right")

    def _position(self) -> None:
        if not self._win:
            return
        try:
            import ctypes
            from ctypes import wintypes
            pt = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            px, py = pt.x, pt.y
        except Exception:
            px = self._root.winfo_pointerx()
            py = self._root.winfo_pointery()

        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._win.update_idletasks()
        h = self._win.winfo_reqheight()
        # Open directly at mouse position (cursor placed 10px inside the top-left of the menu)
        x = max(10, min(px - 10, sw - _W - 10))
        y = max(10, min(py - 10, sh - h - 30))
        self._win.geometry(f"{_W}x{h}+{x}+{y}")

    def _jump(self, n: int) -> None:
        if n < len(self._logic.state.items):
            self._logic.select_at(n)
