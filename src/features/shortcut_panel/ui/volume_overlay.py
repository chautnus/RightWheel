"""Volume overlay HUD — displays master volume level and responds to mouse scroll."""
from __future__ import annotations

import tkinter as tk

_BG = "#1e1e1e"
_TRACK_BG = "#333333"
_ACC = "#0078d4"
_WIDTH = 200
_HEIGHT = 50


class VolumeOverlay:
    """Floating HUD for volume adjustment via mouse scroll."""

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

        # Fullscreen transparent backdrop
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._backdrop = tk.Toplevel(self._root)
        self._backdrop.overrideredirect(True)
        self._backdrop.attributes("-topmost", True)
        self._backdrop.attributes("-alpha", 0.01)
        self._backdrop.geometry(f"{sw}x{sh}+0+0")
        self._backdrop.bind("<ButtonPress>", lambda _: self.hide())
        self._backdrop.bind("<MouseWheel>", self._on_scroll)

        # Small volume indicator window
        self._win = tk.Toplevel(self._root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.configure(bg=_BG)
        self._win.bind("<Escape>", lambda _: self.hide())
        self._win.bind("<MouseWheel>", self._on_scroll)

        self._render()
        self._win.lift()
        self._win.focus_force()
        self._position()

        self._dismiss_timer = self._root.after(3000, self.hide)

    def _render(self) -> None:
        """Render the volume slider on canvas."""
        if not self._win:
            return

        cw = 180
        ch = 20
        if self._canvas is None:
            self._canvas = tk.Canvas(
                self._win,
                width=cw,
                height=ch,
                bg=_BG,
                highlightthickness=0,
            )
            self._canvas.pack(padx=10, pady=15)
            self._canvas.bind("<MouseWheel>", self._on_scroll)
        else:
            self._canvas.delete("all")

        # Track
        self._canvas.create_rectangle(0, 6, cw, 14, fill=_TRACK_BG, outline="")

        # Fill
        fill_w = int(cw * self._level)
        if fill_w > 0:
            self._canvas.create_rectangle(0, 6, fill_w, 14, fill=_ACC, outline="")

        # Thumb
        thumb_x = min(cw, max(0, fill_w))
        self._canvas.create_oval(
            max(0, thumb_x - 5),
            3,
            min(cw, thumb_x + 5),
            17,
            fill="#ffffff",
            outline="",
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
        from ..services import shortcut_executor

        delta = 1 if getattr(event, "delta", 0) > 0 else -1
        shortcut_executor.send_volume_step(delta)
        self._level = max(0.0, min(1.0, self._level + 0.05 * delta))
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
