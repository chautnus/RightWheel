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
from features.mouse_mapper.ui.gesture_guide_overlay import GestureGuideOverlay
from features.mouse_mapper.logic.gesture_recognizer import normalize_directions
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
    trail = TrailOverlay(lambda: getattr(panel_window, "_root", None))

    launcher = WebViewLauncher()

    def open_settings_adaptive() -> None:
        launcher.launch_or_fallback("settings", fallback_fn=panel_window.open_settings)

    def open_welcome_adaptive() -> None:
        launcher.launch_or_fallback("welcome", fallback_fn=panel_window.open_welcome)

    mapper.panel = panel
    panel.on_open_settings = open_settings_adaptive

    # Gesture Guide Overlay: live directional hints while RMB gesture is held,
    # ported from Touchpad Gesture's F-032. Labels come from the flat "gestures"
    # preset list (prefix-matched against each preset's normalized directions),
    # not a binding_key lookup like the touchpad app, since RightWheel's gesture
    # config has no per-finger-count grouping.
    guide_overlay = GestureGuideOverlay()
    _dir_to_letter = {"UP": "U", "DOWN": "D", "LEFT": "L", "RIGHT": "R"}
    _ALL_GUIDE_DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")
    from features.shortcut_panel.services.intent_service import IntentService
    _guide_intent_svc = IntentService()

    def _guide_keys_to_text(keys: str) -> str:
        for it in _guide_intent_svc.catalog:
            if it.keys == keys:
                return it.title_vi
        return keys

    def _guide_active_presets() -> list[dict]:
        try:
            import ctypes as _ctypes
            from src.core.profile_service import resolve_active_profile_full
            hwnd = _ctypes.windll.user32.GetForegroundWindow()
            prof_res = resolve_active_profile_full(hwnd)
            if prof_res.get("ok"):
                presets = prof_res.get("data", {}).get("effective_gestures", [])
                if presets:
                    return presets
        except Exception:
            pass
        try:
            from features.shortcut_panel.services import config_service
            return config_service.load().get("gestures", [])
        except Exception:
            return []

    def _guide_preset_text(preset: dict) -> str:
        if preset.get("description"):
            return str(preset["description"])
        if preset.get("label"):
            return str(preset["label"])
        keys = str(preset.get("keys") or preset.get("target") or "")
        if keys:
            return _guide_keys_to_text(keys)
        return i18n.t("guide_unassigned", "Chưa gán")

    def _guide_labels_for_path(path: list[str]) -> dict[str, str]:
        presets = _guide_active_presets()
        result: dict[str, str] = {}
        for direction in _ALL_GUIDE_DIRECTIONS:
            if path and direction == path[-1]:
                continue
            candidate_path = path + [_dir_to_letter[direction]]
            best: dict | None = None
            best_len = 0
            for preset in presets:
                if not isinstance(preset, dict) or not preset.get("enabled", True):
                    continue
                preset_dirs = preset.get("directions")
                if not preset_dirs:
                    shape = str(preset.get("shape") or preset.get("direction") or "").strip()
                    preset_dirs = [d.strip().upper() for d in shape.split("_") if d.strip()] if shape else None
                if not preset_dirs:
                    continue
                norm = normalize_directions([d.upper() for d in preset_dirs])
                if norm[: len(candidate_path)] == candidate_path:
                    if best is None or len(norm) < best_len:
                        best = preset
                        best_len = len(norm)
            result[direction] = _guide_preset_text(best) if best else i18n.t("guide_unassigned", "Chưa gán")
        return result

    def on_hold_start_wrap() -> None:
        # Fires on RMB-down, before any movement — show the guide overlay
        # immediately (parity with the touchpad app's 3/4-finger-hold trigger).
        try:
            guide_overlay.start(_guide_labels_for_path([]))
        except Exception:
            pass

    def on_gesture_start_wrap(x: int, y: int) -> None:
        memory_manager.notify_activity()
        trail.start(x, y)

    def on_sector_change_wrap(path: list[str]) -> None:
        letters = [_dir_to_letter[d] for d in path]
        try:
            guide_overlay.update_sectors(path, _guide_labels_for_path(letters))
        except Exception:
            pass

    def on_gesture_end_wrap() -> None:
        memory_manager.notify_activity()
        trail.stop()
        guide_overlay.stop()

    mapper.on_hold_start = on_hold_start_wrap
    mapper.on_gesture_start = on_gesture_start_wrap
    mapper.on_sector_change = on_sector_change_wrap
    mapper.on_gesture_end = on_gesture_end_wrap

    # Show modern Welcome onboarding on first launch if enabled
    from src.core.config_service import load_app_settings
    app_settings = load_app_settings()
    if app_settings.get("show_welcome", True) and "--background" not in sys.argv and "--startup" not in sys.argv:
        open_welcome_adaptive()

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
        hook_service=hook,
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
