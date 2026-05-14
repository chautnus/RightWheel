from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import threading
import time
from typing import Callable

from ..types.mouse_mapper_types import MouseEvent, ScrollDirection
from .hotkey_service import INJECTED_MARKER

WH_MOUSE_LL    = 14
WM_MOUSEMOVE   = 0x0200
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP   = 0x0205
WM_MOUSEWHEEL  = 0x020A
WM_APP_REHOOK  = 0x8001   # custom thread msg: re-register hook after sleep/wake

user32   = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
user32.CallNextHookEx.restype    = ctypes.c_long
user32.SetWindowsHookExW.restype = ctypes.c_void_p
user32.GetMessageW.restype       = ctypes.c_long


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt",          wt.POINT),
        ("mouseData",   wt.DWORD),
        ("flags",       wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


_HookProc = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int, wt.WPARAM, ctypes.POINTER(MSLLHOOKSTRUCT),
    use_last_error=True,
)


class MouseHookService:
    """Global WH_MOUSE_LL hook.

    wants_move_events: fast callable — if it returns False, WM_MOUSEMOVE events
    are passed through without entering Python logic (avoids LL hook timeout from
    high-frequency Edge/trackpad move events).
    """

    def __init__(
        self,
        on_event: Callable[[MouseEvent], bool],
        wants_move_events: Callable[[], bool] = lambda: True,
    ) -> None:
        self._on_event       = on_event
        self._wants_moves    = wants_move_events
        self._hook_id        = None
        self._thread_id: int = 0
        self._alive          = True
        self._thread         = threading.Thread(target=self._run, daemon=True)
        self._proc           = _HookProc(self._hook_proc)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._alive = False
        if self._hook_id:
            user32.UnhookWindowsHookEx(self._hook_id)
            self._hook_id = None
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)

    def _run(self) -> None:
        self._thread_id = kernel32.GetCurrentThreadId()
        self._hook_id   = user32.SetWindowsHookExW(WH_MOUSE_LL, self._proc, None, 0)
        self._start_watchdog()
        msg = wt.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_APP_REHOOK:
                # Hook may have been killed by Windows after sleep/wake/lock.
                # Safely unregister old handle and re-register.
                if self._hook_id:
                    user32.UnhookWindowsHookEx(self._hook_id)
                self._hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, self._proc, None, 0)
            else:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        if self._hook_id:
            user32.UnhookWindowsHookEx(self._hook_id)

    def _start_watchdog(self) -> None:
        """Daemon thread that re-registers the hook every 10 s.

        WH_MOUSE_LL is silently killed by Windows after sleep, lock, or UAC.
        Periodic re-registration guarantees recovery within 10 s of any such event.
        """
        def _watch() -> None:
            while self._alive:
                time.sleep(10)
                if self._alive and self._thread_id:
                    user32.PostThreadMessageW(self._thread_id, WM_APP_REHOOK, 0, 0)
        threading.Thread(target=_watch, daemon=True).start()

    def _hook_proc(self, n_code: int, w_param: int, l_param) -> int:
        try:
            if n_code >= 0:
                data = l_param.contents

                if data.dwExtraInfo == INJECTED_MARKER:
                    return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)

                # Fast-path: skip WM_MOUSEMOVE entirely when logic doesn't need it.
                # Avoids Python overhead on every cursor movement (Edge can fire
                # 200+ move events/sec which would risk the 300ms LL hook timeout).
                if w_param == WM_MOUSEMOVE:
                    if not self._wants_moves():
                        return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)
                    self._on_event(MouseEvent("move", x=data.pt.x, y=data.pt.y))
                    return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)

                x, y     = data.pt.x, data.pt.y
                suppress = False

                if w_param == WM_RBUTTONDOWN:
                    suppress = self._on_event(MouseEvent("right_down", x=x, y=y))
                elif w_param == WM_RBUTTONUP:
                    suppress = self._on_event(MouseEvent("right_up", x=x, y=y))
                elif w_param == WM_MOUSEWHEEL:
                    delta     = ctypes.c_short(data.mouseData >> 16).value
                    direction = ScrollDirection.UP if delta > 0 else ScrollDirection.DOWN
                    suppress  = self._on_event(MouseEvent("scroll", scroll_dir=direction))

                if suppress:
                    return 1

        except Exception:
            pass  # never let Python exceptions corrupt the hook return value

        return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)
