"""Modal dialog for editing shortcuts/apps/urls inside a folder item."""
from __future__ import annotations

import tkinter as tk
import tkinter.filedialog as fd

from ..services import config_service
from .ask_dialog import _AskDialog, _btn
from .key_recorder_dialog import KeyRecorderDialog
from features.i18n import t, ui_font

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_RED = "#c0392b"
_SAV = "#16825d"
_CMD = "#6a5acd"


class FolderEditorDialog:
    """Toplevel for managing items inside a single folder."""

    def __init__(self, parent: tk.Widget, folder_idx: int, logic) -> None:
        self._idx   = folder_idx
        self._logic = logic

        self._win = tk.Toplevel(parent)
        self._win.configure(bg=_BG)
        self._win.resizable(False, False)
        self._win.grab_set()
        self._win.attributes("-topmost", True)
        self._build()
        parent.wait_window(self._win)

    def _build(self) -> None:
        w    = self._win
        font = ui_font()
        folder_label = config_service.load()["default"][self._idx].get("label", "Folder")
        w.title(t("folder.title", label=folder_label))
        w.geometry("480x420")

        tk.Label(w, text=t("folder.subtitle", label=folder_label),
                 bg=_BG, fg=_FG, font=(font, 10, "bold")).pack(
                 anchor="w", padx=14, pady=(12, 4))

        body = tk.Frame(w, bg=_BG)
        body.pack(fill="both", expand=True, padx=14, pady=4)

        lf = tk.Frame(body, bg=_BG2)
        lf.pack(side="left", fill="both", expand=True)
        self._lb = tk.Listbox(lf, bg=_BG2, fg=_FG, font=(font, 11),
                              selectbackground=_ACC, relief="flat", bd=0,
                              activestyle="none")
        sb = tk.Scrollbar(lf, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._lb.pack(fill="both", expand=True, padx=4, pady=4)
        self._lb.bind("<Double-Button-1>", lambda _: self._edit())

        bf = tk.Frame(body, bg=_BG)
        bf.pack(side="right", padx=(8, 0), anchor="n")
        for txt, cmd, c in [
            (t("btn.shortcut"), self._add_shortcut,    _ACC),
            (t("btn.app"),      self._add_app,          _ACC),
            (t("btn.url"),      self._add_url,          _ACC),
            ("▶ Command",       self._add_command,      _CMD),
            (t("btn.edit"),     self._edit,             "#404040"),
            (t("btn.del"),      self._delete,           _RED),
            (t("btn.up"),       lambda: self._move(-1), "#404040"),
            (t("btn.down"),     lambda: self._move(1),  "#404040"),
        ]:
            _btn(bf, txt, cmd, c).pack(fill="x", pady=2)

        self._refresh()
        _btn(w, t("btn.done"), self._win.destroy, _SAV).pack(pady=10)

    # ── helpers ───────────────────────────────────────────────────────────

    def _ask(self, *a, **kw) -> str | None:
        return _AskDialog.ask(self._win, *a, **kw)

    def _record_keys(self, init: str = "") -> str | None:
        return KeyRecorderDialog.ask(self._win, init)

    def _children(self) -> list:
        return config_service.load()["default"][self._idx].get("children", [])

    def _sel(self) -> int | None:
        s = self._lb.curselection()
        return s[0] if s else None

    def _refresh(self) -> None:
        self._lb.delete(0, "end")
        for i, ch in enumerate(self._children()):
            ctype = ch.get("type", "shortcut")
            if ctype == "app":
                self._lb.insert("end",
                    f"  🚀  {ch.get('label','')}   →   {ch.get('path','')}")
                self._lb.itemconfigure(i, foreground="#c586c0")
            elif ctype == "url":
                self._lb.insert("end",
                    f"  🌐  {ch.get('label','')}   →   {ch.get('url','')}")
                self._lb.itemconfigure(i, foreground="#4fc1ff")
            elif ctype == "command":
                self._lb.insert("end",
                    f"  ▶  {ch.get('label','')}   →   {ch.get('cmd','')}")
                self._lb.itemconfigure(i, foreground="#ce9178")
            else:
                self._lb.insert("end",
                    f"  ⌨  {ch.get('label','')}   →   {ch.get('keys','')}")

    # ── CRUD ─────────────────────────────────────────────────────────────

    def _add_shortcut(self) -> None:
        label = self._ask(t("dlg.add_shortcut"), t("dlg.display_name"))
        if not label:
            return
        keys = self._record_keys()
        if keys is None:
            return
        data = config_service.load()
        data["default"][self._idx]["children"].append(
            {"type": "shortcut", "label": label, "keys": keys})
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _add_app(self) -> None:
        label = self._ask(t("dlg.add_app"), t("dlg.display_name"))
        if not label:
            return
        path = fd.askopenfilename(
            parent=self._win, title=t("dlg.select_exe"),
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if not path:
            return
        data = config_service.load()
        data["default"][self._idx]["children"].append(
            {"type": "app", "label": label, "path": path, "args": ""})
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _add_url(self) -> None:
        label = self._ask(t("dlg.add_url"), t("dlg.display_name"))
        if not label:
            return
        url = self._ask(t("dlg.add_url"), t("dlg.url"),
                        hint=t("dlg.url_hint"))
        if not url:
            return
        data = config_service.load()
        data["default"][self._idx]["children"].append(
            {"type": "url", "label": label, "url": url})
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _add_command(self) -> None:
        label = self._ask("Add Command", "Display name")
        if not label:
            return
        cmd = self._ask("Add Command", "Shell command",
                        hint="e.g. cd C:\\projects && git pull")
        if not cmd:
            return
        data = config_service.load()
        data["default"][self._idx]["children"].append(
            {"type": "command", "label": label, "cmd": cmd, "cwd": ""})
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _edit(self) -> None:
        idx = self._sel()
        if idx is None:
            return
        data  = config_service.load()
        ch    = data["default"][self._idx]["children"][idx]
        ctype = ch.get("type", "shortcut")
        label = self._ask(t("dlg.edit"), t("dlg.display_name"),
                          init=ch.get("label", ""))
        if label is None:
            return
        ch["label"] = label
        if ctype == "app":
            path = fd.askopenfilename(
                parent=self._win, title=t("dlg.select_exe"),
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            )
            if path:
                ch["path"] = path
        elif ctype == "url":
            url = self._ask(t("dlg.edit_url"), t("dlg.url"),
                            init=ch.get("url", ""))
            if url is None:
                return
            ch["url"] = url
        elif ctype == "command":
            cmd = self._ask("Edit Command", "Shell command",
                            init=ch.get("cmd", ""),
                            hint="e.g. cd C:\\projects && git pull")
            if cmd is None:
                return
            ch["cmd"] = cmd
        else:
            keys = self._record_keys(init=ch.get("keys", ""))
            if keys is None:
                return
            ch["keys"] = keys
        config_service.save(data); self._refresh(); self._logic.reload()

    def _delete(self) -> None:
        idx = self._sel()
        if idx is None:
            return
        data = config_service.load()
        data["default"][self._idx]["children"].pop(idx)
        config_service.save(data); self._refresh(); self._logic.reload()

    def _move(self, delta: int) -> None:
        idx = self._sel()
        if idx is None:
            return
        data = config_service.load()
        ch   = data["default"][self._idx]["children"]
        new  = idx + delta
        if 0 <= new < len(ch):
            ch[idx], ch[new] = ch[new], ch[idx]
            config_service.save(data); self._refresh()
            self._lb.selection_set(new); self._logic.reload()
