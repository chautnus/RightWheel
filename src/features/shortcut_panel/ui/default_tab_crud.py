"""CRUD mixin for DefaultTab — add/edit/delete/move/import handlers."""
from __future__ import annotations

import tkinter.filedialog as fd

from ..services import config_service
from features.i18n import t


class _DefaultTabCRUDMixin:
    """Mixin containing CRUD event handlers for DefaultTab."""

    def _add_shortcut(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            from .intent_picker_dialog import IntentPickerDialog
            intent = IntentPickerDialog.ask(self.winfo_toplevel())
            if intent:
                label = intent.title_vi
                keys = intent.keys
            else:
                label = self._ask(t("dlg.add_shortcut"), t("dlg.display_name"))
                if not label:
                    return
                keys = self._record_keys()
                if keys is None:
                    return
            data = config_service.load()
            data.setdefault("default", []).append({"type": "shortcut", "label": label, "keys": keys})
            config_service.save(data)
            self._refresh(); self._logic.reload()
        finally:
            self._dialog_open = False

    def _add_app(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
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
            data.setdefault("default", []).append({"type": "app", "label": label, "path": path, "args": ""})
            config_service.save(data)
            self._refresh(); self._logic.reload()
        finally:
            self._dialog_open = False

    def _add_url(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            label = self._ask(t("dlg.add_url"), t("dlg.display_name"))
            if not label:
                return
            url = self._ask(t("dlg.add_url"), t("dlg.url"), hint=t("dlg.url_hint"))
            if not url:
                return
            data = config_service.load()
            data.setdefault("default", []).append({"type": "url", "label": label, "url": url})
            config_service.save(data)
            self._refresh(); self._logic.reload()
        finally:
            self._dialog_open = False

    def _add_folder(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            label = self._ask(t("dlg.add_folder"), t("dlg.folder_name"))
            if not label:
                return
            data = config_service.load()
            data.setdefault("default", []).append(
                {"type": "folder", "label": f"📁 {label}", "children": []})
            config_service.save(data)
            self._refresh(); self._logic.reload()
        finally:
            self._dialog_open = False

    def _edit(self) -> None:
        if self._dialog_open:
            return
        idx = self._sel()
        if idx is None:
            return
        data = config_service.load()
        item = data["default"][idx]
        itype = item.get("type", "shortcut")
        if itype == "folder":
            self._dialog_open = True
            try:
                from .folder_editor_dialog import FolderEditorDialog
                FolderEditorDialog(self.winfo_toplevel(), idx, self._logic)
                self._refresh()
            finally:
                self._dialog_open = False
            return
        if itype == "action":
            return  # built-in actions are not editable
        if itype == "sequence":
            self._dialog_open = True
            try:
                new_label = self._ask(t("dlg.edit"), t("dlg.display_name"), init=item.get("label", ""))
                if new_label is not None:
                    item["label"] = new_label
                    config_service.save(data)
                    self._refresh()
                from .sequence_editor_dialog import SequenceEditorDialog
                SequenceEditorDialog(
                    self.winfo_toplevel(),
                    init_steps=item.get("steps", []),
                    on_saved=lambda new_steps, i=idx: self._save_edited_sequence(i, new_steps),
                )
            finally:
                self._dialog_open = False
            return
        self._dialog_open = True
        try:
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
        finally:
            self._dialog_open = False

    def _delete(self) -> None:
        idx = self._sel()
        if idx is None:
            return
        data = config_service.load()
        data["default"].pop(idx)
        config_service.save(data)
        self._refresh(); self._logic.reload()

    def _add_command(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            label = self._ask("Add Command", "Display name")
            if not label:
                return
            cmd = self._ask("Add Command", "Shell command",
                            hint="e.g. cd C:\\projects && git pull")
            if not cmd:
                return
            data = config_service.load()
            data.setdefault("default", []).append(
                {"type": "command", "label": label, "cmd": cmd, "cwd": ""})
            config_service.save(data)
            self._refresh(); self._logic.reload()
        finally:
            self._dialog_open = False

    def _add_sequence(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            label = self._ask("Add Sequence", "Display name")
            if not label:
                return
            from .sequence_editor_dialog import SequenceEditorDialog
            SequenceEditorDialog(
                self.winfo_toplevel(),
                on_saved=lambda steps: self._save_new_sequence(label, steps),
            )
        finally:
            self._dialog_open = False

    def _save_new_sequence(self, label: str, steps: list[dict]) -> None:
        data = config_service.load()
        data.setdefault("default", []).append({"type": "sequence", "label": label, "steps": steps})
        config_service.save(data)
        self._refresh()
        self._logic.reload()

    def _save_edited_sequence(self, idx: int, steps: list[dict]) -> None:
        data = config_service.load()
        items = data.get("default", [])
        if 0 <= idx < len(items):
            items[idx]["steps"] = steps
        config_service.save(data)
        self._refresh()
        self._logic.reload()

    def _import(self) -> None:
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            from .import_dialog import ImportDialog
            ImportDialog.open(self.winfo_toplevel())
            self._refresh()
            self._logic.reload()
        finally:
            self._dialog_open = False

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
