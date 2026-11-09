"""Floating shortcut panel — narrow, dark, always-on-top tkinter window."""
from __future__ import annotations

import queue, threading, tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic
    from .volume_overlay import VolumeOverlay

_W        = 240
_BG       = "#121214"
_BG_CARD  = "#18181b"
_BG_SEL   = "#27272a"
_FG       = "#a1a1aa"
_FG_SEL   = "#ffffff"
_FG_DIR   = "#4ec9b0"
_BORDER   = "#27272a"
_ACC      = "#0078d4"
_FONT     = ("Segoe UI", 11)
_FONT_SEL = ("Segoe UI", 11, "bold")
_FONT_BC  = ("Segoe UI", 9)
_FONT_NUM = ("Segoe UI", 8, "bold")


class PanelWindow:
    def __init__(self, logic: PanelLogic) -> None:
        self._logic   = logic
        self._q: queue.Queue = queue.Queue()
        self._root: tk.Tk | None      = None
        self._win:  tk.Toplevel | None = None
        self._overlay: tk.Toplevel | None = None
        self._volume_overlay: VolumeOverlay | None = None

        logic.on_show   = lambda: self._q.put("show")
        logic.on_hide   = lambda: self._q.put("hide")
        logic.on_update = lambda: self._q.put("update")
        logic.on_show_volume_slider = lambda: self._q.put("volume")

        threading.Thread(target=self._run, daemon=True).start()

    def open_settings(self) -> None:
        self._q.put("settings")

    def open_volume_slider(self) -> None:
        self._q.put("volume")

    # ── tkinter thread ─────────────────────────────────────────────────────

    def _run(self) -> None:
        self._root = tk.Tk()
        self._root.withdraw()
        from .welcome_window import show_welcome
        show_welcome(self._root)   # Toplevel on same root — no Tk conflict
        self._root.after(30, self._pump)
        self._root.mainloop()

    def _pump(self) -> None:
        try:
            while True:
                cmd = self._q.get_nowait()
                {"show": self._do_show, "hide": self._do_hide,
                 "update": self._do_update, "settings": self._do_settings,
                 "volume": self._do_volume,
                 }.get(cmd, lambda: None)()
        except queue.Empty:
            pass
        if self._root:
            self._root.after(30, self._pump)

    # ── window lifecycle ───────────────────────────────────────────────────

    def _do_show(self) -> None:
        if self._overlay:
            self._overlay.destroy()
        if self._win:
            self._win.destroy()

        # Fullscreen transparent overlay — any click outside panel closes it
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._overlay = tk.Toplevel(self._root)
        self._overlay.overrideredirect(True)
        self._overlay.attributes("-topmost", True)
        self._overlay.attributes("-alpha", 0.01)
        self._overlay.geometry(f"{sw}x{sh}+0+0")
        self._overlay.bind("<ButtonPress>", lambda _: self._logic.hide())

        self._win = tk.Toplevel(self._root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.configure(bg=_BG)
        self._win.bind("<Escape>", lambda _: self._logic.hide())
        self._win.bind("<BackSpace>", lambda _: self._logic.go_back())
        self._win.bind("<Return>", lambda _: self._logic.select_current())
        self._win.bind("<Up>", lambda _: self._logic.navigate(-1))
        self._win.bind("<Down>", lambda _: self._logic.navigate(1))
        self._win.bind("<MouseWheel>", lambda e: self._logic.navigate(-1 if e.delta > 0 else 1))
        for k in "0123456789":
            self._win.bind(k, lambda e, c=k: self._jump(int(c)))
        self._render()
        self._win.lift()        # map window above overlay first
        self._win.focus_force()
        self._position()        # position AFTER lift so geometry sticks

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

        # Paused indicator
        if self._logic.paused:
            tk.Label(self._win, text="⏸ Tạm dừng",
                     bg="#3a1a1a", fg="#f48771", font=_FONT_BC,
                     anchor="w", padx=10, pady=3).pack(fill="x")
            tk.Frame(self._win, bg="#6a2020", height=1).pack(fill="x")

        # Active profile name (only when not Default and at root level)
        profile = self._logic.active_profile
        if profile != "Default" and not st.breadcrumb:
            tk.Label(self._win, text=f"◈ {profile}",
                     bg="#0f3460", fg="#6ab0f5", font=_FONT_BC,
                     anchor="w", padx=10, pady=3).pack(fill="x")
            tk.Frame(self._win, bg="#1a4a8a", height=1).pack(fill="x")

        if st.breadcrumb:
            tk.Label(self._win, text=" › ".join(st.breadcrumb),
                     bg=_BG, fg="#71717a", font=_FONT_BC,
                     anchor="w", padx=10, pady=2).pack(fill="x")
            tk.Frame(self._win, bg=_BORDER, height=1).pack(fill="x")

        _ICON = {"folder": "📁 ", "app": "🚀 ", "url": "🌐 ", "action": "⚡ "}
        _CLR  = {"folder": _FG_DIR, "app": "#c586c0",
                 "url": "#4fc1ff", "action": "#dcdcaa"}
        for i, item in enumerate(st.items):
            sel  = (i == st.index)
            icon = _ICON.get(item.type, "")
            label_text = item.label
            if item.type == "action" and getattr(item, "action", "") == "show_volume_slider":
                from ..services import volume_service
                pct = int(round(volume_service.get_master_volume() * 100))
                icon = "🔊 "
                label_text = f"Volume ({pct}%)"

            fg   = _FG_SEL if sel else _CLR.get(item.type, _FG)
            row  = tk.Frame(self._win, bg=_BG_SEL if sel else _BG, padx=8, pady=4)
            row.pack(fill="x", padx=4, pady=1)

            num_bg = "#3f3f46" if sel else "#1e1e24"
            num_fg = "#ffffff" if sel else "#71717a"
            num_lbl = tk.Label(row, text=str(i), bg=num_bg, fg=num_fg,
                               font=_FONT_NUM, width=2, relief="flat")
            num_lbl.pack(side="left", padx=(0, 6))

            lbl = tk.Label(row, text=f"{icon}{label_text}",
                           bg=_BG_SEL if sel else _BG, fg=fg,
                           font=_FONT_SEL if sel else _FONT, anchor="w")
            lbl.pack(side="left", fill="x", expand=True)

            for widget in (row, num_lbl, lbl):
                widget.bind("<Button-1>", lambda _, ii=i: self._logic.select_at(ii))

        self._win.update_idletasks()

    def _position(self) -> None:
        if not self._win:
            return
        px = self._root.winfo_pointerx()
        py = self._root.winfo_pointery()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._win.update_idletasks()
        h  = self._win.winfo_reqheight()
        x  = min(px + 10, sw - _W - 10)
        y  = min(py - h // 2, sh - h - 40)
        self._win.geometry(f"{_W}x{h}+{x}+{max(y, 0)}")

    def _jump(self, n: int) -> None:
        if n < len(self._logic.state.items):
            self._logic.select_at(n)
