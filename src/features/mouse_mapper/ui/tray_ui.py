from __future__ import annotations

import os
import subprocess
import sys
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


def is_admin() -> bool:
    """Check if current process has elevated Administrator privileges."""
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


class TrayUI:
    def __init__(
        self,
        logic: MouseMapperLogic,
        on_settings: Callable | None = None,
        title: str = "RightWheel",
        hook_service: Any = None,
    ) -> None:
        self._logic        = logic
        self._on_settings  = on_settings
        self._title        = title
        self._hook_service = hook_service
        self._icon: pystray.Icon | None = None

    def _build_menu(self) -> pystray.Menu:
        items = [
            pystray.MenuItem(
                lambda item: t("tray.enable"),
                self._toggle,
                checked=lambda item: self._logic.enabled,
                default=True,
            ),
            pystray.Menu.SEPARATOR,
        ]
        if self._on_settings:
            items.append(pystray.MenuItem(lambda item: t("tray.settings"), self._settings))
            items.append(pystray.Menu.SEPARATOR)

        if not is_admin():
            items.append(pystray.MenuItem(lambda item: "🛡️ " + t("tray.run_as_admin", "Chạy với quyền Administrator"), self._run_as_admin))
        items.append(pystray.MenuItem(lambda item: "📋 " + t("tray.copy_diagnostics", "Sao chép chẩn đoán chuột"), self._copy_diagnostics))
        items.append(pystray.Menu.SEPARATOR)

        items.append(pystray.MenuItem(lambda item: t("tray.restart"), self._restart))
        items.append(pystray.MenuItem(lambda item: t("tray.exit"), self._exit))
        return pystray.Menu(*items)

    def _run_as_admin(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Relaunch RightWheel elevated with Administrator privileges."""
        import ctypes
        args = " ".join(f'"{a}"' for a in sys.argv[1:])
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, args, None, 1
            )
            icon.stop()
        except Exception:
            pass

    def _copy_diagnostics(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Export mouse hook and environment diagnostics to clipboard."""
        import ctypes
        import platform
        user32 = ctypes.windll.user32
        swapped = bool(user32.GetSystemMetrics(23))
        admin = is_admin()

        info = [
            "=== RIGHTWHEEL MOUSE DIAGNOSTICS ===",
            f"OS: {platform.platform()} (Build {platform.version()})",
            f"Architecture: {platform.machine()}",
            f"Admin Privileges (UIPI): {'YES' if admin else 'NO (Run as Admin recommended)'}",
            f"Mouse Buttons Swapped (Left-hand): {'YES' if swapped else 'NO'}",
            f"Mapper Enabled: {self._logic.enabled}",
            f"Move Threshold: {getattr(self._logic._cfg, 'move_threshold', 16)}px",
        ]
        hook_svc = self._hook_service
        if hook_svc:
            alive = getattr(hook_svc, "is_hook_alive", False)
            stats = getattr(hook_svc, "stats", {})
            hook_id = getattr(hook_svc, "_hook_id", None)
            info.append(f"Hook Alive: {alive} (ID: 0x{hook_id:X})" if hook_id else f"Hook Alive: {alive}")
            info.append(f"Hook Stats: RMB Down={stats.get('rmb_down', 0)}, RMB Up={stats.get('rmb_up', 0)}, Moves={stats.get('moves', 0)}, Scrolls={stats.get('scroll', 0)}, Re-hooks={stats.get('rehook_count', 0)}")
        else:
            info.append("Hook Service: Reference not linked")

        text = "\n".join(info)
        try:
            import tkinter as tk
            r = tk.Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(text)
            r.update()
            r.destroy()
        except Exception:
            pass

    def run(self) -> None:
        self._icon = pystray.Icon(
            name="RightWheel",
            icon=_make_icon(self._logic.enabled),
            title=self._title,
            menu=self._build_menu(),
        )
        self._icon.run()

    def refresh_menu(self) -> None:
        if self._icon:
            self._icon.menu = self._build_menu()

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

    def _restart(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        icon.stop()
        # PyInstaller onefile sets _MEIPASS2 to the temp extraction dir; execv
        # inherits it, so the relaunched process reuses the OLD dir (mid-cleanup
        # by the exiting one) instead of extracting fresh — drop it so the
        # bootloader re-extracts. No-op when running from source (unset).
        env = os.environ.copy()
        for k in list(env.keys()):
            if k == "_MEIPASS2" or k.startswith("_PYI_"):
                env.pop(k, None)
        env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        args_str = " ".join(f'"{a}"' for a in sys.argv[1:])
        cmd = f'ping 127.0.0.1 -n 2 > nul & "{sys.executable}" {args_str}'.strip()
        subprocess.Popen(
            cmd,
            shell=True,
            env=env,
            creationflags=0x00000008 | 0x00000200,  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            close_fds=True,
        )
        sys.exit(0)
