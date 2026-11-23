"""RightWheel v3.0.0 — system tray app entry point with WebView2 & Tkinter fallback."""
from __future__ import annotations

import sys
from typing import Any

if sys.platform != "win32":
    sys.exit("RightWheel only runs on Windows 10/11.")

from src.core.app_paths import log_debug
from src.core.crash_reporter import install_crash_handlers
from src.core.dpi_helper import enable_high_dpi_awareness
from src.core import memory_manager
from src.core.single_instance import SingleInstanceGuard
from src.core.store_license_service import get_license_service, StoreLicenseStatus

# 0. Early branch for isolated WebView2 child process
if "--webview-host" in sys.argv:
    enable_high_dpi_awareness()
    from src.features.webview_ui.host import run_host
    rc = run_host(sys.argv[1:])
    if rc != 0:
        log_debug(f"WebView2 host exited with code {rc}")
    sys.exit(rc)

# 1. Install global crash handlers early
install_crash_handlers()

# 2. Windows High-DPI Awareness
enable_high_dpi_awareness()

# 3. Single instance guard
instance_guard = SingleInstanceGuard()
if not instance_guard.acquire():
    sys.exit(0)

import features.i18n as i18n
from features.mouse_mapper import MouseHookService, MouseMapperLogic
from features.mouse_mapper.ui.tray_ui import TrayUI
from features.mouse_mapper.ui.trail_overlay import TrailOverlay
from features.mouse_mapper.logic.tab_switch_logic import handle_scroll_for_tab_switch
from features.shortcut_panel import PanelLogic, PanelWindow
from src.features.webview_ui.launcher import WebViewLauncher


def main() -> None:
    # Initialize i18n
    i18n.init()

    # Core mouse logic
    mapper = MouseMapperLogic()

    # Shortcut panel & Tkinter fallback window
    panel = PanelLogic()
    panel_window = PanelWindow(panel)
    trail = TrailOverlay(getattr(panel_window, "_root", None))

    launcher = WebViewLauncher()

    def open_settings_adaptive() -> None:
        launcher.launch_or_fallback("settings", fallback_fn=panel_window.open_settings)

    def open_welcome_adaptive() -> None:
        from features.shortcut_panel.ui.welcome_window import WelcomeWindow
        launcher.launch_or_fallback(
            "welcome",
            fallback_fn=lambda: WelcomeWindow(panel_window._root, panel).show(),
        )

    mapper.panel = panel
    panel.on_open_settings = open_settings_adaptive

    def on_gesture_start_wrap(x: int, y: int) -> None:
        memory_manager.notify_activity()
        trail.start(x, y)

    def on_gesture_end_wrap() -> None:
        memory_manager.notify_activity()
        trail.stop()

    mapper.on_gesture_start = on_gesture_start_wrap
    mapper.on_gesture_end = on_gesture_end_wrap

    # Show modern Welcome onboarding on first launch if enabled
    from src.core.config_service import load_app_settings
    app_settings = load_app_settings()
    if app_settings.get("show_welcome", True) and "--background" not in sys.argv and "--startup" not in sys.argv:
        launcher.launch_or_fallback("welcome")

    # Global mouse hook
    hook = MouseHookService(
        on_event=mapper.handle,
        wants_move_events=mapper.wants_moves,
        on_scroll_modifier=handle_scroll_for_tab_switch,
    )
    hook.start()

    # Start proactive memory compaction daemon (idle trim ~40MB RAM)
    memory_manager.start_periodic_trim(interval_s=300.0, min_idle_s=30.0)

    # License check
    lic_svc = get_license_service()
    st = lic_svc.get_status()
    app_name = i18n.t("app.name", "RightWheel")
    if st.get("is_pro"):
        tray_title = f"{app_name} (Pro)"
    elif st.get("is_trial"):
        tray_title = i18n.t("tray.trial", n=st.get("days_remaining", 30))
    else:
        tray_title = i18n.t("tray.activate", "RightWheel — Trial Expired")

    tray_ui = TrayUI(
        mapper,
        on_settings=open_settings_adaptive,
        title=tray_title,
    )

    # Monitor trial expiration in background
    lic_svc.start_expiry_monitor(
        on_expired_callback=lambda: tray_ui.update_title(i18n.t("tray.activate", "RightWheel — Trial Expired"))
    )

    try:
        tray_ui.run()
    finally:
        memory_manager.stop_periodic_trim()
        hook.stop()
        instance_guard.release()


if __name__ == "__main__":
    main()
