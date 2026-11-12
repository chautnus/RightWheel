"""Sequence steps that read the clipboard and open a URL built from it."""
import ctypes
import ctypes.wintypes as wt
import logging
import urllib.parse
import webbrowser

_log = logging.getLogger("mousehotkey")

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


def _open(url: str) -> None:
    try:
        webbrowser.open(url)
        _log.debug(f"clipboard_web_actions._open()  url={url!r}")
    except Exception as exc:
        _log.warning(f"clipboard_web_actions._open() failed: {exc}")


def execute_url_clipboard(url_template: str) -> None:
    """Substitute clipboard text (URL-encoded) into {text} placeholder, then open URL."""
    encoded = urllib.parse.quote(get_clipboard_text())
    _open(url_template.replace("{text}", encoded))


def execute_gemini(prompt: str) -> None:
    """Open Gemini with `prompt` followed by the clipboard text, both URL-encoded."""
    text = get_clipboard_text()
    query = f"{prompt} {text}" if prompt.strip() else text
    _open(f"{GEMINI_URL}?prompt={urllib.parse.quote(query)}")
