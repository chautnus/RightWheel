"""Memory Manager for RightWheel (Win32 Working Set Compaction & Trim).

Provides proactive memory management for background execution:
- Invokes Python gc.collect(2) to sweep circular references.
- Calls Win32 SetProcessWorkingSetSize(-1, -1) and psapi.EmptyWorkingSet()
  to return unreferenced physical RAM pages back to the Windows Standby list.
- Implements idle-aware periodic trimming (only triggers when no mouse activity
  has occurred for a configurable quiet threshold, e.g. 30 seconds).
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import gc
import threading
import time
from typing import Any

# Win32 API Definitions
_kernel32 = ctypes.windll.kernel32
_psapi = ctypes.windll.psapi

_GetCurrentProcess = _kernel32.GetCurrentProcess
_GetCurrentProcess.restype = wintypes.HANDLE

_SetProcessWorkingSetSize = _kernel32.SetProcessWorkingSetSize
_SetProcessWorkingSetSize.argtypes = [wintypes.HANDLE, ctypes.c_size_t, ctypes.c_size_t]
_SetProcessWorkingSetSize.restype = wintypes.BOOL

_EmptyWorkingSet = _psapi.EmptyWorkingSet
_EmptyWorkingSet.argtypes = [wintypes.HANDLE]
_EmptyWorkingSet.restype = wintypes.BOOL

# Thread-safe activity tracking
_last_activity_lock = threading.Lock()
_last_activity_time: float = time.time()
_periodic_thread: threading.Thread | None = None
_stop_event = threading.Event()


def notify_activity() -> None:
    """Notify memory manager that user is actively interacting (mouse, gesture, UI)."""
    global _last_activity_time
    with _last_activity_lock:
        _last_activity_time = time.time()


def get_idle_seconds() -> float:
    """Return seconds since last user interaction."""
    with _last_activity_lock:
        return time.time() - _last_activity_time


def trim_memory() -> bool:
    """Safely compact and trim process working set.
    
    1. Runs full Python garbage collection across all 3 generations.
    2. Calls SetProcessWorkingSetSize(-1, -1) and EmptyWorkingSet.
    Returns True if trim completed without error.
    """
    try:
        gc.collect(2)
        h_process = _GetCurrentProcess()
        if h_process:
            # -1, -1 instructs Windows to trim unneeded pages from working set
            _SetProcessWorkingSetSize(h_process, ctypes.c_size_t(-1), ctypes.c_size_t(-1))
            _EmptyWorkingSet(h_process)
        return True
    except Exception:
        return False


def start_periodic_trim(interval_s: float = 300.0, min_idle_s: float = 30.0) -> None:
    """Start background daemon thread that trims memory periodically during idle periods."""
    global _periodic_thread, _stop_event

    if _periodic_thread is not None and _periodic_thread.is_alive():
        return

    _stop_event.clear()

    def _worker() -> None:
        while not _stop_event.wait(interval_s):
            if get_idle_seconds() >= min_idle_s:
                trim_memory()

    _periodic_thread = threading.Thread(target=_worker, name="MemoryTrimDaemon", daemon=True)
    _periodic_thread.start()


def stop_periodic_trim() -> None:
    """Stop the background memory trimming thread."""
    global _stop_event
    _stop_event.set()
