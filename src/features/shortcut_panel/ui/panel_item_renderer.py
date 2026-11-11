"""Item and kbd badge renderer for Raycast-style shortcut panel."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types.panel_types import MenuItem

_BG_BASE = "#121214"
_BG_SEL = "#27272a"
_BG_KBD = "#1e1e24"
_BG_KBD_SEL = "#383842"
_BORDER_KBD = "#3f3f46"
_BORDER_KBD_SEL = "#6366f1"
_FG_KBD = "#858590"
_FG_KBD_SEL = "#ffffff"
_FG_SEL = "#ffffff"
_FG_NORM = "#d4d4d8"
_FG_SUB = "#71717a"
_ACCENT_BAR = "#0078d4"

_ICON = {
    "folder": "📁",
    "app": "🚀",
    "url": "🌐",
    "action": "⚡",
    "shortcut": "⌨",
    "command": "💻",
}

_TYPE_LABEL = {
    "folder": "Folder",
    "app": "App",
    "url": "Web",
    "action": "System",
    "shortcut": "Keys",
    "command": "Script",
}


class PanelItemRenderer:
    """Renders shortcut items with Raycast-style kbd badges and subtle subtitles."""

    def __init__(self, parent: tk.Widget, on_select: Callable[[int], None]) -> None:
        self._parent = parent
        self._on_select = on_select
        self._container = tk.Frame(parent, bg=_BG_BASE)
        self._container.pack(fill="both", expand=True)

    def clear(self) -> None:
        """Clear all rendered items."""
        for w in self._container.winfo_children():
            w.destroy()

    def render_items(self, items: list[MenuItem], selected_index: int) -> None:
        """Render the list of MenuItem objects with Raycast styling."""
        self.clear()
        if not items:
            tk.Label(
                self._container, text="No shortcuts configured",
                bg=_BG_BASE, fg=_FG_SUB, font=("Segoe UI", 9, "italic"),
                pady=16,
            ).pack(fill="x")
            return

        has_actions = any(getattr(it, "type", "") == "action" for it in items)
        first_action_seen = False

        for i, item in enumerate(items):
            sel = (i == selected_index)
            itype = getattr(item, "type", "app")

            # Section separator before system actions
            if has_actions and itype == "action" and not first_action_seen and i > 0:
                first_action_seen = True
                self._render_separator("SYSTEM ACTIONS")

            self._render_row(i, item, sel)

    def _render_separator(self, title: str) -> None:
        """Render a subtle Raycast-style section divider."""
        sep_box = tk.Frame(self._container, bg=_BG_BASE, padx=8, pady=(6, 2))
        sep_box.pack(fill="x")
        tk.Label(
            sep_box, text=title, bg=_BG_BASE, fg=_FG_SUB,
            font=("Segoe UI", 7, "bold"), anchor="w",
        ).pack(side="left")
        tk.Frame(sep_box, bg="#27272a", height=1).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _render_row(self, index: int, item: MenuItem, sel: bool) -> None:
        """Render a single shortcut item row."""
        bg = _BG_SEL if sel else _BG_BASE
        itype = getattr(item, "type", "app")
        icon = _ICON.get(itype, "•")
        label_text = item.label

        # If it's a volume action, show dynamic real volume
        if itype == "action" and getattr(item, "action", "") == "show_volume_slider":
            from ..services import volume_service
            pct = int(round(volume_service.get_master_volume() * 100))
            icon = "🔊"
            label_text = f"Master Volume ({pct}%)"

        row = tk.Frame(self._container, bg=bg, cursor="hand2")
        row.pack(fill="x", padx=4, pady=1)

        # Left Accent bar indicator (3px) for active row
        bar_color = _ACCENT_BAR if sel else bg
        acc_bar = tk.Frame(row, bg=bar_color, width=3)
        acc_bar.pack(side="left", fill="y", padx=(0, 4))

        # Keyboard number badge (mechanical kbd look)
        kbd_bg = _BG_KBD_SEL if sel else _BG_KBD
        kbd_fg = _FG_KBD_SEL if sel else _FG_KBD
        kbd_bd = _BORDER_KBD_SEL if sel else _BORDER_KBD
        kbd_badge = tk.Label(
            row, text=str(index) if index < 10 else "•",
            bg=kbd_bg, fg=kbd_fg, font=("Segoe UI", 8, "bold"),
            width=2, relief="flat", highlightbackground=kbd_bd,
            highlightthickness=1, pady=1,
        )
        kbd_badge.pack(side="left", padx=(2, 6), pady=3)

        # Icon + Main Label
        icon_lbl = tk.Label(
            row, text=icon, bg=bg, fg="#ffffff",
            font=("Segoe UI Emoji", 10),
        )
        icon_lbl.pack(side="left", padx=(0, 4))

        main_font = ("Segoe UI", 10, "bold") if sel else ("Segoe UI", 10)
        fg_text = _FG_SEL if sel else _FG_NORM
        title_lbl = tk.Label(
            row, text=label_text, bg=bg, fg=fg_text,
            font=main_font, anchor="w",
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        # Subtitle type badge on the far right
        sub_text = _TYPE_LABEL.get(itype, "")
        sub_lbl = tk.Label(
            row, text=sub_text, bg=bg, fg=_FG_SUB,
            font=("Segoe UI", 8), anchor="e",
        )
        sub_lbl.pack(side="right", padx=(4, 6))

        # Click event to select
        for w in (row, acc_bar, kbd_badge, icon_lbl, title_lbl, sub_lbl):
            w.bind("<Button-1>", lambda _, idx=index: self._on_select(idx))
