from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import logging
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

# Win64 explicit argtypes & restype declarations
user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wt.WPARAM, wt.LPARAM]
user32.CallNextHookEx.restype = ctypes.c_ssize_t

user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, wt.DWORD]
user32.SetWindowsHookExW.restype = ctypes.c_void_p

user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]
user32.UnhookWindowsHookEx.restype = wt.BOOL

user32.GetMessageW.argtypes = [ctypes.POINTER(wt.MSG), wt.HWND, wt.UINT, wt.UINT]
user32.GetMessageW.restype = wt.BOOL


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt",          wt.POINT),
        ("mouseData",   wt.DWORD),
        ("flags",       wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


_HookProc = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t, ctypes.c_int, wt.WPARAM, ctypes.POINTER(MSLLHOOKSTRUCT),
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
        on_scroll_modifier: Callable[[ScrollDirection], bool] | None = None,
    ) -> None:
        self._on_event       = on_event
        self._wants_moves    = wants_move_events
        self._on_scroll_mod  = on_scroll_modifier
        self._hook_id: int | None = None
        self._thread_id: int = 0
        self._alive          = True
        self._watchdog_started = False
        self._thread         = threading.Thread(target=self._run, daemon=True)
        self._proc           = _HookProc(self._hook_proc)

        # Anti-timeout rate limiting variables for 500Hz/1000Hz gaming mice
        self._last_move_x: int = 0
        self._last_move_y: int = 0
        self._last_move_time: float = 0.0

        # Real-time event diagnostics
        self.stats: dict[str, int] = {
            "rmb_down": 0,
            "rmb_up": 0,
            "scroll": 0,
            "moves": 0,
            "rehook_count": 0,
        }

    @property
    def is_hook_alive(self) -> bool:
        """Check if hook handle exists and thread is running."""
        return bool(self._hook_id and self._thread.is_alive())

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
        from src.core.app_paths import log_debug
        self._thread_id = kernel32.GetCurrentThreadId()
        self._hook_id   = user32.SetWindowsHookExW(WH_MOUSE_LL, self._proc, None, 0)
        if self._hook_id:
            log_debug(f"MouseHookService: hook installed successfully (hook_id=0x{self._hook_id:X}, thread={self._thread_id})")
        else:
            err = kernel32.GetLastError()
            log_debug(f"MouseHookService: SetWindowsHookExW FAILED (err={err})")

        self._start_watchdog()
        msg = wt.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_APP_REHOOK:
                # Hook may have been killed by Windows after sleep/wake/lock.
                # Safely unregister old handle and re-register.
                if self._hook_id:
                    user32.UnhookWindowsHookEx(self._hook_id)
                self._hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, self._proc, None, 0)
                self.stats["rehook_count"] += 1
                if self._hook_id:
                    log_debug(f"MouseHookService: hook re-registered (hook_id=0x{self._hook_id:X})")
                else:
                    err = kernel32.GetLastError()
                    log_debug(f"MouseHookService: re-register FAILED (err={err})")
            else:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        if self._hook_id:
            user32.UnhookWindowsHookEx(self._hook_id)
            self._hook_id = None
        self._thread_id = 0

    def _start_watchdog(self) -> None:
        """Daemon thread that re-registers the hook every 10 s.

        WH_MOUSE_LL is silently killed by Windows after sleep, lock, or UAC.
        Periodic re-registration guarantees recovery within 10 s of any such event.
        Also restarts the hook thread if it has terminated.
        """
        if self._watchdog_started:
            return
        self._watchdog_started = True

        def _watch() -> None:
            while self._alive:
                time.sleep(10)
                if not self._alive:
                    break
                if not self._thread.is_alive():
                    from src.core.app_paths import log_debug
                    log_debug("MouseHookService: hook thread is dead, restarting new hook thread...")
                    if self._hook_id:
                        try:
                            user32.UnhookWindowsHookEx(self._hook_id)
                        except Exception:
                            pass
                        self._hook_id = None
                    self._thread = threading.Thread(target=self._run, daemon=True)
                    self._thread.start()
                    continue
                if self._thread_id:
                    user32.PostThreadMessageW(self._thread_id, WM_APP_REHOOK, 0, 0)
        threading.Thread(target=_watch, daemon=True).start()

    def _hook_proc(self, n_code: int, w_param: int, l_param) -> int:
        try:
            if n_code >= 0:
                data = l_param.contents

                if data.dwExtraInfo == INJECTED_MARKER:
                    return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)

                # Fast-path: skip WM_MOUSEMOVE entirely when logic doesn't need it.
                # Avoids Python overhead on every cursor movement.
                if w_param == WM_MOUSEMOVE:
                    if not self._wants_moves():
                        return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)

                    # Anti-timeout rate limiter for 500Hz/1000Hz gaming mice:
                    # Forward to Python logic only if cursor moved >= 2px or >= 8ms elapsed (~125Hz max)
                    cur_x, cur_y = data.pt.x, data.pt.y
                    now = time.perf_counter()
                    if abs(cur_x - self._last_move_x) >= 2 or abs(cur_y - self._last_move_y) >= 2 or (now - self._last_move_time) >= 0.008:
                        self._last_move_x = cur_x
                        self._last_move_y = cur_y
                        self._last_move_time = now
                        self.stats["moves"] += 1
                        self._on_event(MouseEvent("move", x=cur_x, y=cur_y))
                    return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)

                x, y     = data.pt.x, data.pt.y
                suppress = False

                if w_param == WM_RBUTTONDOWN:
                    self.stats["rmb_down"] += 1
                    suppress = self._on_event(MouseEvent("right_down", x=x, y=y))
                elif w_param == WM_RBUTTONUP:
                    self.stats["rmb_up"] += 1
                    suppress = self._on_event(MouseEvent("right_up", x=x, y=y))
                elif w_param == WM_MOUSEWHEEL:
                    self.stats["scroll"] += 1
                    delta     = ctypes.c_short(data.mouseData >> 16).value
                    direction = ScrollDirection.UP if delta > 0 else ScrollDirection.DOWN
                    if self._on_scroll_mod is not None and self._on_scroll_mod(direction):
                        suppress = True
                    else:
                        suppress = self._on_event(MouseEvent("scroll", scroll_dir=direction))

                if suppress:
                    return 1

        except Exception as exc:
            try:
                from src.core.app_paths import log_debug
                log_debug(f"MouseHookService._hook_proc exception: {exc}")
            except Exception:
                pass

        return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)
