"""Action Dispatcher module for executing configured gesture actions."""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import os
import shutil
import subprocess
import time
from typing import Any
import webbrowser

from src.features.action_dispatcher.window_manager import WindowManager

MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

INPUT_KEYBOARD = 1
INPUT_MOUSE = 0
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

_VK: dict[str, int] = {
    "ctrl": 0x11, "control": 0x11,
    "alt": 0x12,
    "shift": 0x10,
    "win": 0x5B, "windows": 0x5B, "win_l": 0x5B, "win_r": 0x5C,
    "tab": 0x09, "enter": 0x0D, "return": 0x0D,
    "esc": 0x1B, "escape": 0x1B,
    "space": 0x20, "backspace": 0x08,
    "del": 0x2E, "delete": 0x2E, "ins": 0x2D, "insert": 0x2D,
    "home": 0x24, "end": 0x23,
    "pgup": 0x21, "pageup": 0x21,
    "pgdn": 0x22, "pagedown": 0x22,
    "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
    "prtsc": 0x2C, "printscreen": 0x2C, "print_screen": 0x2C, "snapshot": 0x2C,
    **{f"f{i}": 0x6F + i for i in range(1, 13)},
    **{str(i): 0x30 + i for i in range(10)},
    **{chr(65 + i).lower(): 0x41 + i for i in range(26)},
}

_EXTENDED = {0x25, 0x26, 0x27, 0x28, 0x2E, 0x2D, 0x21, 0x22, 0x24, 0x23, 0x5C}


