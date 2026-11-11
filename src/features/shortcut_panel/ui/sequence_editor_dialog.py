"""Modal dialog for editing multi-step Sequence actions."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import Callable

from .ask_dialog import _AskDialog
from .key_recorder_dialog import KeyRecorderDialog

_BG = "#1e1e24"
_FG = "#ffffff"
_FG_MUTED = "#858590"
_BTN_BG = "#2a2a34"
_BTN_HOVER = "#383848"
_ACC = "#0078d4"
_BORDER = "#333340"


class SequenceEditorDialog(tk.Toplevel):
    """Modal dialog for configuring multi-step Sequence actions."""

    def __init__(
        self,
        parent: tk.Widget,
        init_steps: list[dict] | None = None,
        on_saved: Callable[[list[dict]], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self.title("Sequence Editor")
        self.configure(bg=_BG)
        self.resizable(False, False)
        self._steps: list[dict] = [dict(s) for s in (init_steps or [])]
        self._on_saved = on_saved
        self._dialog_open: bool = False

        self._build_ui()
        self._refresh_list()
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.focus_set()

    def _build_ui(self) -> None:
        pad_frame = tk.Frame(self, bg=_BG, padx=14, pady=12)
        pad_frame.pack(fill="both", expand=True)

        tk.Label(
            pad_frame,
            text="Sequence Steps (executed top to bottom):",
            bg=_BG,
            fg=_FG,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        list_frame = tk.Frame(pad_frame, bg=_BG)
        list_frame.pack(fill="both", expand=True)

        self._lb = tk.Listbox(
            list_frame,
            bg="#141418",
            fg=_FG,
            selectbackground=_ACC,
            selectforeground=_FG,
            font=("Segoe UI", 9),
            height=8,
            width=54,
            relief="flat",
            highlightthickness=1,
            highlightbackground=_BORDER,
        )
        self._lb.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(list_frame, orient="vertical", command=self._lb.yview)
        sb.pack(side="right", fill="y")
        self._lb.configure(yscrollcommand=sb.set)

        # Step Actions row
        act_row = tk.Frame(pad_frame, bg=_BG)
        act_row.pack(fill="x", pady=(8, 4))

        self._btn(act_row, "+ Keys", self._step_add_shortcut).pack(side="left", padx=(0, 4))
        self._btn(act_row, "+ App", self._step_add_app).pack(side="left", padx=(0, 4))
        self._btn(act_row, "+ Web", self._step_add_url).pack(side="left", padx=(0, 4))
        self._btn(act_row, "+ Script", self._step_add_command).pack(side="left", padx=(0, 4))
        self._btn(act_row, "Delete", self._step_delete, fg="#ff6b6b").pack(side="left", padx=(4, 0))
        self._btn(act_row, "▲", lambda: self._step_move(-1), width=3).pack(side="left", padx=(4, 2))
        self._btn(act_row, "▼", lambda: self._step_move(1), width=3).pack(side="left", padx=(0, 4))

        # Bottom row: Save / Cancel
        sep = tk.Frame(pad_frame, bg=_BORDER, height=1)
        sep.pack(fill="x", pady=(10, 8))

        bot_row = tk.Frame(pad_frame, bg=_BG)
        bot_row.pack(fill="x")

        self._btn(bot_row, "Cancel", self.destroy).pack(side="right", padx=(4, 0))
        self._btn(bot_row, "Save Sequence", self._save, bg=_ACC, fg=_FG).pack(side="right")

    def _btn(
        self, parent: tk.Widget, text: str, cmd: Callable, bg: str = _BTN_BG, fg: str = _FG, width: int | None = None
    ) -> tk.Button:
        kwargs: dict = dict(
            text=text,
            command=cmd,
            bg=bg,
            fg=fg,
            activebackground=_BTN_HOVER,
            activeforeground=_FG,
            relief="flat",
            font=("Segoe UI", 8, "bold" if bg == _ACC else "normal"),
            padx=8,
            pady=3,
            cursor="hand2",
        )
        if width is not None:
            kwargs["width"] = width
        return tk.Button(parent, **kwargs)

    def _ask_delay(self) -> int:
        res = simpledialog.askinteger(
            "Step Delay", "Delay after this step (ms):", initialvalue=100, minvalue=0, maxvalue=10000, parent=self
        )
        return 100 if res is None else res

    def _step_add_shortcut(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            keys = KeyRecorderDialog.ask(self)
            if keys and keys.strip():
                delay = self._ask_delay()
                self._steps.append({"type": "shortcut", "keys": keys.strip(), "delay_ms": delay})
                self._refresh_list()
        finally:
            self._dialog_open = False

    def _step_add_app(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            path = filedialog.askopenfilename(
                title="Select App", filetypes=[("Executables", "*.exe"), ("All", "*.*")], parent=self
            )
            if path:
                args = _AskDialog.ask(self, "App Args", "Optional arguments:") or ""
                delay = self._ask_delay()
                self._steps.append({"type": "app", "path": path, "args": args.strip(), "delay_ms": delay})
                self._refresh_list()
        finally:
            self._dialog_open = False

    def _step_add_url(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            url = _AskDialog.ask(self, "Add Web Step", "URL (e.g. https://google.com):")
            if url and url.strip():
                delay = self._ask_delay()
                self._steps.append({"type": "url", "url": url.strip(), "delay_ms": delay})
                self._refresh_list()
        finally:
            self._dialog_open = False

    def _step_add_command(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            cmd = _AskDialog.ask(self, "Add Script Step", "Command (e.g. echo hello):")
            if cmd and cmd.strip():
                delay = self._ask_delay()
                self._steps.append({"type": "command", "cmd": cmd.strip(), "cwd": "", "delay_ms": delay})
                self._refresh_list()
        finally:
            self._dialog_open = False

    def _step_delete(self) -> None:
        sel = self._lb.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(self._steps):
            del self._steps[idx]
            self._refresh_list()
            if self._steps:
                new_idx = min(idx, len(self._steps) - 1)
                self._lb.selection_set(new_idx)

    def _step_move(self, delta: int) -> None:
        sel = self._lb.curselection()
        if not sel:
            return
        idx = sel[0]
        target = idx + delta
        if 0 <= target < len(self._steps):
            self._steps[idx], self._steps[target] = self._steps[target], self._steps[idx]
            self._refresh_list()
            self._lb.selection_set(target)

    def _refresh_list(self) -> None:
        self._lb.delete(0, "end")
        for i, step in enumerate(self._steps):
            stype = step.get("type", "shortcut")
            delay = step.get("delay_ms", 100)
            if stype == "shortcut":
                detail = f"Keys: {step.get('keys', '')}"
            elif stype == "app":
                detail = f"App: {step.get('path', '')}"
            elif stype == "url":
                detail = f"Web: {step.get('url', '')}"
            elif stype == "command":
                detail = f"Script: {step.get('cmd', '')}"
            else:
                detail = f"{stype}"
            self._lb.insert("end", f"[{i+1}] {detail}  ({delay}ms)")

    def _save(self) -> None:
        if not self._steps:
            if not messagebox.askyesno("Save Sequence", "Sequence currently has 0 steps. Save anyway?", parent=self):
                return
        if self._on_saved:
            self._on_saved(self._steps)
        self.destroy()
