"""Manage Windows auto-startup via HKCU Run registry key."""
from __future__ import annotations

import sys
import winreg

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "RightWheel"


def _exe_path() -> str:
    """Return exe path when running as PyInstaller bundle; empty string otherwise."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return ""


def is_enabled() -> bool:
    """Return True if the startup registry value exists."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as k:
            winreg.QueryValueEx(k, _APP_NAME)
            return True
    except (FileNotFoundError, OSError):
        return False


def enable() -> bool:
    """Add exe to startup. Returns False when running from source (no exe)."""
    exe = _exe_path()
    if not exe:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY,
                            access=winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, _APP_NAME, 0, winreg.REG_SZ, f'"{exe}"')
        return True
    except OSError:
        return False


def disable() -> None:
    """Remove startup registry value (silently ignored if not present)."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY,
                            access=winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, _APP_NAME)
    except (FileNotFoundError, OSError):
        pass
