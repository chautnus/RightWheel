"""Internationalization — t(key) with auto-detect and per-locale font hint."""
from __future__ import annotations

import importlib
import locale
import os
from pathlib import Path

# lang code → module suffix
_SUPPORTED = {"en", "fr", "pt", "es", "it", "vi", "id", "th", "zh"}
_LANG_MAP: dict[str, str] = {
    "fr": "fr", "pt": "pt", "es": "es", "it": "it",
    "vi": "vi", "id": "id", "th": "th",
    "zh": "zh", "zh_cn": "zh", "zh_tw": "zh",
}
# CJK / Thai need different fonts
FONT_OVERRIDE: dict[str, str] = {
    "zh": "Microsoft YaHei",
    "th": "Tahoma",
}

_LANG_FILE = (
    Path(os.environ.get("APPDATA", ".")) / "RightWheel" / "lang.txt"
)

_current: dict[str, str] = {}
_code: str = "en"


# ── public API ────────────────────────────────────────────────────────────────

def t(key: str, **kwargs) -> str:
    """Return translated string, falling back to English, then the key itself."""
    s = _current.get(key)
    if s is None:
        _en = _load("en")
        s = _en.get(key, key)
    return s.format(**kwargs) if kwargs else s


def current() -> str:
    return _code


def ui_font(base: str = "Segoe UI") -> str:
    """Return appropriate font family for current locale."""
    return FONT_OVERRIDE.get(_code, base)


def available() -> list[tuple[str, str]]:
    """Return [(code, native_name), ...] for the language selector."""
    return [
        ("en", "English"), ("fr", "Français"), ("pt", "Português"),
        ("es", "Español"), ("it", "Italiano"), ("vi", "Tiếng Việt"),
        ("id", "Indonesia"), ("th", "ภาษาไทย"), ("zh", "中文"),
    ]


def set_locale(code: str) -> None:
    global _current, _code
    _code = code if code in _SUPPORTED else "en"
    strings = _load(_code)
    _current = strings
    _save_pref(_code)


def init() -> None:
    """Load saved preference, or auto-detect from system locale."""
    saved = _read_pref()
    code  = saved or _detect()
    set_locale(code)


# ── helpers ───────────────────────────────────────────────────────────────────

def _load(code: str) -> dict[str, str]:
    try:
        mod = importlib.import_module(f".{code}", package=__name__)
        return mod.STRINGS
    except Exception:
        return {}


def _detect() -> str:
    try:
        lang = locale.getdefaultlocale()[0] or "en"
        key  = lang.lower().replace("-", "_")
        return _LANG_MAP.get(key, _LANG_MAP.get(key.split("_")[0], "en"))
    except Exception:
        return "en"


def _read_pref() -> str:
    try:
        return _LANG_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _save_pref(code: str) -> None:
    try:
        _LANG_FILE.parent.mkdir(parents=True, exist_ok=True)
        _LANG_FILE.write_text(code, encoding="utf-8")
    except Exception:
        pass
