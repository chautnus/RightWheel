"""Inline volume slider widget for Raycast-style shortcut panel."""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from ..services import volume_service

_BG = "#18181b"
_BG_CARD = "#1c1c20"
_TRACK_BG = "#27272a"
_TRACK_FILL = "#0078d4"
_FG_TEXT = "#ffffff"
_FG_MUTED = "#a1a1aa"
_THUMB = "#ffffff"
_BORDER = "#27272a"


def get_speaker_glyph(level: float, is_muted: bool = False) -> str:
    """Return speaker glyph based on volume percentage and mute status."""
    if is_muted or level <= 0.001:
        return "🔇"
    if level < 0.34:
        return "🔈"
    if level < 0.67:
        return "🔉"
    return "🔊"


class PanelVolumeWidget:
    """Compact interactive volume slider embedded in the shortcut panel."""

    def __init__(self, parent: tk.Widget, on_change: Callable[[], None] | None = None) -> None:
        self._parent = parent
        self._on_change = on_change
        self._level: float = 0.5
        self._is_muted: bool = False

        self._frame = tk.Frame(parent, bg=_BG_CARD, highlightbackground=_BORDER,
                               highlightthickness=1, padx=8, pady=5)

        # Header row: Speaker icon + "Volume" title + percentage badge
        hdr = tk.Frame(self._frame, bg=_BG_CARD)
        hdr.pack(fill="x", pady=(0, 4))

        self._icon_lbl = tk.Label(hdr, text="🔊", bg=_BG_CARD, fg=_FG_TEXT,
                                  font=("Segoe UI Emoji", 10), cursor="hand2")
        self._icon_lbl.pack(side="left", padx=(0, 4))
        self._icon_lbl.bind("<Button-1>", self._on_toggle_mute)

        self._title_lbl = tk.Label(hdr, text="Volume", bg=_BG_CARD, fg=_FG_TEXT,
                                   font=("Segoe UI", 9, "bold"))
        self._title_lbl.pack(side="left")

        self._pct_lbl = tk.Label(hdr, text="50%", bg=_BG_CARD, fg=_FG_MUTED,
                                 font=("Segoe UI", 9))
        self._pct_lbl.pack(side="right")

        # Slider canvas
        self._c_w = 216
        self._c_h = 14
        self._canvas = tk.Canvas(self._frame, width=self._c_w, height=self._c_h,
                                 bg=_BG_CARD, highlightthickness=0, cursor="hand2")
        self._canvas.pack(fill="x")

        # Mouse event bindings
        for w in (self._frame, hdr, self._title_lbl, self._pct_lbl, self._canvas):
            w.bind("<MouseWheel>", self._on_wheel)

        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.bind("<B1-Motion>", self._on_drag)

        self.refresh()

    def pack(self, **kwargs) -> None:
        """Pack the volume widget frame."""
        self._frame.pack(**kwargs)

    def refresh(self) -> None:
        """Fetch real Windows volume and redraw slider state."""
        try:
            self._level = volume_service.get_master_volume()
            self._is_muted = volume_service.get_mute()
        except Exception:
            self._level = 0.5
            self._is_muted = False

        pct = int(round(self._level * 100))
        glyph = get_speaker_glyph(self._level, self._is_muted)
        self._icon_lbl.configure(text=glyph)
        self._pct_lbl.configure(text=f"{pct}%")

        self._canvas.delete("all")
        x1, x2 = 4, self._c_w - 4
        y1, y2 = 4, 10

        # Background track
        self._canvas.create_rectangle(x1, y1, x2, y2, fill=_TRACK_BG, outline="", width=0)

        # Active fill track
        if self._level > 0.001 and not self._is_muted:
            fill_x = x1 + (x2 - x1) * min(1.0, max(0.0, self._level))
            self._canvas.create_rectangle(x1, y1, fill_x, y2, fill=_TRACK_FILL, outline="", width=0)
            # Thumb handle
            self._canvas.create_oval(fill_x - 3, 2, fill_x + 3, 12, fill=_THUMB, outline="")

    def _on_click(self, event: tk.Event) -> None:
        self._update_from_x(event.x)

    def _on_drag(self, event: tk.Event) -> None:
        self._update_from_x(event.x)

    def _update_from_x(self, x: int) -> None:
        x1, x2 = 4, self._c_w - 4
        ratio = max(0.0, min(1.0, (x - x1) / max(1, x2 - x1)))
        if self._is_muted:
            volume_service.set_mute(False)
        volume_service.set_master_volume(ratio)
        self.refresh()
        if self._on_change:
            self._on_change()

    def _on_wheel(self, event: tk.Event) -> None:
        delta = 1 if event.delta > 0 else -1
        if self._is_muted and delta > 0:
            volume_service.set_mute(False)
        volume_service.step_volume(delta, step=0.03)
        self.refresh()
        if self._on_change:
            self._on_change()

    def _on_toggle_mute(self, _: tk.Event) -> None:
        volume_service.set_mute(not self._is_muted)
        self.refresh()
        if self._on_change:
            self._on_change()
