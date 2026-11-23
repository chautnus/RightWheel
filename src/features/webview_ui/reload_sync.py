"""Config file mtime tracker for live-reloading CommandWindow after WebView edits."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from src.core.app_paths import get_config_root


class ConfigReloadWatcher:
    """Lightweight polling watcher using file mtimes (zero extra threads)."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self._dir = config_dir or get_config_root()
        self._targets = ("profiles.json", "app_settings.json", "gestures.json")
        self._mtimes: dict[str, float] = self._snapshot()

    def _snapshot(self) -> dict[str, float]:
        snap: dict[str, float] = {}
        for name in self._targets:
            p = self._dir / name
            try:
                snap[name] = p.stat().st_mtime if p.exists() else 0.0
            except Exception:
                snap[name] = 0.0
        return snap

    def check_and_notify(self, on_change: Callable[[], None]) -> bool:
        """Return True and invoke on_change if any tracked config file changed."""
        current = self._snapshot()
        if current != self._mtimes:
            self._mtimes = current
            on_change()
            return True
        return False
