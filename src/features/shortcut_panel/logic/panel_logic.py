from __future__ import annotations

import ctypes
import logging
import threading
import time
from typing import Callable

_log = logging.getLogger("mousehotkey")
_log.setLevel(logging.DEBUG)
_fh = logging.FileHandler(r"C:\dev\Mousehotkey\debug.log", mode="w", encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s.%(msecs)03d  %(message)s", datefmt="%H:%M:%S"))
_log.addHandler(_fh)

from ..services import config_service, shortcut_executor, window_service
from ..types.panel_types import (
    ActionItem, AppItem, FolderItem, MenuItem, NavState, ShortcutItem, UrlItem,
)


class PanelLogic:
    """Navigation state machine for the shortcut panel."""

    def __init__(self) -> None:
        self._root:  list[MenuItem] = []
        self._items: list[MenuItem] = []
        self._stack: list[tuple[list[MenuItem], int]] = []
        self._index: int  = 0
        self.visible: bool = False
        self.paused:  bool = False          # when True, show() is a no-op
        self._prev_hwnd: int = 0
        self._active_profile: str = "Default"

        # Callbacks set by callers
        self.on_show:          Callable | None = None
        self.on_hide:          Callable | None = None
        self.on_update:        Callable | None = None
        self.on_open_settings: Callable | None = None   # open settings window
        self.on_pause_changed: Callable[[bool], None] | None = None  # pause toggled

        self.reload()

    # ── public API ────────────────────────────────────────────────────────

    def reload(self) -> None:
        data = config_service.load()
        default_raw = data.get("default", data.get("shortcuts", []))
        self._root = config_service.parse_items(default_raw)

    def show(self) -> None:
        if self.paused:
            return
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        self._prev_hwnd = hwnd

        data = config_service.load()
        exe, title, class_name = window_service.get_hwnd_info(hwnd)
        profile_name, raw = config_service.resolve_profile(exe, title, class_name, data)
        self._active_profile = profile_name
        self._root = config_service.parse_items(raw)

        _log.debug(
            f"show()  hwnd={hwnd:#010x}  exe={exe!r}  "
            f"profile={profile_name!r}  items={len(self._root)}"
        )
        self._items = list(self._root)
        self._stack = []
        self._index = 0
        self.visible = True
        if self.on_show:
            self.on_show()

    def hide(self) -> None:
        self.visible = False
        if self.on_hide:
            self.on_hide()

    def navigate(self, delta: int) -> None:
        if not self.visible or not self._items:
            return
        self._index = (self._index + delta) % len(self._items)
        if self.on_update:
            self.on_update()

    def select_at(self, index: int) -> None:
        self._index = index
        self.select_current()

    def select_current(self) -> None:
        if not self.visible or not self._items:
            return
        item = self._items[self._index]

        if isinstance(item, FolderItem):
            self._stack.append((self._items, self._index))
            self._items = list(item.children)
            self._index = 0
            if self.on_update:
                self.on_update()
            return

        if isinstance(item, ActionItem):
            self._handle_action(item.action)
            return

        # For items that need focus restore + delay
        hwnd = self._prev_hwnd
        _log.debug(f"select_current()  type={item.type}  hwnd={hwnd:#010x}")
        if hwnd:
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        self.hide()

        if isinstance(item, ShortcutItem):
            threading.Timer(0.25, self._fire, args=[item.keys]).start()
        elif isinstance(item, AppItem):
            threading.Timer(0.1, shortcut_executor.execute_app,
                            args=[item.path, item.args]).start()
        elif isinstance(item, UrlItem):
            threading.Timer(0.1, shortcut_executor.execute_url,
                            args=[item.url]).start()

    def _handle_action(self, action: str) -> None:
        self.hide()
        if action == "open_settings":
            if self.on_open_settings:
                self.on_open_settings()
        elif action == "toggle_pause":
            self.paused = not self.paused
            _log.debug(f"toggle_pause → paused={self.paused}")
            if self.on_pause_changed:
                self.on_pause_changed(self.paused)

    def _fire(self, keys: str) -> None:
        fg = ctypes.windll.user32.GetForegroundWindow()
        _log.debug(f"_fire()  current FG={fg:#010x}  keys={keys!r}")
        shortcut_executor.execute(keys)

    def go_back(self) -> None:
        if not self._stack:
            self.hide()
            return
        self._items, self._index = self._stack.pop()
        if self.on_update:
            self.on_update()

    # ── read-only snapshot ────────────────────────────────────────────────

    @property
    def active_profile(self) -> str:
        return self._active_profile

    @property
    def state(self) -> NavState:
        crumbs = [items[idx].label for items, idx in self._stack]
        return NavState(items=self._items, breadcrumb=crumbs, index=self._index)
