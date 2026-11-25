"""Resolve a stable, writable app root directory for both dev and frozen (PyInstaller) runs.

PyInstaller onefile builds extract to a temp dir (sys._MEIPASS) whose __file__-derived
paths disappear when the process exits. Runtime-written files (backups, logs, config)
must live next to the real .exe instead.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path


def get_app_root() -> Path:
    """Return the directory that should hold runtime-writable data/config/scripts folders."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


def get_config_root() -> Path:
    """Return %APPDATA%\\RightWheel\\ directory, creating it if it does not exist."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        config_dir = Path(appdata) / "RightWheel"
    else:
        config_dir = Path.home() / "AppData" / "Roaming" / "RightWheel"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


MAX_LOG_BYTES = 2 * 1024 * 1024  # 2 MB per log file limit


def _get_writable_log_dir() -> Path:
    """Return a writable log directory, preferring %LOCALAPPDATA% when running from read-only WindowsApps."""
    exe_str = str(getattr(sys, "executable", ""))
    if getattr(sys, "frozen", False) and "WindowsApps" in exe_str:
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / "RightWheel" / "data"
        return get_config_root() / "data"
    return get_app_root() / "data"


def log_debug(msg: str, filename: str = "app_debug.log") -> None:
    """Append a timestamped line to data/<filename> with 2MB rotation and MSIX fallback. Never raises."""
    try:
        log_dir = _get_writable_log_dir()
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            local_appdata = os.environ.get("LOCALAPPDATA")
            log_dir = (Path(local_appdata) / "RightWheel" / "data") if local_appdata else (get_config_root() / "data")
            log_dir.mkdir(parents=True, exist_ok=True)
        target_path = log_dir / filename

        # Rotate if file size exceeds MAX_LOG_BYTES to prevent memory/disk cache bloat
        if target_path.exists() and target_path.stat().st_size > MAX_LOG_BYTES:
            old_path = log_dir / f"{filename}.old"
            try:
                if old_path.exists():
                    old_path.unlink()
                target_path.rename(old_path)
            except Exception:
                pass

        with open(target_path, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass
