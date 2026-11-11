"""Item and kbd badge renderer for Raycast-style shortcut panel (no emoticons)."""
from __future__ import annotations

import re
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

_TYPE_LABEL = {
    "folder": "Folder",
    "app": "App",
    "url": "Web",
    "action": "System",
    "shortcut": "Keys",
    "command": "Script",
}

# Regex matching Unicode emoticons and pictographs
_EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff\u2600-\u27bf\u2300-\u23ff\u2b50\u200d\ufe0f\u25a0-\u25ff\u2190-\u21ff\u2700-\u27bf\u25b6\u25c0\u25b2\u25bc\u25cb\u25cf\u25e7-\u25fe]+",
    flags=re.UNICODE,
)


def _strip_emojis(text: str) -> str:
    """Strip leading or embedded emojis from text labels."""
    cleaned = _EMOJI_PATTERN.sub("", text).strip()
    return cleaned if cleaned else text


class PanelItemRenderer:
    """Renders shortcut items with Raycast-style kbd badges and subtle subtitles."""

    def __init__(self, parent: tk.Widget, on_select: Callable[[int], None]) -> None:
        self._parent = parent
        self._on_select = on_select
        self._container = tk.Frame(parent, bg=_BG_BASE)
        self._container.pack(fill="both", expand=True)
        self._row_views: list[tuple[tk.Frame, tk.Frame, tk.Label, tk.Label, tk.Label]] = []

    def clear(self) -> None:
        """Clear all rendered items."""
        for w in self._container.winfo_children():
            w.destroy()

    def render_items(self, items: list[MenuItem], selected_index: int) -> None:
        """Render the list of MenuItem objects with Raycast styling."""
        self.clear()
        self._row_views.clear()
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
        sep_box = tk.Frame(self._container, bg=_BG_BASE, padx=8)
        sep_box.pack(fill="x", pady=(6, 2))
        tk.Label(
            sep_box, text=title, bg=_BG_BASE, fg=_FG_SUB,
            font=("Segoe UI", 7, "bold"), anchor="w",
        ).pack(side="left")
        tk.Frame(sep_box, bg="#27272a", height=1).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def update_selection(self, old_idx: int, new_idx: int) -> None:
        """Update row styles in-place without re-rendering."""
        if 0 <= old_idx < len(self._row_views):
            row, acc_bar, kbd_badge, title_lbl, sub_lbl = self._row_views[old_idx]
            row.configure(bg=_BG_BASE)
            acc_bar.configure(bg=_BG_BASE)
            kbd_badge.configure(bg=_BG_KBD, fg=_FG_KBD, highlightbackground=_BORDER_KBD)
            title_lbl.configure(bg=_BG_BASE, fg=_FG_NORM, font=("Segoe UI", 10))
            sub_lbl.configure(bg=_BG_BASE)

        if 0 <= new_idx < len(self._row_views):
            row, acc_bar, kbd_badge, title_lbl, sub_lbl = self._row_views[new_idx]
            row.configure(bg=_BG_SEL)
            acc_bar.configure(bg=_ACCENT_BAR)
            kbd_badge.configure(bg=_BG_KBD_SEL, fg=_FG_KBD_SEL, highlightbackground=_BORDER_KBD_SEL)
            title_lbl.configure(bg=_BG_SEL, fg=_FG_SEL, font=("Segoe UI", 10, "bold"))
            sub_lbl.configure(bg=_BG_SEL)

    def _render_row(self, index: int, item: MenuItem, sel: bool) -> None:
        """Render a single shortcut item row without emoticons."""
        bg = _BG_SEL if sel else _BG_BASE
        itype = getattr(item, "type", "app")
        label_text = _strip_emojis(item.label)

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

        # Main Label (clean, no emoji)
        main_font = ("Segoe UI", 10, "bold") if sel else ("Segoe UI", 10)
        fg_text = _FG_SEL if sel else _FG_NORM
        title_lbl = tk.Label(
            row, text=label_text, bg=bg, fg=fg_text,
            font=main_font, anchor="w",
        )
        title_lbl.pack(side="left", fill="x", expand=True, padx=(2, 0))

        # Subtitle type badge on the far right
        sub_text = _TYPE_LABEL.get(itype, "")
        sub_lbl = tk.Label(
            row, text=sub_text, bg=bg, fg=_FG_SUB,
            font=("Segoe UI", 8), anchor="e",
        )
        sub_lbl.pack(side="right", padx=(4, 6))

        # Click event to select
        for w in (row, acc_bar, kbd_badge, title_lbl, sub_lbl):
            w.bind("<Button-1>", lambda _, idx=index: self._on_select(idx))

        self._row_views.append((row, acc_bar, kbd_badge, title_lbl, sub_lbl))
