"""Gesture Guide Overlay: directional hint panel shown while a right-mouse-button
gesture is being drawn.

Ported from Touchpad Gesture's F-032 gesture_guide_overlay.py (same bottom-right
fixed panel, same click-through Toplevel construction mirroring trail_overlay.py),
adapted for a single mouse pointer instead of 3/4 touchpad fingers: the center icon
is a right-click glyph (no finger count), and there is no "finger_count" parameter.
"""
from __future__ import annotations

import ctypes
import math
from ctypes import wintypes
import tkinter as tk
from typing import Tuple

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000
WS_EX_TOOLWINDOW = 0x00000080

_GetWindowLong = ctypes.windll.user32.GetWindowLongW
_GetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int]
_GetWindowLong.restype = wintypes.LONG

_SetWindowLong = ctypes.windll.user32.SetWindowLongW
_SetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
_SetWindowLong.restype = wintypes.LONG

_PANEL = 480
_MARGIN = 24
_ARROW_COLOR = "#4EA8FF"
_LABEL_COLOR = "#CFE6FF"
_ICON_COLOR = "#4EA8FF"
_BG_KEY = "#000001"

# Screen-space unit vector per cardinal direction (y grows downward on canvas).
_VECTORS: dict[str, Tuple[float, float]] = {
    "UP": (0.0, -1.0),
    "DOWN": (0.0, 1.0),
    "LEFT": (-1.0, 0.0),
    "RIGHT": (1.0, 0.0),
}
_ALL_DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")

# UP/DOWN labels sit beyond the arrow tip along the same (vertical) axis, anchored
# away from the arrow so they never fall back over it; the panel's full width is
# free to wrap into on that axis, so they get a generous width.
#
# LEFT/RIGHT arrows are horizontal, so that same "past the tip" position leaves very
# little room before hitting the panel's side edge. Instead, their labels sit BELOW
# the arrow line (vertical offset, same side as the arrow), clear of the stroke,
# where the panel's vertical room lets them use a much wider wrap width.
_LABEL_ANCHOR: dict[str, str] = {"UP": "s", "DOWN": "n", "LEFT": "center", "RIGHT": "center"}
_LABEL_WIDTH: dict[str, int] = {"UP": 220, "DOWN": 220, "LEFT": 180, "RIGHT": 180}
_LABEL_SIDE_X = 115  # LEFT/RIGHT label horizontal offset from center
_LABEL_SIDE_Y = 48   # LEFT/RIGHT label vertical offset below the arrow line


