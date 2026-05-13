"""Default tab — shortcut/folder/app/url listbox with full CRUD."""
from __future__ import annotations

import tkinter as tk
import tkinter.filedialog as fd
from typing import TYPE_CHECKING

from ..services import config_service
from .ask_dialog import _AskDialog, _btn
from .key_recorder_dialog import KeyRecorderDialog
from features.i18n import t, ui_font

if TYPE_CHECKING:
    from ..logic.panel_logic import PanelLogic

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_RED = "#c0392b"
_GRN = "#16825d"


class DefaultTab(tk.Frame):
    """Listbox + CRUD buttons for the Default shortcuts list."""

    def __init__(self, parent: tk.Widget, logic: PanelLogic) -> None:
        super().__init__(parent, bg=_BG)
        self._logic = logic
        self._build()
        self._refresh()

    # ── build ─────────────────────────────────────────────────────────────

    def _build(self) -> None:
        lf = tk.Frame(self, bg=_BG2)
        lf.pack(side="left", fill="both", expand=True)

        self._lb = tk.Listbox(lf, bg=_BG2, fg=_FG, font=(ui_font(), 11),
                              selectbackground=_ACC, relief="flat", bd=0,
                              activestyle="none")
        sb = tk.Scrollbar(lf, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._lb.pack(fill="both", expand=True, padx=4, pady=4)
        self._lb.bind("<Double-Button-1>", lambda _: self._edit())

        bf = tk.Frame(self, bg=_BG)
        bf.pack(side="right", padx=(8, 0), anchor="n", pady=4)
        for txt, cmd, c in [
            (t("btn.shortcut"), self._add_shortcut,    _ACC),
            (t("btn.app"),      self._add_app,          _ACC),
            (t("btn.url"),      self._add_url,          _ACC),
            (t("btn.folder"),   self._add_folder,       _ACC),
            (t("btn.edit"),     self._edit,             "#404040"),
            (t("btn.delete"),   self._delete,           _RED),
            (t("btn.up"),       lambda: self._move(-1), "#404040"),
            (t("btn.down"),     lambda: self._move(1),  "#404040"),
            ("⬇ Import",        self._import,           _GRN),
        ]:
            _btn(bf, txt, cmd, c).pack(fill="x", pady=2)

    # ── helpers ───────────────────────────────────────────────────────────

    def _ask(self, *a, **kw) -> str | None:
        return _AskDialog.ask(self.winfo_toplevel(), *a, **kw)

    def _record_keys(self, init: str = "") -> str | None:
        return KeyRecorderDialog.ask(self.winfo_toplevel(), init)

    def _sel(self) -> int | None:
        s = self._lb.curselection()
        return s[0] if s else None

    def refresh(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        self._lb.delete(0, "end")
        for i, it in enumerate(config_service.load().get("default", [])):
            t = it.get("type", "shortcut")
            if t == "folder":
                n = len(it.get("children", []))
                self._lb.insert("end", f"  {it['label']}  ({n} items)")
                self._lb.itemconfigure(i, foreground="#4ec9b0")
            elif t == "app":
                self._lb.insert("end", f"  🚀  {it['label']}   →   {it.get('path','')}")
                self._lb.itemconfigure(i, foreground="#c586c0")
            elif t == "url":
                self._lb.insert("end", f"  🌐  {it['label']}   →   {it.get('url','')}")
                self._lb.itemconfigure(i, foreground="#4fc1ff")
            elif t == "action":
                self._lb.insert("end", f"  ⚡  {it['label']}")
                self._lb.itemconfigure(i, foreground="#dcdcaa")
            else:
                self._lb.insert("end",
                    f"  ⌨  {it['label']}   →   {it.get('keys', '')}")

    # ── CRUD ──────────────────────────────────────────────────────────────

    def _add_shortcut(self) -> None:
        label = self._ask(t("dlg.add_shortcut"), t("dlg.display_name"))
        if not label:
            return
        keys = self._record_keys()
        if keys is None:
            return
        data = config_service.load()
        data.setdefault("default", []).append(
            {"type": "shortcut", "label": label, "keys": keys})
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _add_app(self) -> None:
        label = self._ask(t("dlg.add_app"), t("dlg.display_name"))
        if not label:
            return
        path = fd.askopenfilename(
            parent=self.winfo_toplevel(),
            title=t("dlg.select_exe"),
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if not path:
            return
        data = config_service.load()
        data.setdefault("default", []).append(
            {"type": "app", "label": label, "path": path, "args": ""})
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _add_url(self) -> None:
        label = self._ask(t("dlg.add_url"), t("dlg.display_name"))
        if not label:
            return
        url = self._ask(t("dlg.add_url"), t("dlg.url"), hint=t("dlg.url_hint"))
        if not url:
            return
        data = config_service.load()
        data.setdefault("default", []).append(
            {"type": "url", "label": label, "url": url})
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _add_folder(self) -> None:
        label = self._ask(t("dlg.add_folder"), t("dlg.folder_name"))
        if not label:
            return
        data = config_service.load()
        data.setdefault("default", []).append(
            {"type": "folder", "label": f"📁 {label}", "children": []})
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _edit(self) -> None:
        idx = self._sel()
        if idx is None:
            return
        data = config_service.load()
        item = data["default"][idx]
        itype = item.get("type", "shortcut")
        if itype == "folder":
            from .folder_editor_dialog import FolderEditorDialog
            FolderEditorDialog(self.winfo_toplevel(), idx, self._logic)
            self._refresh()
            return
        if itype == "action":
            return  # built-in actions are not editable
        label = self._ask(t("dlg.edit"), t("dlg.display_name"),
                          init=item.get("label", ""))
        if label is None:
            return
        item["label"] = label
        if itype == "app":
            path = fd.askopenfilename(
                parent=self.winfo_toplevel(), title=t("dlg.select_exe"),
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
                initialfile=item.get("path", ""),
            )
            if path:
                item["path"] = path
        elif itype == "url":
            url = self._ask(t("dlg.edit_url"), t("dlg.url"),
                            init=item.get("url", ""))
            if url is None:
                return
            item["url"] = url
        else:
            keys = self._record_keys(init=item.get("keys", ""))
            if keys is None:
                return
            item["keys"] = keys
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _delete(self) -> None:
        idx = self._sel()
        if idx is None:
            return
        data = config_service.load()
        data["default"].pop(idx)
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _import(self) -> None:
        from .import_dialog import ImportDialog
        ImportDialog.open(self.winfo_toplevel())
        self._refresh()
        self._logic.reload()

    def _move(self, delta: int) -> None:
        idx = self._sel()
        if idx is None:
            return
        data  = config_service.load()
        items = data.get("default", [])
        new   = idx + delta
        if 0 <= new < len(items):
            items[idx], items[new] = items[new], items[idx]
            config_service.save(data)
            self._refresh()
            self._lb.selection_set(new)
            self._logic.reload()
