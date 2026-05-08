"""RightWheel v2.9.0 — system tray app entry point."""
import sys

if sys.platform != "win32":
    sys.exit("RightWheel only runs on Windows.")

import features.i18n as i18n
from features.licensing import LicenseState, get_info
from features.mouse_mapper import HotkeyConfig, MouseHookService, MouseMapperLogic
from features.mouse_mapper.ui.tray_ui import TrayUI
from features.shortcut_panel import PanelLogic, PanelWindow


def main() -> None:
    # Initialize i18n — auto-detect language from system locale or saved pref
    i18n.init()

    # Core mouse logic
    mapper = MouseMapperLogic(HotkeyConfig(move_threshold=8))

    # Shortcut panel — starts its own tkinter daemon thread
    panel        = PanelLogic()
    panel_window = PanelWindow(panel)
    mapper.panel = panel                                    # scroll-up → show panel
    panel.on_open_settings = panel_window.open_settings    # action → open settings

    # Global mouse hook
    hook = MouseHookService(
        on_event=mapper.handle,
        wants_move_events=mapper.wants_moves,
    )
    hook.start()

    # License check — set tray title based on license state
    lic = get_info()
    app_name = i18n.t("app.name")
    if lic.state == LicenseState.TRIAL_ACTIVE:
        tray_title = i18n.t("tray.trial", n=lic.days_remaining)
    elif lic.state == LicenseState.TRIAL_EXPIRED:
        tray_title = i18n.t("tray.activate")
    else:
        tray_title = app_name

    try:
        TrayUI(mapper, on_settings=panel_window.open_settings,
               title=tray_title).run()
    finally:
        hook.stop()


if __name__ == "__main__":
    main()
