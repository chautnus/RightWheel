"""Quick preview launcher for the modernized RightWheel Settings & Gestures UI."""
import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import tkinter as tk
import features.i18n as i18n
from features.shortcut_panel.logic.panel_logic import PanelLogic
from features.shortcut_panel.ui.settings_window import SettingsWindow


def main() -> None:
    i18n.init()
    root = tk.Tk()
    root.withdraw()
    logic = PanelLogic()
    win = SettingsWindow(root, logic)
    win.show()
    # Switch to gestures tab so user sees it immediately
    win._switch_tab("gestures")
    if win._win:
        win._win.lift()
        win._win.focus_force()
    root.mainloop()


if __name__ == "__main__":
    main()
