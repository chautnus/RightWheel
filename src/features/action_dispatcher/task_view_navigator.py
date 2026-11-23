"""Task View / Alt-Tab window switcher scroll navigator (aligned with RightWheel pattern).

When Windows Task View (Win+Tab) or Alt-Tab is active on screen, this service
intercepts 2-finger trackpad scrolling (or mouse wheel) and translates it into
keyboard navigation (Left / Right arrow keys) to smoothly browse open window thumbnails.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import threading
import time
from typing import Any

from src.core.app_paths import log_debug
from src.features.action_dispatcher.dispatcher import ActionDispatcher, is_task_switcher_active

WH_MOUSE_LL = 14
WM_MOUSEWHEEL = 0x020A
WM_MOUSEHWHEEL = 0x020E
WM_QUIT = 0x0012

user32 = getattr(ctypes, "windll", None).user32 if hasattr(ctypes, "windll") else None
kernel32 = getattr(ctypes, "windll", None).kernel32 if hasattr(ctypes, "windll") else None

if user32:
    user32.CallNextHookEx.restype = ctypes.c_long
    user32.SetWindowsHookExW.restype = ctypes.c_void_p
    user32.GetMessageW.restype = ctypes.c_long


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wt.POINT),
        ("mouseData", wt.DWORD),
        ("flags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


_HookProc = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int, wt.WPARAM, ctypes.POINTER(MSLLHOOKSTRUCT),
    use_last_error=True,
)


class TaskViewNavigator:
    """Listens for mouse wheel / 2-finger scroll when Task View or Alt-Tab is active."""

    def __init__(self, dispatcher: ActionDispatcher | None = None) -> None:
        self._dispatcher = dispatcher or ActionDispatcher()
        self._hook_id: Any = None
        self._thread_id: int = 0
        self._alive = True
        self._last_nav_time = 0.0
        self._min_nav_interval = 0.075  # 75ms debounce between navigation steps
        self._thread = threading.Thread(target=self._run, daemon=True, name="TaskViewNavigatorThread")
        self._proc = _HookProc(self._hook_proc)

    def start(self) -> None:
        if not user32 or not kernel32:
            return
        self._alive = True
        self._thread.start()
        log_debug("TaskViewNavigator started.")

    def stop(self) -> None:
        self._alive = False
        if user32 and self._hook_id:
            try:
                user32.UnhookWindowsHookEx(self._hook_id)
            except Exception:
                pass
            self._hook_id = None
        if user32 and self._thread_id:
            try:
                user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass
        log_debug("TaskViewNavigator stopped.")

    def _run(self) -> None:
        if not user32 or not kernel32:
            return
        self._thread_id = kernel32.GetCurrentThreadId()
        self._hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, self._proc, None, 0)
        if not self._hook_id:
            log_debug("TaskViewNavigator failed to install WH_MOUSE_LL hook.")
            return

        msg = wt.MSG()
        while self._alive:
            res = user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
            if res <= 0:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self._hook_id:
            user32.UnhookWindowsHookEx(self._hook_id)
            self._hook_id = None

    def _hook_proc(self, n_code: int, w_param: wt.WPARAM, l_param: ctypes.POINTER(MSLLHOOKSTRUCT)) -> int:
        try:
            if n_code >= 0 and (w_param == WM_MOUSEWHEEL or w_param == WM_MOUSEHWHEEL):
                if is_task_switcher_active():
                    data = l_param.contents
                    delta = ctypes.c_short(data.mouseData >> 16).value
                    now = time.perf_counter()
                    if now - self._last_nav_time >= self._min_nav_interval:
                        self._last_nav_time = now
                        # Vertical wheel down (delta < 0) or Horizontal wheel right (delta > 0) -> Move to next window
                        if w_param == WM_MOUSEHWHEEL:
                            direction = "right" if delta > 0 else "left"
                        else:
                            direction = "right" if delta < 0 else "left"
                        self._dispatcher.execute({
                            "type": "TASK_VIEW_NAV",
                            "target": direction,
                        })
                    # Suppress raw wheel event inside switcher to prevent jarring scrolling
                    return 1
        except Exception:
            pass

        return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)
