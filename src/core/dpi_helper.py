"""DPI Awareness helper for Windows 10/11 native high-resolution rendering."""
from __future__ import annotations

import ctypes
import sys


def enable_high_dpi_awareness() -> bool:
    """Enable Per-Monitor v2 DPI Awareness to render razor-sharp native text on Windows.

    Prevents Windows DWM from applying blurry bilinear bitmap upscaling (DPI virtualization)
    on high-resolution or scaled laptop displays (125%, 150%, 200%).
    """
    if sys.platform != "win32":
        return False

    # 1. Try Windows 10 1703+ Per-Monitor v2 DPI Awareness (-4 = DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
    try:
        res = ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        if res:
            return True
    except Exception:
        pass

    # 2. Try Windows 8.1+ Shcore.dll SetProcessDpiAwareness (2 = PROCESS_PER_MONITOR_DPI_AWARE)
    try:
        res = ctypes.windll.shcore.SetProcessDpiAwareness(2)
        if res == 0:
            return True
    except Exception:
        pass

    # 3. Fallback to system-level DPI Aware
    try:
        return bool(ctypes.windll.user32.SetProcessDPIAware())
    except Exception:
        return False
