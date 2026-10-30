"""Gate + direction logic for the Shift+Scroll browser-tab-switch gesture."""
from __future__ import annotations

import ctypes

from ..services import hotkey_service
from ...shortcut_panel.services import window_service
from ..types.mouse_mapper_types import ScrollDirection

VK_SHIFT = 0x10

CHROMIUM_EXES = {"chrome.exe", "msedge.exe", "brave.exe", "opera.exe", "vivaldi.exe"}

_user32 = ctypes.windll.user32


def is_chromium_browser(exe_basename: str) -> bool:
    """True if exe_basename (case-insensitive) is a known Chromium-based browser."""
    return exe_basename.lower() in CHROMIUM_EXES


def resolve_tab_direction(scroll_dir: ScrollDirection) -> bool:
    """True = forward/next tab (UP), False = backward/previous tab (DOWN)."""
    return scroll_dir == ScrollDirection.UP


def _shift_held() -> bool:
    return bool(_user32.GetAsyncKeyState(VK_SHIFT) & 0x8000)


def handle_scroll_for_tab_switch(scroll_dir: ScrollDirection) -> bool:
    """Called from mouse_hook_service on every WM_MOUSEWHEEL, BEFORE the normal
    on_event dispatch. Returns True if this tick was consumed (gesture fired —
    caller must suppress the event), False to let normal dispatch proceed."""
    if not _shift_held():
        return False
    hwnd = _user32.GetForegroundWindow()
    exe, _title, _cls = window_service.get_hwnd_info(hwnd)
    if not is_chromium_browser(exe):
        return False
    hotkey_service.switch_tab(resolve_tab_direction(scroll_dir))
    return True
