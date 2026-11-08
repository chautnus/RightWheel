"""Fullscreen transparent overlay canvas displaying real-time mouse gesture trails."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import tkinter as tk


class TrailOverlay:
    """Fullscreen transparent overlay canvas displaying real-time mouse gesture trails."""

    def __init__(self, root: tk.Tk | None = None) -> None:
        self._root = root
        self._win: tk.Toplevel | None = None
        self._canvas: tk.Canvas | None = None
        self._poll_job: str | None = None
        self._last_point: tuple[int, int] | None = None
        self._active: bool = False
        self._vx: int = 0
        self._vy: int = 0

    def _get_root(self) -> tk.Tk | None:
        if self._root is not None:
            return self._root
        return getattr(tk, "_default_root", None)

    def start(self, x: int, y: int) -> None:
        """Begin gesture trail drawing at starting point (x, y). Thread-safe."""
        root = self._get_root()
        if root is not None:
            root.after(0, lambda: self._do_start(x, y))
        else:
            self._do_start(x, y)

    def stop(self) -> None:
        """Stop gesture trail and immediately destroy overlay window. Thread-safe."""
        root = self._get_root()
        if root is not None:
            root.after(0, self._do_stop)
        else:
            self._do_stop()

    def _do_start(self, x: int, y: int) -> None:
        root = self._get_root()
        if root is None:
            return

        self._do_stop()

        user32 = ctypes.windll.user32
        vx = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
        vy = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
        vw = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        vh = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
        if vw <= 0 or vh <= 0:
            vx, vy = 0, 0
            vw = root.winfo_screenwidth()
            vh = root.winfo_screenheight()

        self._vx = vx
        self._vy = vy

        win = tk.Toplevel(root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-transparentcolor", "#000001")
        win.config(bg="#000001")
        win.geometry(f"{vw}x{vh}+{vx}+{vy}")

        canvas = tk.Canvas(win, bg="#000001", highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        self._win = win
        self._canvas = canvas
        self._last_point = (x - vx, y - vy)
        self._active = True
        self._poll()

    def _poll(self) -> None:
        if not self._active or self._canvas is None:
            return

        pt = wintypes.POINT()
        if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
            cx = pt.x - self._vx
            cy = pt.y - self._vy
            if self._last_point is not None:
                lx, ly = self._last_point
                if (lx, ly) != (cx, cy):
                    self._canvas.create_line(
                        lx,
                        ly,
                        cx,
                        cy,
                        fill="#00e5ff",
                        width=3,
                        capstyle=tk.ROUND,
                        joinstyle=tk.ROUND,
                    )
                    self._last_point = (cx, cy)

        root = self._get_root()
        if self._active and root is not None:
            self._poll_job = root.after(16, self._poll)

    def _do_stop(self) -> None:
        self._active = False
        root = self._get_root()
        if self._poll_job and root is not None:
            try:
                root.after_cancel(self._poll_job)
            except Exception:
                pass
            self._poll_job = None

        if self._win is not None:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None
            self._canvas = None

        self._last_point = None