class GestureGuideOverlay:
    """Fixed bottom-right panel showing live directional hints for a RMB-held gesture."""

    def __init__(self, root: tk.Tk | None = None) -> None:
        self._root = root
        self._win: tk.Toplevel | None = None
        self._canvas: tk.Canvas | None = None
        self._active: bool = False

    def _get_root(self) -> tk.Tk | None:
        if self._root is not None:
            return self._root
        return getattr(tk, "_default_root", None)

    def start(self, labels: dict[str, str]) -> None:
        """Show the panel with the 4 cardinal directions. Thread-safe."""
        root = self._get_root()
        if root is not None:
            root.after(0, lambda: self._do_start(labels))
        else:
            self._do_start(labels)

    def update_sectors(self, path: list[str], labels: dict[str, str]) -> None:
        """Re-render with the directions still available after `path`. Thread-safe."""
        root = self._get_root()
        if root is not None:
            root.after(0, lambda: self._do_update(path, labels))
        else:
            self._do_update(path, labels)

    def stop(self) -> None:
        """Hide the panel immediately (no fade/delay). Thread-safe."""
        root = self._get_root()
        if root is not None:
            root.after(0, self._do_stop)
        else:
            self._do_stop()

    def _do_start(self, labels: dict[str, str]) -> None:
        root = self._get_root()
        if root is None:
            return

        if self._active and self._win is not None and self._win.winfo_exists():
            self._render(_ALL_DIRECTIONS, labels)
            return

        self._do_stop()

        user32 = ctypes.windll.user32
        vx = user32.GetSystemMetrics(76)
        vy = user32.GetSystemMetrics(77)
        vw = user32.GetSystemMetrics(78)
        vh = user32.GetSystemMetrics(79)
        if vw <= 0 or vh <= 0:
            vx, vy = 0, 0
            vw = root.winfo_screenwidth()
            vh = root.winfo_screenheight()

        px = vx + vw - _PANEL - _MARGIN
        py = vy + vh - _PANEL - _MARGIN

        win = tk.Toplevel(root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-transparentcolor", _BG_KEY)
        win.config(bg=_BG_KEY)
        win.geometry(f"{_PANEL}x{_PANEL}+{px}+{py}")

        canvas = tk.Canvas(win, width=_PANEL, height=_PANEL, bg=_BG_KEY, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id()) or win.winfo_id()
        cur = _GetWindowLong(hwnd, GWL_EXSTYLE)
        _SetWindowLong(
            hwnd,
            GWL_EXSTYLE,
            int(cur) | WS_EX_NOACTIVATE | WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOOLWINDOW,
        )

        self._win = win
        self._canvas = canvas
        self._active = True
        self._render(_ALL_DIRECTIONS, labels)

    def _do_update(self, path: list[str], labels: dict[str, str]) -> None:
        if not self._active or self._canvas is None or not path:
            return
        last = path[-1]
        remaining = tuple(d for d in _ALL_DIRECTIONS if d != last)
        self._render(remaining, labels)

    def _do_stop(self) -> None:
        self._active = False
        if self._win is not None:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None
            self._canvas = None
            root = self._get_root()
            if root is not None:
                try:
                    from src.core.memory_manager import trim_memory
                    root.after(300, trim_memory)
                except Exception:
                    pass

    # ── Rendering ──────────────────────────────────────────────────────────

    def _render(self, directions: tuple[str, ...], labels: dict[str, str]) -> None:
        canvas = self._canvas
        if canvas is None:
            return
        canvas.delete("all")

        cx = cy = _PANEL / 2.0

        self._draw_rounded_rect(canvas, 2, 2, _PANEL - 2, _PANEL - 2, 36, fill="#0a0a0e", outline="")
        self._draw_rmb_icon(canvas, cx, cy)

        hub_r = 45
        tip_r = 130
        label_r = 144
        for direction in directions:
            dx, dy = _VECTORS[direction]
            x0, y0 = cx + dx * hub_r, cy + dy * hub_r
            x1, y1 = cx + dx * tip_r, cy + dy * tip_r
            self._draw_arrow(canvas, x0, y0, x1, y1)

            if direction in ("LEFT", "RIGHT"):
                lx = cx + (_LABEL_SIDE_X if direction == "RIGHT" else -_LABEL_SIDE_X)
                ly = cy + _LABEL_SIDE_Y
            else:
                lx, ly = cx + dx * label_r, cy + dy * label_r

            text = labels.get(direction, "")
            if text:
                canvas.create_text(
                    lx, ly, text=text, fill=_LABEL_COLOR, font=("Segoe UI", 11, "bold"),
                    anchor=_LABEL_ANCHOR[direction], width=_LABEL_WIDTH[direction], justify="center",
                )

    def _draw_rmb_icon(self, canvas: tk.Canvas, cx: float, cy: float) -> None:
        """Simple right-click glyph: a mouse body outline with the right button filled."""
        canvas.create_oval(cx - 39, cy - 39, cx + 39, cy + 39, outline=_ICON_COLOR, width=3, fill="")
        body_w, body_h = 27, 39
        self._draw_rounded_rect(
            canvas, cx - body_w / 2, cy - body_h / 2, cx + body_w / 2, cy + body_h / 2, 12,
            outline=_ICON_COLOR, width=3, fill="",
        )
        canvas.create_line(cx, cy - body_h / 2, cx, cy - 3, fill=_ICON_COLOR, width=3)
        canvas.create_rectangle(
            cx + 0.5, cy - body_h / 2 + 3, cx + body_w / 2 - 3, cy - 3,
            fill=_ICON_COLOR, outline="",
        )

    def _draw_arrow(self, canvas: tk.Canvas, x0: float, y0: float, x1: float, y1: float) -> None:
        canvas.create_line(x0, y0, x1, y1, fill=_ARROW_COLOR, width=5, capstyle=tk.ROUND)
        ang = math.atan2(y1 - y0, x1 - x0)
        head = 15
        spread = math.radians(28)
        hx1 = x1 - head * math.cos(ang - spread)
        hy1 = y1 - head * math.sin(ang - spread)
        hx2 = x1 - head * math.cos(ang + spread)
        hy2 = y1 - head * math.sin(ang + spread)
        canvas.create_polygon(x1, y1, hx1, hy1, hx2, hy2, fill=_ARROW_COLOR, outline="")

    def _draw_rounded_rect(self, canvas: tk.Canvas, x0, y0, x1, y1, r, **kwargs) -> None:
        points = [
            x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
            x1, y1 - r, x1, y1, x1 - r, y1, x0 + r, y1,
            x0, y1, x0, y1 - r, x0, y0 + r, x0, y0,
        ]
        canvas.create_polygon(points, smooth=True, **kwargs)
