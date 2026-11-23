"""Single instance application guard using Win32 Named Mutex."""
from __future__ import annotations

import ctypes
import sys
from typing import Any

ERROR_ALREADY_EXISTS = 183
DEFAULT_MUTEX_NAME = "Local\\RightWheel_SingleInstance_Mutex"


class SingleInstanceGuard:
    """Ensures only one instance of the application can run simultaneously."""

    def __init__(self, mutex_name: str = DEFAULT_MUTEX_NAME) -> None:
        self.mutex_name = mutex_name
        self._handle: Any = None
        self._is_owner = False

    def acquire(self, show_dialog: bool = True) -> bool:
        """Attempt to acquire the single-instance mutex.

        Returns True if this is the primary instance, False if already running.
        """
        kernel32 = ctypes.windll.kernel32
        kernel32.SetLastError(0)

        # CreateMutexW(lpMutexAttributes, bInitialOwner, lpName)
        self._handle = kernel32.CreateMutexW(None, True, self.mutex_name)
        last_error = kernel32.GetLastError()

        if not self._handle or last_error == ERROR_ALREADY_EXISTS:
            if show_dialog:
                try:
                    from src.core.i18n import t as _t
                    user32 = ctypes.windll.user32
                    user32.MessageBoxW(
                        0,
                        _t("msg_already_running", "RightWheel đã đang chạy trên máy tính (kiểm tra khay hệ thống System Tray)."),
                        _t("title_already_running", "RightWheel — Đang chạy"),
                        0x40,  # MB_OK | MB_ICONINFORMATION
                    )
                except Exception:
                    pass
            self.release()
            return False

        self._is_owner = True
        return True

    def release(self) -> None:
        """Release mutex handle."""
        if self._handle:
            try:
                kernel32 = ctypes.windll.kernel32
                if self._is_owner:
                    kernel32.ReleaseMutex(self._handle)
                kernel32.CloseHandle(self._handle)
            except Exception:
                pass
            self._handle = None
            self._is_owner = False

    def __enter__(self) -> bool:
        return self.acquire(show_dialog=False)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.release()
