"""Quick preview launcher for the modernized RightWheel Settings UI (WebView2 or Tkinter)."""
import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from src.features.webview_ui.launcher import is_webview_available, get_preferred_ui_engine


def main() -> None:
    view = "settings"
    if "--welcome" in sys.argv:
        view = "welcome"
    elif "--wizard" in sys.argv:
        view = "wizard"

    if "--tkinter" not in sys.argv and is_webview_available() and get_preferred_ui_engine() == "webview":
        from src.features.webview_ui.host import run_host
        run_host(["--webview-host", "--view", view])
        return

    # Tkinter fallback preview
    import tkinter as tk
    import features.i18n as i18n
    from features.shortcut_panel.logic.panel_logic import PanelLogic
    from features.shortcut_panel.ui.settings_window import SettingsWindow

    i18n.init()
    root = tk.Tk()
    root.withdraw()
    logic = PanelLogic()
    win = SettingsWindow(root, logic)
    win.show()
    win._switch_tab("gestures")
    if win._win:
        win._win.lift()
        win._win.focus_force()
    root.mainloop()


if __name__ == "__main__":
    main()
