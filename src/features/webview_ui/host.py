"""Isolated Edge WebView2 host process entry point (STA main thread)."""
from __future__ import annotations

import argparse
import sys

from src.core.app_paths import get_config_root, log_debug
from src.features.webview_ui.bridge_api import WebViewBridgeAPI, resolve_ui_index_path

_WINDOW_GEOMETRY = {
    "settings": ("RightWheel — Settings", 1040, 720),
    "welcome": ("RightWheel — Welcome", 720, 560),
    "wizard": ("RightWheel — Onboarding", 760, 600),
}


def run_host(argv: list[str] | None = None) -> int:
    """Launch pywebview Edge WebView2 window for the requested view."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--webview-host", action="store_true")
    parser.add_argument("--view", default="settings", choices=["settings", "welcome", "wizard"])
    args, _ = parser.parse_known_args(argv if argv is not None else sys.argv[1:])

    index_path = resolve_ui_index_path()
    if not index_path:
        log_debug("WebView2 host aborted: ui_dist/index.html not found.")
        return 2

    try:
        import webview  # type: ignore[import-not-found]
    except Exception as exc:
        log_debug(f"WebView2 host import failed: {exc}")
        return 3

    storage_dir = get_config_root() / "webview2_cache"
    storage_dir.mkdir(parents=True, exist_ok=True)

    title, width, height = _WINDOW_GEOMETRY[args.view]
    api = WebViewBridgeAPI(default_view=args.view)
    try:
        win = webview.create_window(
            title=title,
            url=str(index_path),
            js_api=api,
            width=width,
            height=height,
            min_size=(640, 480),
            background_color="#0b1326",
        )
        api.set_window(win)
        log_debug(f"WebView2 host starting view={args.view} url={index_path}")
        webview.start(
            gui="edgechromium",
            http_server=True,
            storage_path=str(storage_dir),
            debug=False,
        )
        return 0
    except Exception as exc:
        log_debug(f"WebView2 host runtime error (view={args.view}): {exc}")
        return 4
