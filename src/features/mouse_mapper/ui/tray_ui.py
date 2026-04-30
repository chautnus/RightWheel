from __future__ import annotations

from typing import TYPE_CHECKING

import pystray
from PIL import Image, ImageDraw

if TYPE_CHECKING:
    from ..logic.mouse_mapper_logic import MouseMapperLogic


def _make_icon(enabled: bool) -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (70, 180, 70) if enabled else (180, 70, 70)
    draw.ellipse([8, 8, size - 8, size - 8], fill=color)
    return img


class TrayUI:
    def __init__(self, logic: MouseMapperLogic) -> None:
        self._logic = logic
        self._icon: pystray.Icon | None = None

    def run(self) -> None:
        """Blocking call — runs the tray event loop on the calling thread."""
        self._icon = pystray.Icon(
            name="MouseHotkey",
            icon=_make_icon(self._logic.enabled),
            title="MouseHotkey",
            menu=pystray.Menu(
                pystray.MenuItem(
                    "Enable",
                    self._toggle,
                    checked=lambda item: self._logic.enabled,
                    default=True,
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self._exit),
            ),
        )
        self._icon.run()

    # ------------------------------------------------------------------

    def _toggle(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._logic.enabled = not self._logic.enabled
        icon.icon = _make_icon(self._logic.enabled)

    def _exit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        icon.stop()
