"""Modal dialog for managing mouse gesture presets."""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from ..services import config_service
from .ask_dialog import _AskDialog, _btn
from features.i18n import t, ui_font

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_RED = "#c0392b"


class GestureSettingsDialog:
    """Toplevel dialog for managing mouse gesture presets."""

    def __init__(self, parent: tk.Widget, on_saved: Callable | None = None) -> None:
        self._on_saved = on_saved
        self._win = tk.Toplevel(parent)
        self._win.title(t("tray.gestures"))
        self._win.geometry("500x380")
        self._win.configure(bg=_BG)
        self._win.resizable(False, False)
        self._win.grab_set()
        self._win.attributes("-topmost", True)
        self._build()
        parent.wait_window(self._win)

    def _build(self) -> None:
        w = self._win
        font = ui_font()

        tk.Label(
            w, text="Chuột phải + Kéo theo hướng để kích hoạt phím tắt",
            bg=_BG, fg=_FG, font=(font, 10, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 4))

        body = tk.Frame(w, bg=_BG)
        body.pack(fill="both", expand=True, padx=14, pady=4)

        lf = tk.Frame(body, bg=_BG2)
        lf.pack(side="left", fill="both", expand=True)
        self._lb = tk.Listbox(
            lf, bg=_BG2, fg=_FG, font=(font, 10),
            selectbackground=_ACC, relief="flat", bd=0, activestyle="none"
        )
        sb = tk.Scrollbar(lf, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._lb.pack(fill="both", expand=True, padx=4, pady=4)
        self._lb.bind("<Double-Button-1>", lambda _: self._toggle())

        bf = tk.Frame(body, bg=_BG)
        bf.pack(side="right", padx=(8, 0), anchor="n")
        _btn(bf, "Thêm", self._add, bg=_ACC).pack(fill="x", pady=2)
        _btn(bf, "Bật/Tắt", self._toggle, bg="#404040").pack(fill="x", pady=2)
        _btn(bf, "Xoá", self._delete, bg=_RED).pack(fill="x", pady=2)
        _btn(bf, "Đóng", self._win.destroy, bg="#333333").pack(fill="x", pady=(12, 2))

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

    def _add(self) -> None:
        dirs_str = _AskDialog.ask(
            self._win, "Thêm cử chỉ", "Các hướng di chuyển (cách nhau bởi dấu phẩy):",
            init="D,R", hint="Các hướng: U, D, L, R, UR, DR, DL, UL"
        )
        if not dirs_str:
            return
        directions = [d.strip().upper() for d in dirs_str.split(",") if d.strip()]
        if not directions:
            return

        keys = _AskDialog.ask(
            self._win, "Phím tắt", "Tổ hợp phím tắt cần gửi:",
            init="ctrl+w", hint="Ví dụ: ctrl+w, ctrl+t, alt+f4"
        )
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
