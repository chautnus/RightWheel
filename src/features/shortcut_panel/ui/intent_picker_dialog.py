"""Intent Picker Dialog: Search and pick standard shortcuts by goal/purpose."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import Callable

from features.i18n import ui_font
from ..services.intent_service import IntentItem, IntentService
from . import theme

_BG = theme.BG_CONTENT
_BG2 = theme.BG_CARD
_BORDER = theme.BORDER_SUBTLE
_FG = theme.FG_PRIMARY
_MUTED = theme.FG_MUTED
_ACC = theme.ACCENT_BLUE


class IntentPickerDialog(tk.Toplevel):
    """Modal dialog allowing users to browse and search actions by goal/intent."""

    @classmethod
    def ask(cls, parent: tk.Widget) -> IntentItem | None:
        dlg = cls(parent)
        parent.wait_window(dlg)
        return dlg.result

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.title("Trợ lý Phím tắt theo Mục đích")
        self.resizable(False, False)
        self.configure(bg=_BG)
        top_parent = parent.winfo_toplevel() if hasattr(parent, "winfo_toplevel") else parent
        self.transient(top_parent)
        self.grab_set()
        self.attributes("-topmost", True)

        self.service = IntentService()
        self.result: IntentItem | None = None
        self._items: list[IntentItem] = []

        self._build_ui()
        self._center(parent, width=540, height=480)
        self._search_var.set("")
        self._on_search()
        self._entry.focus_set()

    def _center(self, parent: tk.Widget, width: int, height: int) -> None:
        try:
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            if pw > 100 and ph > 100:
                x = px + (pw - width) // 2
                y = py + (ph - height) // 2
            else:
                sw = parent.winfo_screenwidth()
                sh = parent.winfo_screenheight()
                x = (sw - width) // 2
                y = (sh - height) // 2
        except Exception:
            x, y = 100, 100
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self) -> None:
        font_name = ui_font()
        p = tk.Frame(self, bg=_BG, padx=16, pady=14)
        p.pack(fill="both", expand=True)

        # Header
        tk.Label(
            p, text="Chọn phím tắt theo mục đích bạn muốn thực hiện",
            bg=_BG, fg=_FG, font=(font_name, 11, "bold"),
        ).pack(anchor="w")
        tk.Label(
            p, text="Gõ mục đích (chụp màn hình, đổi tab, task manager...) hoặc chọn danh mục:",
            bg=_BG, fg=_MUTED, font=(font_name, 9),
        ).pack(anchor="w", pady=(2, 8))

        # Search Bar
        sf = tk.Frame(p, bg=_BG)
        sf.pack(fill="x", pady=(0, 8))

        tk.Label(sf, text="🔍", bg=_BG, fg=_MUTED, font=(font_name, 10)).pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        self._entry = tk.Entry(
            sf, textvariable=self._search_var, bg=_BG2, fg=_FG,
            insertbackground=_FG, font=(font_name, 10), relief="flat", bd=4,
        )
        self._entry.pack(side="left", fill="x", expand=True)
        self._search_var.trace_add("write", lambda *_: self._on_search())

        # Category Filter Pills
        cat_frame = tk.Frame(p, bg=_BG)
        cat_frame.pack(fill="x", pady=(0, 8))
        tk.Label(cat_frame, text="Nhóm:", bg=_BG, fg=_MUTED, font=(font_name, 8)).pack(side="left", padx=(0, 6))

        self._cat_var = tk.StringVar(value="Tất cả")
        cats = ["Tất cả"] + self.service.get_all_categories()
        for cat in cats:
            rb = tk.Radiobutton(
                cat_frame, text=cat, variable=self._cat_var, value=cat,
                command=self._on_search, bg=_BG, fg=_FG, selectcolor=theme.BG_ACTIVE,
                activebackground=_BG, font=(font_name, 8), cursor="hand2",
            )
            rb.pack(side="left", padx=3)

        # Results Listbox
        list_box = tk.Frame(p, bg=_BG2, highlightbackground=_BORDER, highlightthickness=1)
        list_box.pack(fill="both", expand=True, pady=(0, 8))

        self._lb = tk.Listbox(
            list_box, bg=_BG2, fg=_FG, font=(font_name, 9),
            selectbackground=theme.BG_ACTIVE, selectforeground=_FG,
            relief="flat", bd=0, activestyle="none",
        )
        sb = ttk.Scrollbar(list_box, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._lb.pack(fill="both", expand=True, padx=4, pady=4)

        self._lb.bind("<Double-1>", lambda _: self._select_current())
        self._entry.bind("<Return>", lambda _: self._select_current())
        self._entry.bind("<Down>", lambda _: self._focus_list())
        self._lb.bind("<Return>", lambda _: self._select_current())
        self._lb.bind("<<ListboxSelect>>", self._on_preview_select)

        # Preview description
        self._desc_label = tk.Label(
            p, text="", bg=_BG, fg=_MUTED, font=(font_name, 8, "italic"),
            anchor="w", justify="left",
        )
        self._desc_label.pack(fill="x", pady=(0, 8))

        # Bottom Buttons
        btn_box = tk.Frame(p, bg=_BG)
        btn_box.pack(fill="x")

        tk.Button(
            btn_box, text="Chọn phím này", command=self._select_current,
            bg=_ACC, fg="white", font=(font_name, 9, "bold"),
            relief="flat", cursor="hand2", padx=12, pady=4,
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            btn_box, text="Nhập thủ công...", command=self.destroy,
            bg=theme.BG_CARD_HOVER, fg=_FG, font=(font_name, 9),
            relief="flat", cursor="hand2", padx=10, pady=4,
        ).pack(side="right")

    def _focus_list(self) -> None:
        if self._lb.size() > 0:
            self._lb.focus_set()
            if not self._lb.curselection():
                self._lb.selection_set(0)
                self._on_preview_select()

    def _on_search(self) -> None:
        q = self._search_var.get().strip()
        cat = self._cat_var.get()
        if cat == "Tất cả":
            items = self.service.search(q, limit=25)
        else:
            cat_items = self.service.get_by_category(cat)
            if q:
                temp_service = IntentService(catalog=cat_items)
                items = temp_service.search(q, limit=25)
            else:
                items = cat_items

        self._items = items
        self._lb.delete(0, "end")
        for it in items:
            self._lb.insert("end", f"[{it.category}]  {it.title_vi}  →  {it.keys.upper()}")

        if items:
            self._lb.selection_set(0)
            self._on_preview_select()
        else:
            self._desc_label.configure(text="Không tìm thấy phím tắt phù hợp. Bạn có thể chọn 'Nhập thủ công'.")

    def _on_preview_select(self, event: tk.Event | None = None) -> None:
        sel = self._lb.curselection()
        if sel and sel[0] < len(self._items):
            it = self._items[sel[0]]
            self._desc_label.configure(text=f"💡 {it.description} (Phím: {it.keys.upper()})")

    def _select_current(self) -> None:
        sel = self._lb.curselection()
        if sel and sel[0] < len(self._items):
            self.result = self._items[sel[0]]
            self.destroy()
