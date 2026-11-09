"""Volume overlay HUD — displays master volume level and responds to mouse scroll."""
from __future__ import annotations

import tkinter as tk

from ..services import config_service, shortcut_executor
from features.i18n import ui_font

_BG = "#18181b"
_BORDER = "#3f3f46"
_TRACK_BG = "#27272a"
_ACC = "#0078d4"
_WIDTH = 224
_HEIGHT = 46


def _speaker_icon(level: float) -> str:
    """Return appropriate speaker glyph based on volume percentage."""
    if level <= 0.001:
        return "🔇"
    if level < 0.34:
        return "🔈"
    if level < 0.67:
        return "🔉"
    return "🔊"


class VolumeOverlay:
    """Floating Capsule HUD for volume adjustment via mouse scroll."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._backdrop: tk.Toplevel | None = None
        self._win: tk.Toplevel | None = None
        self._canvas: tk.Canvas | None = None
        self._dismiss_timer: str | None = None
        self._level: float = 0.5

    def show(self) -> None:
        """Create and display the volume overlay near cursor."""
        self.hide()

        # Fullscreen transparent backdrop for outside-click dismiss
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._backdrop = tk.Toplevel(self._root)
        self._backdrop.overrideredirect(True)
        self._backdrop.attributes("-topmost", True)
        self._backdrop.attributes("-alpha", 0.01)
        self._backdrop.geometry(f"{sw}x{sh}+0+0")
        self._backdrop.bind("<ButtonPress>", lambda _: self.hide())
        self._backdrop.bind("<MouseWheel>", self._on_scroll)

        # Capsule volume indicator window with 1px modern border
        self._win = tk.Toplevel(self._root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.configure(bg=_BORDER)
        self._win.bind("<Escape>", lambda _: self.hide())
        self._win.bind("<MouseWheel>", self._on_scroll)

        self._render()
        self._win.lift()
        self._win.focus_force()
        self._position()

        self._dismiss_timer = self._root.after(3000, self.hide)

    def _render(self) -> None:
        """Render the capsule slider, dynamic icon, and percentage."""
        if not self._win:
            return

        cw = _WIDTH - 2
        ch = _HEIGHT - 2
        if self._canvas is None:
            self._canvas = tk.Canvas(
                self._win,
                width=cw,
                height=ch,
                bg=_BG,
                highlightthickness=0,
            )
            self._canvas.pack(padx=1, pady=1)
            self._canvas.bind("<MouseWheel>", self._on_scroll)
        else:
            self._canvas.delete("all")

        # 1. Dynamic speaker icon
        icon = _speaker_icon(self._level)
        self._canvas.create_text(
            18, ch // 2,
            text=icon,
            font=("Segoe UI Emoji", 11),
            fill="#ffffff",
            anchor="center",
        )

        # 2. Track & Fill
        tx1, tx2 = 36, cw - 48
        ty1, ty2 = (ch // 2) - 3, (ch // 2) + 3
        self._canvas.create_rectangle(tx1, ty1, tx2, ty2, fill=_TRACK_BG, outline="")

        fill_w = int((tx2 - tx1) * self._level)
        if fill_w > 0:
            self._canvas.create_rectangle(
                tx1, ty1, min(tx2, tx1 + fill_w), ty2,
                fill=_ACC, outline=""
            )

        # 3. Thumb indicator
        thumb_x = min(tx2, max(tx1, tx1 + fill_w))
        self._canvas.create_oval(
            thumb_x - 5, (ch // 2) - 5,
            thumb_x + 5, (ch // 2) + 5,
            fill="#ffffff", outline="",
        )

        # 4. Percentage label
        pct = f"{int(round(self._level * 100))}%"
        self._canvas.create_text(
            cw - 8, ch // 2,
            text=pct,
            font=(ui_font(), 9, "bold"),
            fill="#e4e4e7",
            anchor="e",
        )

    def _position(self) -> None:
        """Position overlay near cursor and clamp within screen."""
        if not self._win:
            return
        px = self._root.winfo_pointerx()
        py = self._root.winfo_pointery()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()

        x = max(10, min(px - _WIDTH // 2, sw - _WIDTH - 10))
        y = max(10, min(py - _HEIGHT // 2, sh - _HEIGHT - 40))
        self._win.geometry(f"{_WIDTH}x{_HEIGHT}+{x}+{y}")

    def _on_scroll(self, event) -> None:
        """Handle scroll event to change volume and update timer."""
        delta = 1 if getattr(event, "delta", 0) > 0 else -1
        shortcut_executor.send_volume_step(delta)

        step = config_service.get_volume_step()
        self._level = max(0.0, min(1.0, self._level + step * delta))
        self._render()

        if self._dismiss_timer:
            try:
                self._root.after_cancel(self._dismiss_timer)
            except Exception:
                pass
        self._dismiss_timer = self._root.after(3000, self.hide)

    def hide(self) -> None:
        """Dismiss the volume overlay and clear timers."""
        if self._dismiss_timer:
            try:
                self._root.after_cancel(self._dismiss_timer)
            except Exception:
                pass
            self._dismiss_timer = None

        if self._backdrop:
            try:
                self._backdrop.destroy()
            except Exception:
                pass
            self._backdrop = None

        if self._win:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None

        self._canvas = None
