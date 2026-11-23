"""Clipboard and web actions for multi-step Sequence items (aligned with Mousehotkey / RightWheel ADR-013)."""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import logging
import os
import re
import subprocess
import sys
from typing import Any
import urllib.parse
import webbrowser

_log = logging.getLogger("touchpadgesture")

GEMINI_URL = "https://gemini.google.com/app"


def get_clipboard_text() -> str:
    """Read current clipboard text via raw Win32 API (no Tkinter dependency)."""
    CF_UNICODETEXT = 13
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    try:
        user32.GetClipboardData.argtypes = [wt.UINT]
        user32.GetClipboardData.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalUnlock.restype = wt.BOOL

        if not user32.OpenClipboard(None):
            return ""
        try:
            h = user32.GetClipboardData(CF_UNICODETEXT)
            if not h:
                return ""
            locked = kernel32.GlobalLock(h)
            if not locked:
                return ""
            try:
                text = ctypes.wstring_at(locked)
            finally:
                kernel32.GlobalUnlock(h)
            return text
        finally:
            user32.CloseClipboard()
    except Exception as exc:
        _log.warning(f"get_clipboard_text() failed: {exc}")
        return ""


def normalize_url(url: str) -> str:
    """Normalize URL string by prepending https:// when no scheme is present."""
    clean = str(url or "").strip()
    if not clean:
        return ""
    if "://" not in clean and not clean.startswith(("mailto:", "ms-settings:")):
        return f"https://{clean}"
    return clean


def open_url_default_browser(url: str) -> str:
    """Open URL in the system default browser out-of-process (avoids in-process COM/DDE UI hang)."""
    norm = normalize_url(url)
    if not norm:
        return ""
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.AllowSetForegroundWindow(0xFFFFFFFF)
        except Exception:
            pass
        browser_path = get_default_browser_path()
        if browser_path:
            try:
                subprocess.Popen([browser_path, norm], shell=False)
                _log.debug(f"open_url_default_browser() browser_path={browser_path!r} url={norm!r}")
                return norm
            except Exception as exc:
                _log.warning(f"open_url_default_browser() browser launch failed: {exc}")
        # Secondary fallback: standard Windows URL protocol handler out-of-process (never explorer.exe)
        try:
            subprocess.Popen(["rundll32.exe", "url.dll,FileProtocolHandler", norm], shell=False)
            _log.debug(f"open_url_default_browser() rundll32 url={norm!r}")
            return norm
        except Exception as exc:
            _log.warning(f"open_url_default_browser() rundll32 failed: {exc}")
    webbrowser.open(norm)
    _log.debug(f"open_url_default_browser() webbrowser.open url={norm!r}")
    return norm


def get_default_browser_path() -> str:
    """Resolve the full executable path (e.g. 'C:\\Program Files\\...\\chrome.exe') of Windows default browser."""
    if sys.platform != "win32":
        return ""
    try:
        import winreg
        prog_id = ""
        for subkey in (
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoiceLatest\ProgId",
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice",
        ):
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey) as key:
                    val, _ = winreg.QueryValueEx(key, "ProgId")
                    if val:
                        prog_id = str(val)
                        break
            except OSError:
                continue
        if not prog_id:
            return ""
        with winreg.OpenKey(
            winreg.HKEY_CLASSES_ROOT,
            rf"{prog_id}\shell\open\command",
        ) as cmd_key:
            cmd_val, _ = winreg.QueryValueEx(cmd_key, None)
        raw = str(cmd_val or "").strip()
        if raw.startswith('"'):
            end_q = raw.find('"', 1)
            if end_q != -1:
                exe = raw[1:end_q]
                if os.path.isfile(exe):
                    return exe
        m = re.search(r'([a-zA-Z]:\\[^"*?<>|]+?\.exe)', raw, flags=re.IGNORECASE)
        if m and os.path.isfile(m.group(1)):
            return m.group(1)
        return ""
    except Exception:
        return ""


def get_default_browser_exe() -> str:
    """Resolve the executable basename (e.g. 'chrome.exe') of Windows default https browser."""
    if sys.platform != "win32":
        return ""
    full_path = get_default_browser_path()
    if full_path:
        return os.path.basename(full_path).lower()
    try:
        import winreg
        prog_id = ""
        for subkey in (
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoiceLatest\ProgId",
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice",
        ):
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey) as key:
                    val, _ = winreg.QueryValueEx(key, "ProgId")
                    if val:
                        prog_id = str(val)
                        break
            except OSError:
                continue
        if not prog_id:
            return ""
        with winreg.OpenKey(
            winreg.HKEY_CLASSES_ROOT,
            rf"{prog_id}\shell\open\command",
        ) as cmd_key:
            cmd_val, _ = winreg.QueryValueEx(cmd_key, None)
        m = re.search(r'([^\\/:*?"<>|]+\.exe)', str(cmd_val), flags=re.IGNORECASE)
        return m.group(1).lower() if m else ""
    except Exception:
        return ""


_LOADING_TAB_PREFIXES = ("untitled", "new tab", "th" + chr(0x1EBB) + " m" + chr(0x1EDB) + "i", "about:blank")


