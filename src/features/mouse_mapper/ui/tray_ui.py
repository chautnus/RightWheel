from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pystray
from PIL import Image, ImageDraw

from features.i18n import t

if TYPE_CHECKING:
    from ..logic.mouse_mapper_logic import MouseMapperLogic


def _make_icon(enabled: bool) -> Image.Image:
    size = 64
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (70, 180, 70) if enabled else (180, 70, 70)
    draw.ellipse([8, 8, size - 8, size - 8], fill=color)
    return img


class TrayUI:
    def __init__(
        self,
        logic: MouseMapperLogic,
        on_settings: Callable | None = None,
        title: str = "RightWheel",
    ) -> None:
        self._logic       = logic
        self._on_settings = on_settings
        self._title       = title
        self._icon: pystray.Icon | None = None

    def run(self) -> None:
        items = [
            pystray.MenuItem(
                t("tray.enable"),
                self._toggle,
                checked=lambda item: self._logic.enabled,
                default=True,
            ),
            pystray.Menu.SEPARATOR,
        ]
        if self._on_settings:
            items.append(pystray.MenuItem(t("tray.settings"), self._settings))
            items.append(pystray.Menu.SEPARATOR)
        items.append(pystray.MenuItem(t("tray.exit"), self._exit))

        self._icon = pystray.Icon(
            name="RightWheel",
            icon=_make_icon(self._logic.enabled),
            title=self._title,
            menu=pystray.Menu(*items),
        )
        self._icon.run()

    def update_title(self, title: str) -> None:
        self._title = title
        if self._icon:
            self._icon.title = title

    def _toggle(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._logic.enabled = not self._logic.enabled
        icon.icon = _make_icon(self._logic.enabled)

    def _settings(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        if self._on_settings:
            self._on_settings()

    def _exit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        icon.stop()
