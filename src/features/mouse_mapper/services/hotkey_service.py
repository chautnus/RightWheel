"""Keystroke + mouse injection via SendInput.

Alt+Tab session:
  begin_switch(forward)   — Alt↓ Tab↓↑  (opens switcher, Alt stays held)
  cycle(forward)          — Tab↓↑        (Alt still held, moves one step)
  end_switch()            — Alt↑         (confirms selection)

Mouse passthrough helpers (all tagged INJECTED_MARKER so our hook skips them):
  inject_right_down()     — retroactive RMB down at current cursor pos (for gestures)
  inject_right_click()    — RMB down+up for context menu passthrough
  inject_right_cleanup()  — orphan RMB up to fix OS button state after SCROLLING
"""
import ctypes
import ctypes.wintypes as wt

INJECTED_MARKER = 0xFEED1234

INPUT_KEYBOARD = 1
INPUT_MOUSE    = 0

KEYEVENTF_KEYUP       = 0x0002
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP   = 0x0010

VK_MENU  = 0x12
VK_TAB   = 0x09
VK_SHIFT = 0x10


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk",         wt.WORD),
        ("wScan",       wt.WORD),
        ("dwFlags",     wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx",          ctypes.c_long),
        ("dy",          ctypes.c_long),
        ("mouseData",   wt.DWORD),
        ("dwFlags",     wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class _INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("ki", _KEYBDINPUT), ("mi", _MOUSEINPUT)]
    _anonymous_ = ("_u",)
    _fields_ = [("type", wt.DWORD), ("_u", _U)]


_SendInput = ctypes.windll.user32.SendInput
_INPUT_SZ  = ctypes.sizeof(_INPUT)
_D, _U_    = 0, KEYEVENTF_KEYUP


def _keys(*pairs: tuple[int, int]) -> None:
    arr = (_INPUT * len(pairs))()
    for i, (vk, flags) in enumerate(pairs):
        arr[i].type = INPUT_KEYBOARD
        arr[i].ki.wVk = vk
        arr[i].ki.dwFlags = flags
    _SendInput(len(pairs), arr, _INPUT_SZ)


def _mouse(*flags_seq: int) -> None:
    arr = (_INPUT * len(flags_seq))()
    for i, flags in enumerate(flags_seq):
        arr[i].type = INPUT_MOUSE
        arr[i].mi.dwFlags = flags
        arr[i].mi.dwExtraInfo = INJECTED_MARKER
    _SendInput(len(flags_seq), arr, _INPUT_SZ)


# ── Alt+Tab ────────────────────────────────────────────────────────────────

def begin_switch(forward: bool) -> None:
    if forward:
        _keys((VK_MENU, _D), (VK_TAB, _D), (VK_TAB, _U_))
    else:
        _keys((VK_MENU, _D), (VK_SHIFT, _D), (VK_TAB, _D), (VK_TAB, _U_), (VK_SHIFT, _U_))


def cycle(forward: bool) -> None:
    if forward:
        _keys((VK_TAB, _D), (VK_TAB, _U_))
    else:
        _keys((VK_SHIFT, _D), (VK_TAB, _D), (VK_TAB, _U_), (VK_SHIFT, _U_))


def end_switch() -> None:
    _keys((VK_MENU, _U_))


# ── Mouse helpers ──────────────────────────────────────────────────────────

def inject_right_down() -> None:
    """Retroactive right_down at current cursor pos so apps can start gesture tracking."""
    _mouse(MOUSEEVENTF_RIGHTDOWN)


def inject_right_click() -> None:
    """Right down+up → context menu at current cursor pos."""
    _mouse(MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP)


