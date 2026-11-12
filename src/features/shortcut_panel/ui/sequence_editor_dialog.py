"""Modal dialog for editing multi-step Sequence actions."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from . import sequence_step_dialogs as stepdlg

_BG = "#1e1e24"
_FG = "#ffffff"
_FG_MUTED = "#858590"
_BTN_BG = "#2a2a34"
_BTN_HOVER = "#383848"
_ACC = "#0078d4"
_BORDER = "#333340"

_STEP_ORDER = ["shortcut", "app", "url", "command", "url_clipboard", "gemini"]


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
        self._lb.bind("<Double-Button-1>", lambda _e: self._step_edit())

        sb = tk.Scrollbar(list_frame, orient="vertical", command=self._lb.yview)
        sb.pack(side="right", fill="y")
        self._lb.configure(yscrollcommand=sb.set)

        # Step Actions row (one "+ <kind>" button per entry in stepdlg.STEP_KINDS)
        act_row = tk.Frame(pad_frame, bg=_BG)
        act_row.pack(fill="x", pady=(8, 4))
        for stype in _STEP_ORDER:
            label, _ = stepdlg.STEP_KINDS[stype]
            self._btn(act_row, label, lambda t=stype: self._step_add(t)).pack(side="left", padx=(0, 4))

        # Edit / Delete / reorder row
        act_row2 = tk.Frame(pad_frame, bg=_BG)
        act_row2.pack(fill="x", pady=(0, 4))
        self._btn(act_row2, "Edit", self._step_edit).pack(side="left", padx=(0, 4))
        self._btn(act_row2, "Delete", self._step_delete, fg="#ff6b6b").pack(side="left", padx=(4, 0))
        self._btn(act_row2, "▲", lambda: self._step_move(-1), width=3).pack(side="left", padx=(4, 2))
        self._btn(act_row2, "▼", lambda: self._step_move(1), width=3).pack(side="left", padx=(0, 4))

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

    def _step_add(self, stype: str) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            _, ask_fn = stepdlg.STEP_KINDS[stype]
            step = ask_fn(self)
            if step is not None:
                self._steps.append(step)
                self._refresh_list()
        finally:
            self._dialog_open = False

    def _step_edit(self) -> None:
        if self._dialog_open:
            return
        sel = self._lb.curselection()
        if not sel:
            return
        idx = sel[0]
        step = self._steps[idx]
        kind = stepdlg.STEP_KINDS.get(step.get("type", "shortcut"))
        if kind is None:
            messagebox.showwarning("Edit Step", "Unknown step type — delete and re-add instead.", parent=self)
            return
        self._dialog_open = True
        try:
            _, ask_fn = kind
            new_step = ask_fn(self, init=step)
            if new_step is not None:
                self._steps[idx] = new_step
                self._refresh_list()
                self._lb.selection_set(idx)
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
            elif stype == "url_clipboard":
                detail = f"Web+Clip: {step.get('url_template', '')}"
            elif stype == "gemini":
                detail = f"Gemini: {step.get('prompt', '')}"
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
