"""Per-step-type parameter dialogs for SequenceEditorDialog (add + edit share these)."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from .ask_dialog import _AskDialog
from .key_recorder_dialog import KeyRecorderDialog


def ask_delay(parent: tk.Widget, initial: int = 100) -> int:
    res = simpledialog.askinteger(
        "Step Delay", "Delay after this step (ms):", initialvalue=initial, minvalue=0, maxvalue=10000, parent=parent
    )
    return initial if res is None else res


def ask_shortcut(parent: tk.Widget, init: dict | None = None) -> dict | None:
    init = init or {}
    keys = KeyRecorderDialog.ask(parent, init=init.get("keys", ""))
    if not keys or not keys.strip():
        return None
    delay = ask_delay(parent, init.get("delay_ms", 100))
    return {"type": "shortcut", "keys": keys.strip(), "delay_ms": delay}


def ask_app(parent: tk.Widget, init: dict | None = None) -> dict | None:
    init = init or {}
    path = filedialog.askopenfilename(
        title="Select App", filetypes=[("Executables", "*.exe"), ("All", "*.*")], parent=parent,
        initialdir=os.path.dirname(init.get("path", "")) or None,
    )
    if not path:
        return None
    args = _AskDialog.ask(parent, "App Args", "Optional arguments:", init=init.get("args", "")) or ""
    delay = ask_delay(parent, init.get("delay_ms", 100))
    return {"type": "app", "path": path, "args": args.strip(), "delay_ms": delay}


def ask_url(parent: tk.Widget, init: dict | None = None) -> dict | None:
    init = init or {}
    url = _AskDialog.ask(parent, "Add Web Step", "URL (e.g. https://google.com):", init=init.get("url", ""))
    if not url or not url.strip():
        return None
    delay = ask_delay(parent, init.get("delay_ms", 100))
    return {"type": "url", "url": url.strip(), "delay_ms": delay}


def ask_command(parent: tk.Widget, init: dict | None = None) -> dict | None:
    init = init or {}
    cmd = _AskDialog.ask(parent, "Add Script Step", "Command (e.g. echo hello):", init=init.get("cmd", ""))
    if not cmd or not cmd.strip():
        return None
    delay = ask_delay(parent, init.get("delay_ms", 100))
    return {"type": "command", "cmd": cmd.strip(), "cwd": init.get("cwd", ""), "delay_ms": delay}


def ask_url_clipboard(parent: tk.Widget, init: dict | None = None) -> dict | None:
    init = init or {}
    template = _AskDialog.ask(
        parent, "Add Web+Clipboard Step",
        "URL template (use {text} for clipboard content):",
        hint="e.g. https://chatgpt.com/?q={text}  —  not guaranteed to work, test yourself",
        init=init.get("url_template", ""),
    )
    if not template or not template.strip():
        return None
    if "{text}" not in template:
        messagebox.showwarning("Missing placeholder", "URL template must contain {text}.", parent=parent)
        return None
    delay = ask_delay(parent, init.get("delay_ms", 100))
    return {"type": "url_clipboard", "url_template": template.strip(), "delay_ms": delay}


def ask_gemini(parent: tk.Widget, init: dict | None = None) -> dict | None:
    init = init or {}
    prompt = _AskDialog.ask(
        parent, "Add Gemini Step",
        "Prompt (clipboard text is appended automatically):",
        hint="e.g. Translate to English:",
        init=init.get("prompt", ""),
    )
    if prompt is None or not prompt.strip():
        return None
    delay = ask_delay(parent, init.get("delay_ms", 100))
    return {"type": "gemini", "prompt": prompt.strip(), "delay_ms": delay}


# Maps step "type" -> (button label, ask function)
STEP_KINDS: dict[str, tuple[str, callable]] = {
    "shortcut":      ("+ Keys", ask_shortcut),
    "app":           ("+ App", ask_app),
    "url":           ("+ Web", ask_url),
    "command":       ("+ Script", ask_command),
    "url_clipboard": ("+ Web (Clip)", ask_url_clipboard),
    "gemini":        ("+ Gemini", ask_gemini),
}