def wait_until_browser_tab_ready(timeout_s: float = 5.0) -> bool:
    """Wait until the active browser tab title leaves 'Untitled'/'New Tab' (up to timeout_s)."""
    if sys.platform != "win32":
        return True
    try:
        import time
        from src.features.action_dispatcher.window_manager import get_window_title

        deadline = time.perf_counter() + timeout_s
        waited_for_untitled = False
        while time.perf_counter() < deadline:
            fg = ctypes.windll.user32.GetForegroundWindow()
            title = (get_window_title(fg) or "").lstrip("\u200e\u200f ").lower()
            if any(title.startswith(p) for p in _LOADING_TAB_PREFIXES):
                waited_for_untitled = True
                time.sleep(0.15)
                continue
            if waited_for_untitled:
                # Give page autofocus script a brief moment to focus the input field
                time.sleep(0.25)
            return True
    except Exception:
        pass
    return False


def focus_default_browser_window() -> bool:
    """Ensure the Windows default browser window is in the foreground before sending keystrokes."""
    if sys.platform != "win32":
        return False
    try:
        from src.features.action_dispatcher.window_manager import (
            WindowManager,
            focus_window,
            get_window_exe,
        )
        wm = WindowManager()
        target_exe = get_default_browser_exe()
        fg = wm.get_foreground_window()
        if fg and target_exe and get_window_exe(fg).lower() == target_exe:
            return True

        common_browsers = {"chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe", "vivaldi.exe", "coccoc.exe"}
        for w in wm.get_recent_windows():
            exe = str(w.get("exe", "")).lower()
            if (target_exe and exe == target_exe) or (not target_exe and exe in common_browsers):
                ok = focus_window(int(w["hwnd"]))
                _log.debug(f"focus_default_browser_window() exe={exe!r} hwnd={w['hwnd']} ok={ok}")
                return ok
    except Exception as exc:
        _log.warning(f"focus_default_browser_window() failed: {exc}")
    return False


_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")


def clipboard_has_image() -> bool:
    """Return True if the Windows clipboard currently contains an image (DIB/Bitmap or image file)."""
    if sys.platform != "win32" or not hasattr(ctypes, "windll"):
        return False
    CF_BITMAP = 2
    CF_DIB = 8
    CF_HDROP = 15
    CF_DIBV5 = 17
    user32 = ctypes.windll.user32
    try:
        for fmt in (CF_DIB, CF_DIBV5, CF_BITMAP):
            if user32.IsClipboardFormatAvailable(fmt):
                return True
        if user32.IsClipboardFormatAvailable(CF_HDROP):
            if user32.OpenClipboard(None):
                try:
                    h_drop = user32.GetClipboardData(CF_HDROP)
                    if h_drop:
                        shell32 = ctypes.windll.shell32
                        count = shell32.DragQueryFileW(h_drop, 0xFFFFFFFF, None, 0)
                        for idx in range(min(int(count), 10)):
                            buf = ctypes.create_unicode_buffer(520)
                            if shell32.DragQueryFileW(h_drop, idx, buf, 520):
                                if buf.value.lower().endswith(_IMAGE_EXTENSIONS):
                                    return True
                finally:
                    user32.CloseClipboard()
    except Exception as exc:
        _log.warning(f"clipboard_has_image() failed: {exc}")
    return False


def _derive_base_url(url_template: str, base_url: str = "") -> str:
    """Derive a clean target page URL (without query placeholders) for paste_submit mode."""
    if base_url and base_url.strip():
        return normalize_url(base_url)
    cleaned = str(url_template or "").strip()
    if "{text}" in cleaned:
        idx = cleaned.find("?")
        if idx != -1:
            cleaned = cleaned[:idx]
    return normalize_url(cleaned)


def _open(url: str) -> None:
    try:
        open_url_default_browser(url)
    except Exception as exc:
        _log.warning(f"clipboard_web_actions._open() failed: {exc}")


def execute_url_clipboard(
    url_template: str,
    prompt: str = "",
    mode: str = "url_query",
    base_url: str = "",
    auto_submit: bool = True,
    send_key_fn: Any = None,
    send_text_fn: Any = None,
) -> None:
    """Execute WebClip step: URL query for short text, or smart paste+prompt+enter for images/AI."""
    import time

    has_image = clipboard_has_image()
    clip_text = "" if has_image else get_clipboard_text()
    clean_prompt = str(prompt or "").strip()

    if clean_prompt and clip_text:
        combined_text = f"{clean_prompt}\n{clip_text}"
    else:
        combined_text = clean_prompt or clip_text

    use_paste_flow = (
        has_image
        or mode == "paste_submit"
        or "{text}" not in url_template
        or len(combined_text) > 1800
    )

    if not use_paste_flow:
        encoded = urllib.parse.quote(combined_text)
        _open(url_template.replace("{text}", encoded))
        return

    target_url = _derive_base_url(url_template, base_url)
    _open(target_url)
    time.sleep(0.5)
    focus_default_browser_window()
    wait_until_browser_tab_ready(timeout_s=5.0)

    if send_key_fn:
        if has_image or clip_text:
            send_key_fn("ctrl+v")
            time.sleep(0.55 if has_image else 0.15)
        if clean_prompt and send_text_fn:
            send_text_fn(f" {clean_prompt}" if (has_image or clip_text) else clean_prompt)
            time.sleep(0.15)
        if auto_submit:
            send_key_fn("enter")


def execute_gemini(prompt: str) -> None:
    """Open Gemini with `prompt` followed by the clipboard text, both URL-encoded."""
    text = get_clipboard_text()
    query = f"{prompt} {text}" if prompt.strip() else text
    _open(f"{GEMINI_URL}?prompt={urllib.parse.quote(query)}")