class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wt.LONG),
        ("dy", wt.LONG),
        ("mouseData", wt.DWORD),
        ("dwFlags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wt.WORD),
        ("wScan", wt.WORD),
        ("dwFlags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class _HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wt.DWORD),
        ("wParamL", wt.WORD),
        ("wParamH", wt.WORD),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", _MOUSEINPUT),
        ("ki", _KEYBDINPUT),
        ("hi", _HARDWAREINPUT),
    ]


class _INPUT(ctypes.Structure):
    _anonymous_ = ("_u",)
    _fields_ = [("type", wt.DWORD), ("_u", _INPUT_UNION)]


_SZ = ctypes.sizeof(_INPUT)


def is_task_switcher_active() -> bool:
    """Check if Windows Task View or Alt-Tab switcher is currently in the foreground."""
    if not (hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32")):
        return False
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    if not hwnd:
        return False
    buf = ctypes.create_unicode_buffer(256)
    ctypes.windll.user32.GetClassNameW(hwnd, buf, 256)
    cls_name = buf.value
    if cls_name in ("XamlExplorerHostIslandWindow", "TaskSwitcherWnd", "MultitaskingViewFrame"):
        return True
    if cls_name == "Windows.UI.Core.CoreWindow":
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
        if "Task View" in buf.value or "Alt-Tab" in buf.value:
            return True
    return False


class ActionDispatcher:
    """Executes actions mapped to touchpad gestures (FR-005)."""

    VALID_TYPES = {
        "RUN_APP", "RUN_SHELL", "OPEN_URL", "KEY_COMBO", "WINDOW_CMD",
        "SEQUENCE", "execute_sequence", "MIDDLE_CLICK", "TASK_VIEW_NAV",
        "TYPE_TEXT", "WEB_CLIP",
    }

    def __init__(self, window_manager: WindowManager | None = None) -> None:
        self.wm = window_manager or WindowManager()

    def execute(self, action_config: dict[str, Any]) -> dict[str, Any]:
        """Execute a configured action according to Test Contract.

        Returns:
            {"ok": True, "data": {"executed_type": str, "target": str, "execution_time_ms": float}}
            or
            {"ok": False, "error": {"code": "TARGET_NOT_FOUND" | "COMMAND_TIMEOUT" | "INVALID_ACTION_SCHEMA", "message": str}}
        """
        start_t = time.perf_counter()

        if not isinstance(action_config, dict):
            return {
                "ok": False,
                "error": {
                    "code": "INVALID_ACTION_SCHEMA",
                    "message": "Action config must be a dictionary",
                },
            }

        act_type = action_config.get("type", "")
        target = action_config.get("target", "")

        if act_type not in self.VALID_TYPES:
            return {
                "ok": False,
                "error": {
                    "code": "INVALID_ACTION_SCHEMA",
                    "message": f"Unsupported action type: {act_type}",
                },
            }

        try:
            if act_type == "RUN_APP":
                # Check target executable existence
                target_path = Path_or_str = target
                if not os.path.exists(target_path) and not shutil.which(target_path):
                    return {
                        "ok": False,
                        "error": {
                            "code": "TARGET_NOT_FOUND",
                            "message": f"Executable not found on system: {target}",
                        },
                    }
                subprocess.Popen([target], shell=False)

            elif act_type == "RUN_SHELL":
                subprocess.Popen(target, shell=True)

            elif act_type == "OPEN_URL":
                from src.features.action_dispatcher.clipboard_web_actions import open_url_default_browser
                open_url_default_browser(target)

            elif act_type == "KEY_COMBO":
                # Simulate keystroke combinations via ctypes or pywin32 if available
                if not self._send_key_combo(target):
                    return {
                        "ok": False,
                        "error": {
                            "code": "INVALID_ACTION_SCHEMA",
                            "message": f"KEY_COMBO target is empty or has no recognized keys: {target!r}",
                        },
                    }

            elif act_type == "WINDOW_CMD":
                cmd = target.strip()
                cmd_upper = cmd.upper()
                if cmd_upper in ("RUN", "OPEN_RUN"):
                    self._send_key_combo("win+r")
                elif cmd_upper in ("SHOW_DESKTOP", "DESKTOP"):
                    self._send_key_combo("win+d")
                elif cmd_upper in ("TASK_MGR", "TASK_MANAGER"):
                    self._send_key_combo("ctrl+shift+esc")
                elif cmd_upper in ("SETTINGS", "SETTINGS_WIN"):
                    self._send_key_combo("win+i")
                elif cmd_upper in ("NOTIFICATION_CENTER", "NOTIFICATIONS", "NOTIFICATION_PANEL"):
                    self._send_key_combo("win+n")
                elif cmd_upper in ("ACTION_CENTER", "QUICK_SETTINGS"):
                    self._send_key_combo("win+a")
                elif cmd_upper == "MINIMIZE":
                    hwnd = self.wm.get_foreground_window()
                    self.wm.minimize_window(hwnd)
                elif cmd_upper == "MAXIMIZE":
                    hwnd = self.wm.get_foreground_window()
                    self.wm.maximize_window(hwnd)
                elif cmd_upper == "CLOSE":
                    hwnd = self.wm.get_foreground_window()
                    self.wm.close_window(hwnd)
                else:
                    # Treat custom WINDOW_CMD as Windows Run command (e.g. calc, notepad, control)
                    try:
                        subprocess.Popen(cmd, shell=True)
                    except Exception as e:
                        return {
                            "ok": False,
                            "error": {
                                "code": "RUN_CMD_FAILED",
                                "message": f"Failed to execute Windows command '{cmd}': {e}",
                            },
                        }

            elif act_type == "MIDDLE_CLICK":
                self._send_middle_click()

            elif act_type == "TASK_VIEW_NAV":
                # Navigate window thumbnails in Task View / Alt-Tab (RightWheel pattern)
                direction = str(target).lower()
                vk = 0x27 if direction in ("next", "right", "down") else 0x25
                self._send_single_key(vk, is_up=False)
                time.sleep(0.015)
                self._send_single_key(vk, is_up=True)

            elif act_type == "TYPE_TEXT":
                from src.features.action_dispatcher.sequence_executor import execute_steps
                res = execute_steps([{"type": "text", "text": str(target), "delay_ms": 0}])
                if not res.get("ok"):
                    return res

            elif act_type == "WEB_CLIP":
                from src.features.action_dispatcher.sequence_executor import execute_steps
                res = execute_steps([{
                    "type": "url_clipboard",
                    "url_template": str(target),
                    "mode": action_config.get("mode", "url_query"),
                    "prompt": action_config.get("prompt", ""),
                    "auto_submit": bool(action_config.get("auto_submit", True)),
                    "delay_ms": 0,
                }])
                if not res.get("ok"):
                    return res

            elif act_type in ("SEQUENCE", "execute_sequence"):
                from src.features.action_dispatcher.sequence_executor import execute_steps, execute_steps_async
                steps = action_config.get("steps")
                if steps is None and isinstance(target, list):
                    steps = target
                if not isinstance(steps, list):
                    return {
                        "ok": False,
                        "error": {
                            "code": "INVALID_ACTION_SCHEMA",
                            "message": f"{act_type} requires 'steps' list in action_config",
                        },
                    }
                async_exec = bool(action_config.get("async", False))
                if async_exec:
                    execute_steps_async(steps)
                    res = {"ok": True, "data": {"executed_steps": len(steps), "elapsed_ms": 0.0}}
                else:
                    res = execute_steps(steps)
                if not res.get("ok"):
                    return res
                elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                return {
                    "ok": True,
                    "data": {
                        "executed_type": act_type,
                        "target": str(target),
                        "execution_time_ms": elapsed_ms,
                        "sequence_result": res.get("data", {}),
                    },
                }

            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            return {
                "ok": True,
                "data": {
                    "executed_type": act_type,
                    "target": target,
                    "execution_time_ms": elapsed_ms,
                },
            }
        except Exception as e:
            return {
                "ok": False,
                "error": {
                    "code": "TARGET_NOT_FOUND",
                    "message": str(e),
                },
            }

    @staticmethod
    def _resolve_scan_code(vk: int) -> int:
        """Resolve hardware scan code for SendInput, excluding VK_SNAPSHOT (0x2C).

        MapVirtualKeyW(0x2C, 0) returns 0x54 (SysRq), which triggers duplicate
        screenshot captures in Windows 11 Snipping Tool / Clipboard History.
        """
        if vk == 0x2C:
            return 0
        try:
            return int(ctypes.windll.user32.MapVirtualKeyW(vk, 0))
        except Exception:
            return 0

    def _send_single_key(self, vk: int, is_up: bool) -> None:
        if not (hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32")):
            return
        inp = _INPUT()
        inp.type = INPUT_KEYBOARD
        inp.ki.wVk = vk
        inp.ki.wScan = self._resolve_scan_code(vk)
        flags = KEYEVENTF_EXTENDEDKEY if vk in _EXTENDED else 0
        if is_up:
            flags |= KEYEVENTF_KEYUP
        inp.ki.dwFlags = flags
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), _SZ)

    def _send_key_combo(self, combo: str) -> bool:
        """Simulate keyboard shortcut via SendInput. Returns False if nothing was sent."""
        if not combo or not combo.strip():
            return False

        clean_combo = combo.strip().lower()
        # Automatically map Notification Center for Windows 10 vs 11:
        # Windows 11 (build >= 22000) uses Win+N, Windows 10 uses Win+A
        if clean_combo == "win+n":
            try:
                import sys
                if sys.getwindowsversion().build < 22000:
                    clean_combo = "win+a"
            except Exception:
                pass

        parts = [p.strip() for p in clean_combo.split("+")]
        vks = [_VK[p] for p in parts if p in _VK]
        if not vks:
            return False

        # If combination includes Win key or Alt+Tab, send sequentially with slight micro-delays
        # to ensure Windows Shell Hooks catch the hotkey reliably and switch windows cleanly
        has_win = (0x5B in vks or 0x5C in vks)
        has_alt_tab = (0x12 in vks and 0x09 in vks)
        if (has_win or has_alt_tab) and hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32"):
            for vk in vks:
                self._send_single_key(vk, is_up=False)
                time.sleep(0.015)
            for vk in reversed(vks):
                self._send_single_key(vk, is_up=True)
                time.sleep(0.015)
            return True

        # Otherwise, batch via standard SendInput
        n = len(vks) * 2
        arr = (_INPUT * n)()

        for i, vk in enumerate(vks):
            flags = KEYEVENTF_EXTENDEDKEY if vk in _EXTENDED else 0
            arr[i].type = INPUT_KEYBOARD
            arr[i].ki.wVk = vk
            arr[i].ki.wScan = self._resolve_scan_code(vk)
            arr[i].ki.dwFlags = flags

        for i, vk in enumerate(reversed(vks)):
            flags = (KEYEVENTF_EXTENDEDKEY if vk in _EXTENDED else 0) | KEYEVENTF_KEYUP
            arr[len(vks) + i].type = INPUT_KEYBOARD
            arr[len(vks) + i].ki.wVk = vk
            arr[len(vks) + i].ki.wScan = self._resolve_scan_code(vk)
            arr[len(vks) + i].ki.dwFlags = flags

        if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32"):
            ctypes.windll.user32.SendInput(n, arr, _SZ)
        return True


    def _send_middle_click(self) -> bool:
        """Simulate a middle mouse click (down then up)."""
        arr = (_INPUT * 2)()
        arr[0].type = INPUT_MOUSE
        arr[0].mi.dwFlags = MOUSEEVENTF_MIDDLEDOWN
        arr[1].type = INPUT_MOUSE
        arr[1].mi.dwFlags = MOUSEEVENTF_MIDDLEUP

        if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32"):
            ctypes.windll.user32.SendInput(2, arr, _SZ)
            return True
        return False
