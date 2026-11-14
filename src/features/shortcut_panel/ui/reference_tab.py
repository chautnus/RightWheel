"""Reference tab frame displaying common shortcuts and gesture references."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import Any

from features.i18n import ui_font
from ..services import config_service
from .reference_shortcuts_data import _DEFAULT_SHORTCUTS
from . import theme

_BG = theme.BG_CONTENT
_BG2 = theme.BG_CARD
_FG = theme.FG_SECONDARY
_ACC = theme.ACCENT_BLUE
_GRN = theme.COLOR_SUCCESS


class ReferenceTab(tk.Frame):
    """Tab frame displaying common shortcut references with search filter and 1-click import."""

    def __init__(self, parent: tk.Widget, logic: Any = None) -> None:
        super().__init__(parent, bg=_BG)
        self._logic = logic
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
        self._tree.bind("<Double-1>", lambda _: self._add_selected())

        # Bottom action bar for 1-click import into user shortcuts
        bot_bar = tk.Frame(self, bg=_BG)
        bot_bar.pack(fill="x", padx=6, pady=(4, 6))

        self._feedback_lbl = tk.Label(
            bot_bar,
            text="Nhấp đúp chuột hoặc chọn mục rồi bấm nút để thêm vào phím tắt của bạn:",
            bg=_BG,
            fg=theme.FG_MUTED,
            font=(font_name, 9),
        )
        self._feedback_lbl.pack(side="left")

        add_btn = tk.Button(
            bot_bar,
            text="+ Thêm vào Phím tắt của tôi",
            command=self._add_selected,
            bg=_ACC,
            fg="white",
            font=(font_name, 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=3,
        )
        add_btn.pack(side="right")

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

    def _add_selected(self) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        vals = self._tree.item(sel[0], "values")
        if not vals or len(vals) < 3:
            return
        cat, sc, desc = vals[0], vals[1], vals[2]

        # Ignore mouse combos that aren't keyboard hotkeys
        if "rmb" in sc.lower():
            self._feedback_lbl.configure(
                text=f"ℹ '{sc}' là cử chỉ chuột tích hợp, không phải phím tắt bàn phím.",
                fg=theme.COLOR_WARNING,
            )
            return

        keys = sc.lower().replace(" ", "")
        data = config_service.load()
        data.setdefault("default", []).append({"type": "shortcut", "label": desc, "keys": keys})
        config_service.save(data)

        if self._logic and hasattr(self._logic, "reload"):
            self._logic.reload()

        self._feedback_lbl.configure(
            text=f"✓ Đã thêm '{desc}' ({sc}) vào danh sách phím tắt!",
            fg=_GRN,
        )
        self.after(3500, self._reset_feedback)

    def _reset_feedback(self) -> None:
        self._feedback_lbl.configure(
            text="Nhấp đúp chuột hoặc chọn mục rồi bấm nút để thêm vào phím tắt của bạn:",
            fg=theme.FG_MUTED,
        )
