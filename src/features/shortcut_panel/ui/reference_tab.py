"""Reference tab frame displaying common shortcuts and gesture references."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk

from features.i18n import ui_font

_BG = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG = "#cccccc"
_ACC = "#0078d4"

_DEFAULT_SHORTCUTS: list[tuple[str, str, str]] = [
    ("RightWheel", "RMB + Scroll Up", "Open Shortcut Panel"),
    ("RightWheel", "RMB + Scroll Down", "Switch app (Alt+Tab)"),
    ("RightWheel", "RMB + Drag", "Draw gesture to run custom shortcut"),
    ("RightWheel", "RMB + X1/X2", "Switch browser tab prev/next"),
    ("Windows System", "Win + D", "Show/hide desktop"),
    ("Windows System", "Win + E", "Open File Explorer"),
    ("Windows System", "Win + L", "Lock PC"),
    ("Windows System", "Win + R", "Open Run dialog"),
    ("Windows System", "Win + Tab", "Task view"),
    ("Windows System", "Win + Shift + S", "Snip & Sketch screenshot"),
    ("Windows System", "Win + I", "Open Settings"),
    ("Windows System", "Win + V", "Clipboard history"),
    ("Window Management", "Win + Left/Right", "Snap window half screen"),
    ("Window Management", "Win + Up/Down", "Maximize/minimize window"),
    ("Window Management", "Alt + Tab", "Switch windows"),
    ("Window Management", "Alt + F4", "Close window"),
    ("Browser", "Ctrl + T", "New tab"),
    ("Browser", "Ctrl + W", "Close tab"),
    ("Browser", "Ctrl + Tab", "Next tab"),
    ("Browser", "Ctrl + Shift + Esc", "Task Manager"),
    ("Browser", "Ctrl + R", "Reload page"),
]


class ReferenceTab(tk.Frame):
    """Tab frame displaying common shortcut references."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=_BG)
        self._build()

    def _build(self) -> None:
        font_name = ui_font()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Reference.Treeview",
            background=_BG2,
            foreground=_FG,
            fieldbackground=_BG2,
            borderwidth=0,
            font=(font_name, 9),
            rowheight=24,
        )
        style.configure(
            "Reference.Treeview.Heading",
            background=_BG,
            foreground=_FG,
            font=(font_name, 10, "bold"),
            borderwidth=1,
            relief="flat",
        )
        style.map(
            "Reference.Treeview",
            background=[("selected", _ACC)],
            foreground=[("selected", "#ffffff")],
        )

        container = tk.Frame(self, bg=_BG)
        container.pack(fill="both", expand=True)

        cols = ("category", "shortcut", "description")
        self._tree = ttk.Treeview(
            container,
            columns=cols,
            show="headings",
            style="Reference.Treeview",
            selectmode="browse",
        )

        self._tree.heading("category", text="Category")
        self._tree.heading("shortcut", text="Shortcut")
        self._tree.heading("description", text="Description")

        self._tree.column("category", width=130, anchor="w")
        self._tree.column("shortcut", width=180, anchor="w")
        self._tree.column("description", width=330, anchor="w")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for cat, shortcut, desc in _DEFAULT_SHORTCUTS:
            self._tree.insert("", "end", values=(cat, shortcut, desc))
