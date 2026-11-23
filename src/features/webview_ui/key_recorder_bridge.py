"""Key combo capture helper for WebView2 bridge using Win32 GetAsyncKeyState."""
from __future__ import annotations

import ctypes
import time

_MODIFIER_VKS = {
    0x11: "ctrl",
    0xA2: "ctrl",
    0xA3: "ctrl",
    0x12: "alt",
    0xA4: "alt",
    0xA5: "alt",
    0x10: "shift",
    0xA0: "shift",
    0xA1: "shift",
    0x5B: "win",
    0x5C: "win",
}

_SPECIAL_VKS = {
    0x08: "backspace",
    0x09: "tab",
    0x0D: "enter",
    0x1B: "esc",
    0x20: "space",
    0x21: "pageup",
    0x22: "pagedown",
    0x23: "end",
    0x24: "home",
    0x25: "left",
    0x26: "up",
    0x27: "right",
    0x28: "down",
    0x2C: "prtsc",
    0x2D: "insert",
    0x2E: "delete",
    0xAD: "volumemute",
    0xAE: "volumedown",
    0xAF: "volumeup",
    0xB0: "medianext",
    0xB1: "mediaprev",
    0xB2: "mediastop",
    0xB3: "mediaplaypause",
    0xBA: ";",
    0xBB: "=",
    0xBC: ",",
    0xBD: "-",
    0xBE: ".",
    0xBF: "/",
    0xC0: "`",
    0xDB: "[",
    0xDC: "\\",
    0xDD: "]",
    0xDE: "'",
}


def capture_next_key_combo(timeout_sec: float = 6.0) -> dict:
    """Poll Win32 key state briefly to capture a user hotkey combination.

    Pressing Esc alone cancels capture cleanly.
    """
    try:
        user32 = ctypes.windll.user32
    except Exception as exc:
        return {"ok": False, "error": {"code": "KEY_CAPTURE_UNAVAILABLE", "message": str(exc)}}

    # Flush any already-held keys briefly before polling
    time.sleep(0.08)
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        mods: list[str] = []
        for vk, name in _MODIFIER_VKS.items():
            if user32.GetAsyncKeyState(vk) & 0x8000 and name not in mods:
                mods.append(name)

        for vk in range(0x08, 0xE0):
            if vk in _MODIFIER_VKS:
                continue
            if user32.GetAsyncKeyState(vk) & 0x8000:
                if vk == 0x1B and not mods:
                    return {
                        "ok": False,
                        "error": {"code": "KEY_CAPTURE_CANCELLED", "message": "Cancelled by Esc"},
                    }
                key_name = _SPECIAL_VKS.get(vk)
                if not key_name:
                    if 0x30 <= vk <= 0x5A:
                        key_name = chr(vk).lower()
                    elif 0x60 <= vk <= 0x69:
                        key_name = f"num{vk - 0x60}"
                    elif 0x70 <= vk <= 0x87:
                        key_name = f"f{vk - 0x6F}"
                if key_name:
                    combo = "+".join([*mods, key_name]) if mods else key_name
                    return {"ok": True, "data": {"keys": combo}}
        time.sleep(0.025)

    return {
        "ok": False,
        "error": {"code": "KEY_CAPTURE_TIMEOUT", "message": "Timed out waiting for key press"},
    }
