"""Global crash handling, exception logging, and 1-click diagnostic export.

Provides:
- sys.excepthook & threading.excepthook handlers to capture unhandled exceptions.
- Persistent crash logging in %LOCALAPPDATA%\\RightWheel\\data\\crash.log.
- 1-click diagnostic report generation and clipboard copy.
- Log directory quick-opener.
"""
from __future__ import annotations

import os
from pathlib import Path
import platform
import sys
import threading
import time
import traceback
from typing import Any

from src.core.app_paths import get_app_root, get_config_root, log_debug

LAST_CRASH_INFO: dict[str, Any] = {}
_ORIGINAL_EXCEPTHOOK = sys.excepthook


def get_logs_dir() -> Path:
    """Return runtime-writable logs/data directory."""
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        p = Path(local_appdata) / "RightWheel" / "data"
    else:
        p = get_config_root() / "data"
    try:
        p.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return p


def write_crash_log(exc_type: type, exc_value: BaseException, exc_tb: Any) -> None:
    """Write detailed exception traceback to crash.log in both local appdata and app root."""
    global LAST_CRASH_INFO
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

    LAST_CRASH_INFO = {
        "timestamp": now_str,
        "type": getattr(exc_type, "__name__", str(exc_type)),
        "message": str(exc_value),
        "traceback": tb_str,
    }

    entry = f"[{now_str}] UNHANDLED EXCEPTION: {exc_type.__name__}: {exc_value}\n{tb_str}\n" + ("=" * 80) + "\n"

    # 1. Write to LOCALAPPDATA
    try:
        crash_path = get_logs_dir() / "crash.log"
        with open(crash_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

    # 2. Best-effort write to app root data
    try:
        app_crash_path = get_app_root() / "data" / "crash.log"
        app_crash_path.parent.mkdir(parents=True, exist_ok=True)
        with open(app_crash_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

    log_debug(f"Crash captured: {exc_type.__name__}: {exc_value}")


def _unhandled_exception_hook(exc_type: type, exc_value: BaseException, exc_tb: Any) -> None:
    write_crash_log(exc_type, exc_value, exc_tb)
    try:
        if _ORIGINAL_EXCEPTHOOK:
            _ORIGINAL_EXCEPTHOOK(exc_type, exc_value, exc_tb)
    except Exception:
        pass


def _unhandled_thread_exception_hook(args: threading.ExceptHookArgs) -> None:
    write_crash_log(args.exc_type, args.exc_value, args.exc_traceback)


def install_crash_handlers() -> None:
    """Install global process and thread exception hooks."""
    sys.excepthook = _unhandled_exception_hook
    if hasattr(threading, "excepthook"):
        threading.excepthook = _unhandled_thread_exception_hook
    log_debug("Crash handlers successfully installed.")


def generate_diagnostic_report() -> str:
    """Generate an anonymous, detailed technical diagnostic report string."""
    lines: list[str] = [
        "=== RIGHTWHEEL DIAGNOSTIC REPORT ===",
        f"Generated At: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"OS: {platform.platform()} ({platform.machine()})",
        f"Python: {platform.python_version()} ({platform.architecture()[0]})",
        f"App Root: {get_app_root()}",
        f"Config Root: {get_config_root()}",
        f"Logs Dir: {get_logs_dir()}",
    ]

    # License / Trial Status check
    try:
        from src.core.store_license_service import get_license_service
        svc = get_license_service()
        st = svc.get_status()
        lines.append(f"License Status: {st.get('status')} | Days Left: {st.get('days_remaining')} | Is Pro: {st.get('is_pro')}")
    except Exception as e:
        lines.append(f"License Status: Unknown ({e})")

    # Last crash info
    if LAST_CRASH_INFO:
        lines.append("\n--- LAST CRASH IN CURRENT SESSION ---")
        lines.append(f"Time: {LAST_CRASH_INFO.get('timestamp')}")
        lines.append(f"Error: {LAST_CRASH_INFO.get('type')}: {LAST_CRASH_INFO.get('message')}")
        lines.append("Traceback:")
        lines.append(LAST_CRASH_INFO.get("traceback", ""))
    else:
        try:
            clog = get_logs_dir() / "crash.log"
            if clog.exists() and clog.stat().st_size > 0:
                with open(clog, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                last_block = content.split("=" * 80)[-1].strip()
                lines.append(f"\n--- RECENT CRASH FROM LOG ---\n{last_block}")
            else:
                lines.append("\nNo crash recorded. Session is healthy.")
        except Exception:
            lines.append("\nNo crash recorded.")

    lines.append("=" * 42)
    return "\n".join(lines)


def copy_diagnostic_to_clipboard() -> bool:
    """Copy the generated diagnostic report to the Windows clipboard."""
    text = generate_diagnostic_report()
    try:
        import ctypes
        GMEM_MOVEABLE = 0x0002
        CF_UNICODETEXT = 13

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        if not user32.OpenClipboard(0):
            return False

        user32.EmptyClipboard()
        encoded = text.encode("utf-16le") + b"\x00\x00"
        h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
        if h_mem:
            ptr = kernel32.GlobalLock(h_mem)
            ctypes.memmove(ptr, encoded, len(encoded))
            kernel32.GlobalUnlock(h_mem)
            user32.SetClipboardData(CF_UNICODETEXT, h_mem)
        user32.CloseClipboard()
        return True
    except Exception:
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return True
        except Exception:
            return False


def open_crash_logs_folder() -> bool:
    """Open the crash/logs directory in Windows File Explorer."""
    try:
        p = get_logs_dir()
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
        os.startfile(str(p))
        return True
    except Exception as e:
        log_debug(f"Failed to open logs folder: {e}")
        return False
