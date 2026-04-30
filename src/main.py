"""MouseHotkey — system tray app entry point."""
import sys

# Guard: Windows only
if sys.platform != "win32":
    sys.exit("MouseHotkey only runs on Windows.")

from features.mouse_mapper import HotkeyConfig, MouseHookService, MouseMapperLogic
from features.mouse_mapper.ui.tray_ui import TrayUI


def main() -> None:
    config = HotkeyConfig(move_threshold=8)
    logic = MouseMapperLogic(config)
    hook = MouseHookService(on_event=logic.handle, wants_move_events=logic.wants_moves)

    hook.start()
    try:
        TrayUI(logic).run()   # blocks until user clicks Exit
    finally:
        hook.stop()


if __name__ == "__main__":
    main()
