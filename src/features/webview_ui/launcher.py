"""Launcher for isolated WebView2 child process with automatic Tkinter fallback."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

from src.core.app_paths import get_config_root, log_debug
from src.features.webview_ui.bridge_api import resolve_ui_index_path


def get_preferred_ui_engine(settings_path: Path | None = None) -> str:
    """Read ui_engine from app_settings.json (default: 'webview')."""
    path = settings_path or (get_config_root() / "app_settings.json")
    if not path.exists():
        return "webview"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        engine = str(data.get("ui_engine", "webview")).lower()
        return engine if engine in ("webview", "tkinter") else "webview"
    except Exception:
        return "webview"


def is_webview_available() -> bool:
    """Verify ui_dist bundle exists and pywebview is importable.

    Uses find_spec instead of a real `import webview` so the ~8MB module graph
    (pywebview + its deps) never loads into the long-lived main process — the
    real import only happens inside the isolated --webview-host subprocess
    (see host.py), which is the only place that actually needs the library.
    """
    if resolve_ui_index_path() is None:
        return False
    try:
        import importlib.util
        return importlib.util.find_spec("webview") is not None
    except Exception:
        return False


def _build_clean_child_env() -> dict[str, str]:
    """Reset PyInstaller onefile environment variables so child subprocess unpacks cleanly."""
    env = os.environ.copy()
    for k in list(env.keys()):
        if k == "_MEIPASS2" or k.startswith("_PYI_"):
            env.pop(k, None)
    env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    return env


class WebViewLauncher:
    """Spawns and tracks isolated --webview-host subprocesses per view."""

    def __init__(self) -> None:
        self._procs: dict[str, subprocess.Popen] = {}

    def launch_or_fallback(self, view: str, fallback_fn: Callable[[], None] | None = None) -> bool:
        """Open WebView2 subprocess if enabled & available; otherwise call fallback_fn if provided."""
        if get_preferred_ui_engine() != "webview" or not is_webview_available():
            log_debug(f"WebViewLauncher using Tkinter fallback for view={view}")
            if fallback_fn is not None:
                fallback_fn()
            return False

        existing = self._procs.get(view)
        if existing is not None and existing.poll() is None:
            return True

        try:
            cmd = (
                [sys.executable, "--webview-host", "--view", view]
                if getattr(sys, "frozen", False)
                else [sys.executable, "-m", "src.main", "--webview-host", "--view", view]
            )
            proc = subprocess.Popen(cmd, env=_build_clean_child_env(), close_fds=True)
            self._procs[view] = proc
            log_debug(f"WebViewLauncher spawned view={view} pid={proc.pid}")
            return True
        except Exception as exc:
            log_debug(f"WebViewLauncher failed for {view}, falling back to Tkinter: {exc}")
            if fallback_fn is not None:
                fallback_fn()
            return False
