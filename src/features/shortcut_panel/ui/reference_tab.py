"""Reference tab frame displaying common shortcuts and gesture references."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk

from features.i18n import ui_font
from .reference_shortcuts_data import _DEFAULT_SHORTCUTS

_BG = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG = "#cccccc"
_ACC = "#0078d4"


class ReferenceTab(tk.Frame):
    """Tab frame displaying common shortcut references with search filter."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=_BG)
        self._search_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        font_name = ui_font()

        # Search bar container
        search_frame = tk.Frame(self, bg=_BG)
        search_frame.pack(fill="x", padx=6, pady=(6, 4))

        search_icon = tk.Label(
            search_frame,
            text="🔍",
            bg=_BG,
            fg=_FG,
            font=(font_name, 10),
        )
        search_icon.pack(side="left", padx=(0, 4))

        self._search_entry = tk.Entry(
            search_frame,
            textvariable=self._search_var,
            bg=_BG2,
            fg=_FG,
            insertbackground=_FG,
            relief="flat",
            font=(font_name, 10),
        )
        self._search_entry.pack(side="left", fill="x", expand=True, ipady=3)
        self._search_entry.bind("<KeyRelease>", self._on_search)

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
        container.pack(fill="both", expand=True, padx=6, pady=(0, 6))

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

        self._tree.column("category", width=140, anchor="w")
        self._tree.column("shortcut", width=190, anchor="w")
        self._tree.column("description", width=340, anchor="w")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._populate_tree(_DEFAULT_SHORTCUTS)

    def _populate_tree(self, shortcuts: list[tuple[str, str, str]]) -> None:
        self._tree.delete(*self._tree.get_children())
        for cat, shortcut, desc in shortcuts:
            self._tree.insert("", "end", values=(cat, shortcut, desc))

    def _on_search(self, event: tk.Event | None = None) -> None:
        keyword = self._search_var.get().lower().strip()
        if not keyword:
            self._populate_tree(_DEFAULT_SHORTCUTS)
            return

        filtered = [
            (cat, sc, desc)
            for cat, sc, desc in _DEFAULT_SHORTCUTS
            if keyword in cat.lower() or keyword in sc.lower() or keyword in desc.lower()
        ]
        self._populate_tree(filtered)
