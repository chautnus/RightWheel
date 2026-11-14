"""Gestures tab frame for managing mouse gesture presets within SettingsWindow."""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from ..services import config_service
from .ask_dialog import _AskDialog, _btn
from .key_recorder_dialog import KeyRecorderDialog
from . import theme
from features.i18n import t, ui_font

_BG  = theme.BG_CONTENT
_BG2 = theme.BG_CARD
_FG  = theme.FG_SECONDARY
_ACC = theme.ACCENT_BLUE
_RED = theme.COLOR_DANGER
_BTN_NEUTRAL = theme.BORDER_INPUT


class GesturesTab(tk.Frame):
    """Tab frame for managing mouse gesture presets."""

    def __init__(self, parent: tk.Widget, on_saved: Callable | None = None) -> None:
        super().__init__(parent, bg=_BG)
        self._on_saved = on_saved
        self._dialog_open = False
        self._build()

    def _build(self) -> None:
        font = ui_font()

        tk.Label(
            self,
            text="Chuột phải + Kéo theo hướng để kích hoạt phím tắt",
            bg=_BG,
            fg=_FG,
            font=(font, 10, "bold"),
        ).pack(anchor="w", padx=4, pady=(4, 4))

        body = tk.Frame(self, bg=_BG)
        body.pack(fill="both", expand=True, padx=4, pady=4)

        lf = tk.Frame(body, bg=_BG2)
        lf.pack(side="left", fill="both", expand=True)
        self._lb = tk.Listbox(
            lf,
            bg=_BG2,
            fg=_FG,
            font=(font, 10),
            selectbackground=_ACC,
            relief="flat",
            bd=0,
            activestyle="none",
        )
        sb = tk.Scrollbar(lf, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._lb.pack(fill="both", expand=True, padx=4, pady=4)

        bf = tk.Frame(body, bg=_BG)
        bf.pack(side="right", padx=(8, 0), anchor="n")
        _btn(bf, "Thêm", self._add, bg=_ACC).pack(fill="x", pady=2)
        _btn(bf, "Sửa", self._edit, bg=_BTN_NEUTRAL).pack(fill="x", pady=2)
        _btn(bf, "Bật/Tắt", self._toggle, bg=_BTN_NEUTRAL).pack(fill="x", pady=2)
        _btn(bf, "Xoá", self._delete, bg=_RED).pack(fill="x", pady=2)

        self._load_items()

    def _load_items(self) -> None:
        self._lb.delete(0, "end")
        cfg = config_service.load()
        for g in cfg.get("gestures", []):
            dirs = ",".join(g.get("directions", []))
            keys = g.get("keys", "")
            status = "Bật" if g.get("enabled", True) else "Tắt"
            self._lb.insert("end", f"Hướng [{dirs}] → Phím [{keys}] ({status})")

    def _toggle(self) -> None:
        sel = self._lb.curselection()
        if not sel:
            return
        idx = sel[0]
        cfg = config_service.load()
        gestures = cfg.get("gestures", [])
        if 0 <= idx < len(gestures):
            gestures[idx]["enabled"] = not gestures[idx].get("enabled", True)
            config_service.save(cfg)
            self._load_items()
            self._lb.selection_set(idx)
            if self._on_saved:
                self._on_saved()

    def _delete(self) -> None:
        sel = self._lb.curselection()
        if not sel:
            return
        idx = sel[0]
        cfg = config_service.load()
        gestures = cfg.get("gestures", [])
        if 0 <= idx < len(gestures):
            gestures.pop(idx)
            config_service.save(cfg)
            self._load_items()
            if self._on_saved:
                self._on_saved()

    def _edit(self) -> None:
        if self._dialog_open:
            return
        sel = self._lb.curselection()
        if not sel:
            return
        idx = sel[0]
        cfg = config_service.load()
        gestures = cfg.get("gestures", [])
        if not (0 <= idx < len(gestures)):
            return

        self._dialog_open = True
        try:
            parent_win = self.winfo_toplevel()
            keys = KeyRecorderDialog.ask(parent_win, init=gestures[idx].get("keys", ""))
            if keys is not None:
                gestures[idx]["keys"] = keys.strip().lower()
                config_service.save(cfg)
                self._load_items()
                self._lb.selection_set(idx)
                if self._on_saved:
                    self._on_saved()
        finally:
            self._dialog_open = False

    def _add(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            parent_win = self.winfo_toplevel()
            dirs_str = _AskDialog.ask(
                parent_win,
                "Thêm cử chỉ",
                "Các hướng di chuyển (cách nhau bởi dấu phẩy):",
                init="D,R",
                hint="Các hướng: U, D, L, R, UR, DR, DL, UL",
            )
            if not dirs_str:
                return
            directions = [d.strip().upper() for d in dirs_str.split(",") if d.strip()]
            if not directions:
                return

            keys = KeyRecorderDialog.ask(parent_win)
            if not keys:
                return

            cfg = config_service.load()
            gestures = cfg.get("gestures", [])
            gestures.append({
                "directions": directions,
                "keys": keys.strip().lower(),
                "enabled": True,
            })
            cfg["gestures"] = gestures
            config_service.save(cfg)
            self._load_items()
            self._lb.selection_set("end")
            if self._on_saved:
                self._on_saved()
        finally:
            self._dialog_open = False
