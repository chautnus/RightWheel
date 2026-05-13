"""Floating shortcut panel — narrow, tall, dark, always-on-top tkinter window.

Runs entirely on its own daemon thread; communicates with the hook thread via
a queue + root.after() pump so tkinter stays single-threaded.
"""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic

_W       = 230
_BG      = "#1a1a1a"
_BG_SEL  = "#2a2a2a"
_FG      = "#777777"
_FG_SEL  = "#ffffff"
_FG_DIR  = "#4ec9b0"
_FONT    = ("Segoe UI", 12)
_FONT_SEL= ("Segoe UI", 15, "bold")
_FONT_BC = ("Segoe UI", 9)


class PanelWindow:
    def __init__(self, logic: PanelLogic) -> None:
        self._logic  = logic
        self._q: queue.Queue = queue.Queue()
        self._root: tk.Tk | None  = None
        self._win:  tk.Toplevel | None = None

        logic.on_show   = lambda: self._q.put("show")
        logic.on_hide   = lambda: self._q.put("hide")
        logic.on_update = lambda: self._q.put("update")

        threading.Thread(target=self._run, daemon=True).start()

    def open_settings(self) -> None:
        self._q.put("settings")

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
                 "update": self._do_update, "settings": self._do_settings
                 }.get(cmd, lambda: None)()
        except queue.Empty:
            pass
        if self._root:
            self._root.after(30, self._pump)

    # ── window lifecycle ───────────────────────────────────────────────────

    def _do_show(self) -> None:
        if self._win:
            self._win.destroy()
        self._win = tk.Toplevel(self._root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.configure(bg=_BG)
        self._win.bind("<Escape>",    lambda _: self._logic.hide())
        self._win.bind("<BackSpace>", lambda _: self._logic.go_back())
        self._win.bind("<Return>",    lambda _: self._logic.select_current())
        self._win.bind("<Up>",        lambda _: self._logic.navigate(-1))
        self._win.bind("<Down>",      lambda _: self._logic.navigate(1))
        self._win.bind("<MouseWheel>",
                       lambda e: self._logic.navigate(-1 if e.delta > 0 else 1))
        self._win.bind("<FocusOut>",  lambda _: self._logic.hide())
        for k in "0123456789":
            self._win.bind(k, lambda e, c=k: self._jump(int(c)))
        self._hover_job: str | None = None
        self._render()
        self._position()
        self._win.focus_force()

    def _do_hide(self) -> None:
        if self._win:
            self._win.destroy()
            self._win = None

    def _do_update(self) -> None:
        if self._win:
            self._render()

    def _do_settings(self) -> None:
        from .settings_window import SettingsWindow
        SettingsWindow(self._root, self._logic).show()

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
                     bg=_BG, fg="#555", font=_FONT_BC,
                     anchor="w", padx=10, pady=2).pack(fill="x")
            tk.Frame(self._win, bg="#333", height=1).pack(fill="x")

        _ICON = {"folder": "📁 ", "app": "🚀 ", "url": "🌐 ", "action": "⚡ "}
        _CLR  = {"folder": _FG_DIR, "app": "#c586c0",
                 "url": "#4fc1ff", "action": "#dcdcaa"}
        for i, item in enumerate(st.items):
            sel  = (i == st.index)
            icon = _ICON.get(item.type, "")
            text = f"  {i}  {icon}{item.label}"
            fg   = _FG_SEL if sel else _CLR.get(item.type, _FG)
            lbl  = tk.Label(
                self._win, text=text,
                bg=_BG_SEL if sel else _BG,
                fg=fg,
                font=_FONT_SEL if sel else _FONT,
                anchor="w", padx=4,
                pady=7 if sel else 4,
                width=20, cursor="hand2",
            )
            lbl.pack(fill="x")
            lbl.bind("<Button-1>", lambda _, ii=i: self._logic.select_at(ii))
            if item.type == "folder":
                lbl.bind("<Enter>", lambda _, ii=i: self._on_hover(ii))
                lbl.bind("<Leave>", lambda _: self._cancel_hover())
            else:
                # Moving onto a non-folder cancels any pending folder open
                lbl.bind("<Enter>", lambda _: self._cancel_hover())

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

    def _on_hover(self, idx: int) -> None:
        """Schedule folder open after hover delay — no re-render triggered."""
        self._cancel_hover()
        if self._win:
            self._hover_job = self._win.after(
                400, lambda: self._logic.select_at(idx))

    def _cancel_hover(self) -> None:
        if self._hover_job and self._win:
            self._win.after_cancel(self._hover_job)
        self._hover_job = None

    def _jump(self, n: int) -> None:
        if n < len(self._logic.state.items):
            self._logic.select_at(n)
