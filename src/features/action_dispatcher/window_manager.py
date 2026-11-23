"""Window Manager helper for enumerating and managing Windows application windows."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import os

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SW_MINIMIZE = 6
SW_MAXIMIZE = 3
SW_RESTORE = 9
WM_CLOSE = 0x0010
ASFW_ANY = 0xFFFFFFFF


def get_window_title(hwnd: int) -> str:
    """Retrieve title text for a window handle."""
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def get_window_exe(hwnd: int) -> str:
    """Retrieve executable name for a window handle."""
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return ""

    h_proc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not h_proc:
        return ""

    try:
        buf_size = wintypes.DWORD(1024)
        buf = ctypes.create_unicode_buffer(1024)
        success = kernel32.QueryFullProcessImageNameW(h_proc, 0, buf, ctypes.byref(buf_size))
        if success:
            return os.path.basename(buf.value)
        return ""
    finally:
        kernel32.CloseHandle(h_proc)


def is_window_visible(hwnd: int) -> bool:
    """Check if window is visible and not an empty tool window."""
    if not user32.IsWindowVisible(hwnd):
        return False
    title = get_window_title(hwnd)
    if not title:
        return False
    # Check if window is cloaked (e.g. UWP apps suspended)
    DWMWA_CLOAKED = 14
    cloaked = wintypes.DWORD()
    try:
        dwmapi = ctypes.windll.dwmapi
        if dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked)) == 0:
            if cloaked.value != 0:
                return False
    except Exception:
        pass
    return True


class WindowManager:
    """Service to enumerate and manage active windows."""

    def get_foreground_window(self) -> int:
        return user32.GetForegroundWindow()

    def get_recent_windows(self) -> list[dict]:
        """List active visible application windows."""
        windows: list[dict] = []

        def enum_handler(hwnd: int, lparam: int) -> bool:
            if is_window_visible(hwnd):
                title = get_window_title(hwnd)
                exe = get_window_exe(hwnd)
                windows.append({
                    "hwnd": hwnd,
                    "title": title,
                    "exe": exe,
                })
            return True

        user32.EnumWindows(WNDENUMPROC(enum_handler), 0)
        return windows

    def minimize_window(self, hwnd: int) -> bool:
        return bool(user32.ShowWindow(hwnd, SW_MINIMIZE))

    def maximize_window(self, hwnd: int) -> bool:
        return bool(user32.ShowWindow(hwnd, SW_MAXIMIZE))

    def close_window(self, hwnd: int) -> bool:
        return bool(user32.PostMessageW(hwnd, WM_CLOSE, 0, 0))


def focus_window(hwnd: int) -> bool:
    """Reliably bring `hwnd` to foreground, bypassing Windows foreground lock via AttachThreadInput."""
    if not hwnd or not user32.IsWindow(hwnd):
        return False
    try:
        user32.AllowSetForegroundWindow(ASFW_ANY)
    except Exception:
        pass
    try:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        fg = user32.GetForegroundWindow()
        if fg == hwnd:
            return True
        fg_tid = user32.GetWindowThreadProcessId(fg, None) if fg else 0
        target_tid = user32.GetWindowThreadProcessId(hwnd, None)
        cur_tid = kernel32.GetCurrentThreadId()
        attached_fg = False
        attached_target = False
        try:
            if fg_tid and fg_tid != cur_tid:
                attached_fg = bool(user32.AttachThreadInput(cur_tid, fg_tid, True))
            if target_tid and target_tid != cur_tid:
                attached_target = bool(user32.AttachThreadInput(cur_tid, target_tid, True))
            user32.BringWindowToTop(hwnd)
            ok = bool(user32.SetForegroundWindow(hwnd))
            return ok
        finally:
            if attached_target:
                user32.AttachThreadInput(cur_tid, target_tid, False)
            if attached_fg:
                user32.AttachThreadInput(cur_tid, fg_tid, False)
    except Exception:
        return False
