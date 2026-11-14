"""Gestures tab — modern mouse gesture management with interactive test playground."""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from ..services import config_service
from .ask_dialog import _AskDialog, _btn
from .key_recorder_dialog import KeyRecorderDialog
from ..logic.gesture_recognizer import GestureRecognizer
from . import theme
from features.i18n import t, ui_font

_BG  = theme.BG_CONTENT
_BG2 = theme.BG_CARD
_FG  = theme.FG_SECONDARY
_ACC = theme.ACCENT_BLUE
_RED = theme.COLOR_DANGER
_GRN = theme.COLOR_SUCCESS
_BTN_NEUTRAL = theme.BORDER_INPUT

_ARROWS = {
    "U": "↑", "D": "↓", "L": "←", "R": "→",
    "UR": "↗", "DR": "↘", "DL": "↙", "UL": "↖",
}


def _format_directions(dirs: list[str]) -> str:
    """Format directions list into clean arrow glyphs."""
    arrows = " ".join(_ARROWS.get(d.strip().upper(), d) for d in dirs)
    return f"[ {arrows} ]"


class GesturesTab(tk.Frame):
    """Tab frame for managing mouse gestures with a real-time test playground."""

    def __init__(self, parent: tk.Widget, on_saved: Callable | None = None) -> None:
        super().__init__(parent, bg=_BG)
        self._on_saved = on_saved
        self._dialog_open = False
        self._test_recognizer = GestureRecognizer(threshold=16)
        self._test_pts: list[tuple[int, int]] = []
        self._build()

    def _build(self) -> None:
        font = ui_font()

        # ── 1. Top Header ────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=_BG)
        hdr.pack(fill="x", padx=4, pady=(0, 6))

        tk.Label(
            hdr, text=t("settings.tab.gestures"),
            bg=_BG, fg=theme.FG_PRIMARY, font=(font, 11, "bold")
        ).pack(side="left")
        tk.Label(
            hdr, text="• Giữ chuột phải + Kéo theo hướng",
            bg=_BG, fg=theme.FG_MUTED, font=(font, 9)
        ).pack(side="left", padx=(8, 0))

        _btn(hdr, "+ Thêm Cử chỉ", self._add, bg=_ACC).pack(side="right", padx=2)

        # ── 2. Gesture List Frame ────────────────────────────────────────────
        list_wrap = tk.Frame(self, bg=theme.BORDER_SUBTLE, padx=1, pady=1)
        list_wrap.pack(fill="both", expand=True, padx=4)

        lf = tk.Frame(list_wrap, bg=_BG2)
        lf.pack(fill="both", expand=True)

        self._lb = tk.Listbox(
            lf, bg=_BG2, fg=_FG, font=(font, 10),
            selectbackground=_ACC, selectforeground="#ffffff",
            relief="flat", bd=0, activestyle="none", highlightthickness=0
        )
        sb = tk.Scrollbar(lf, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._lb.pack(fill="both", expand=True, padx=4, pady=4)
        self._lb.bind("<Double-Button-1>", lambda _: self._edit())

        # ── 3. Action Toolbar ────────────────────────────────────────────────
        act_box = tk.Frame(self, bg=_BG)
        act_box.pack(fill="x", padx=4, pady=(6, 8))

        tk.Label(
            act_box, text="Nhấp đúp để đổi phím • Chọn để bật/tắt hoặc xóa",
            bg=_BG, fg=theme.FG_MUTED, font=(font, 9)
        ).pack(side="left")

        btn_row = tk.Frame(act_box, bg=_BG)
        btn_row.pack(side="right")
        _btn(btn_row, "Sửa phím", self._edit, bg=_BTN_NEUTRAL).pack(side="left", padx=2)
        _btn(btn_row, "Bật / Tắt", self._toggle, bg=_BTN_NEUTRAL).pack(side="left", padx=2)
        _btn(btn_row, "Xoá", self._delete, bg=_RED).pack(side="left", padx=2)

        # ── 4. Interactive Gesture Playground ────────────────────────────────
        pg_wrap = tk.Frame(self, bg=theme.BORDER_SUBTLE, padx=1, pady=1)
        pg_wrap.pack(fill="x", padx=4, pady=(0, 4))

        pg = tk.Frame(pg_wrap, bg=theme.BG_SIDEBAR)
        pg.pack(fill="x")

        tk.Label(
            pg, text="Bảng vẽ thử (Giữ chuột phải vẽ vào đây để kiểm tra nhận diện):",
            bg=theme.BG_SIDEBAR, fg=theme.FG_MUTED, font=(font, 9)
        ).pack(anchor="w", padx=8, pady=(4, 2))

        self._canvas = tk.Canvas(
            pg, height=64, bg=theme.BG_WINDOW, highlightthickness=0, cursor="crosshair"
        )
        self._canvas.pack(fill="x", padx=6, pady=(0, 4))

        self._cv_hint = self._canvas.create_text(
            180, 32, text="Giữ chuột phải (RMB) và kéo rê...",
            fill=theme.FG_MUTED, font=(font, 9, "italic")
        )

        self._canvas.bind("<ButtonPress-3>", self._on_pg_down)
        self._canvas.bind("<B3-Motion>", self._on_pg_move)
        self._canvas.bind("<ButtonRelease-3>", self._on_pg_up)

        self._load_items()

    # ── Playground Interaction ───────────────────────────────────────────

    def _on_pg_down(self, event: tk.Event) -> None:
        self._canvas.delete("trail")
        self._test_pts = [(event.x, event.y)]
        self._test_recognizer.reset()
        self._test_recognizer.feed_point(event.x, event.y)
        self._canvas.itemconfigure(self._cv_hint, text="Đang nhận diện...")

    def _on_pg_move(self, event: tk.Event) -> None:
        if not self._test_pts:
            return
        last_x, last_y = self._test_pts[-1]
        self._canvas.create_line(
            last_x, last_y, event.x, event.y,
            fill=_ACC, width=3, capstyle="round", tags="trail"
        )
        self._test_pts.append((event.x, event.y))
        self._test_recognizer.feed_point(event.x, event.y)

    def _on_pg_up(self, event: tk.Event) -> None:
        cfg = config_service.load()
        presets = cfg.get("gestures", [])
        matched = self._test_recognizer.finish(presets)

        dirs = self._test_recognizer._directions
        dir_str = " → ".join(_ARROWS.get(d, d) for d in dirs) if dirs else "Không có hướng"
        txt, clr = (f"✓ Khớp: {dir_str} → [ {matched.get('keys','').upper()} ]", _GRN) if matched else (f"✗ Cử chỉ: {dir_str} (Chưa gán)", theme.FG_MUTED)

        self._canvas.itemconfigure(self._cv_hint, text=txt, fill=clr)
        self.after(3000, lambda: self._canvas.delete("trail"))

    # ── Item CRUD ────────────────────────────────────────────────────────

    def _load_items(self) -> None:
        self._lb.delete(0, "end")
        cfg = config_service.load()
        for i, g in enumerate(cfg.get("gestures", [])):
            dirs = g.get("directions", [])
            arrow_badge = _format_directions(dirs)
            keys = g.get("keys", "").upper()
            enabled = g.get("enabled", True)
            status = "● Bật" if enabled else "○ Tắt"

            line = f"  {arrow_badge:<12}  {','.join(dirs):<8}  →  Phím: {keys:<14}  {status}"
            self._lb.insert("end", line)
            self._lb.itemconfigure(i, foreground=theme.FG_PRIMARY if enabled else theme.FG_MUTED)

    def _toggle(self) -> None:
        sel = self._lb.curselection()
        if not sel: return
        idx = sel[0]
        cfg = config_service.load()
        gestures = cfg.get("gestures", [])
        if 0 <= idx < len(gestures):
            gestures[idx]["enabled"] = not gestures[idx].get("enabled", True)
            config_service.save(cfg)
            self._load_items()
            self._lb.selection_set(idx)
            if self._on_saved: self._on_saved()

    def _delete(self) -> None:
        sel = self._lb.curselection()
        if not sel: return
        idx = sel[0]
        cfg = config_service.load()
        gestures = cfg.get("gestures", [])
        if 0 <= idx < len(gestures):
            gestures.pop(idx)
            config_service.save(cfg)
            self._load_items()
            if self._on_saved: self._on_saved()

    def _edit(self) -> None:
        if self._dialog_open: return
        sel = self._lb.curselection()
        if not sel: return
        idx = sel[0]
        cfg = config_service.load()
        gestures = cfg.get("gestures", [])
        if not (0 <= idx < len(gestures)): return

        self._dialog_open = True
        try:
            parent_win = self.winfo_toplevel()
            keys = KeyRecorderDialog.ask(parent_win, init=gestures[idx].get("keys", ""))
            if keys is not None:
                gestures[idx]["keys"] = keys.strip().lower()
                config_service.save(cfg)
                self._load_items()
                self._lb.selection_set(idx)
                if self._on_saved: self._on_saved()
        finally:
            self._dialog_open = False

    def _add(self) -> None:
        if self._dialog_open: return
        self._dialog_open = True
        try:
            parent_win = self.winfo_toplevel()
            dirs_str = _AskDialog.ask(
                parent_win, "Thêm cử chỉ",
                "Các hướng di chuyển (cách nhau bởi dấu phẩy):",
                init="D,R", hint="Hướng: U (Lên), D (Xuống), L (Trái), R (Phải)",
            )
            if not dirs_str: return
            directions = [d.strip().upper() for d in dirs_str.split(",") if d.strip()]
            if not directions: return
            keys = KeyRecorderDialog.ask(parent_win)
            if not keys: return

            cfg = config_service.load()
            gestures = cfg.get("gestures", [])
            gestures.append({"directions": directions, "keys": keys.strip().lower(), "enabled": True})
            cfg["gestures"] = gestures
            config_service.save(cfg)
            self._load_items()
            self._lb.selection_set("end")
            if self._on_saved: self._on_saved()
        finally:
            self._dialog_open = False
