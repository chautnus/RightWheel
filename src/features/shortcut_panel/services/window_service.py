"""Get exe, window title, and class name for a HWND — ctypes only, no psutil."""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import os

_u32 = ctypes.windll.user32
_k32 = ctypes.windll.kernel32

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def get_hwnd_info(hwnd: int) -> tuple[str, str, str]:
    """Return (exe_basename, window_title, class_name).

    All strings are empty on failure or when hwnd is 0.
    exe_basename is case-preserved (e.g. 'WINWORD.EXE').
    """
    if not hwnd:
        return "", "", ""

    # window title
    buf = ctypes.create_unicode_buffer(512)
    _u32.GetWindowTextW(hwnd, buf, 512)
    title = buf.value

    # win32 class name
    buf2 = ctypes.create_unicode_buffer(256)
    _u32.GetClassNameW(hwnd, buf2, 256)
    class_name = buf2.value

    # exe basename via QueryFullProcessImageName
    pid = wt.DWORD(0)
    _u32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    exe = ""
    if pid.value:
        h = _k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        if h:
            buf3 = ctypes.create_unicode_buffer(512)
            sz   = wt.DWORD(512)
            if _k32.QueryFullProcessImageNameW(h, 0, buf3, ctypes.byref(sz)):
                exe = os.path.basename(buf3.value)
            _k32.CloseHandle(h)

    return exe, title, class_name
