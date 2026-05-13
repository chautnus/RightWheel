from __future__ import annotations

import threading

from ..services import hotkey_service
from ..types.mouse_mapper_types import (
    HotkeyConfig,
    MapperState,
    MouseEvent,
    ScrollDirection,
)


class MouseMapperLogic:
    def __init__(self, config: HotkeyConfig | None = None) -> None:
        self._cfg      = config or HotkeyConfig()
        self._state    = MapperState.IDLE
        self._lock     = threading.Lock()
        self._alt_held = False
        self._down_x   = 0
        self._down_y   = 0
        self.enabled   = True

    def handle(self, event: MouseEvent) -> bool:
        if not self.enabled:
            return False
        with self._lock:
            if event.kind == "right_down": return self._on_right_down(event.x, event.y)
            if event.kind == "right_up":   return self._on_right_up()
            if event.kind == "scroll":     return self._on_scroll(event.scroll_dir)
            if event.kind == "move":       return self._on_move(event.x, event.y)
        return False

    def wants_moves(self) -> bool:
        """Fast check (no lock) — True only while waiting to decide gesture vs scroll."""
        return self._state == MapperState.RIGHT_HELD

    # ── state transitions ──────────────────────────────────────────────────

    def _on_right_down(self, x: int, y: int) -> bool:
        self._state  = MapperState.RIGHT_HELD
        self._down_x = x
        self._down_y = y
        return True   # always suppress; re-inject on right_up or move

    def _on_move(self, x: int, y: int) -> bool:
        if self._state != MapperState.RIGHT_HELD:
            return False
        dx = abs(x - self._down_x)
        dy = abs(y - self._down_y)
        if dx >= self._cfg.move_threshold or dy >= self._cfg.move_threshold:
            self._state = MapperState.GESTURE
            hotkey_service.inject_right_down()   # retroactive — Edge can now track
        return False   # never suppress mouse moves

    def _on_scroll(self, direction: ScrollDirection | None) -> bool:
        if self._state not in (MapperState.RIGHT_HELD, MapperState.SCROLLING):
            return False
        self._state = MapperState.SCROLLING
        panel = getattr(self, "panel", None)
        if panel:
            delta = -1 if direction == ScrollDirection.UP else 1
            if not self._alt_held:
                panel.show()   # show() resets index to 0
                self._alt_held = True
            else:
                panel.navigate(delta)
        else:
            forward = (direction == ScrollDirection.DOWN)
            if not self._alt_held:
                hotkey_service.begin_switch(forward)
                self._alt_held = True
            else:
                hotkey_service.cycle(forward)
        return True

    def _on_right_up(self) -> bool:
        prev        = self._state
        self._state = MapperState.IDLE

        # Guard: spurious right_up received when already IDLE (e.g. app just
        # started while RMB was held, or state was reset externally).
        if prev == MapperState.IDLE:
            return False

        if self._alt_held:
            panel = getattr(self, "panel", None)
            if not panel:
                hotkey_service.end_switch()
            self._alt_held = False

        if prev == MapperState.RIGHT_HELD:
            # Short tap — re-inject clean down+up so context menu appears
            hotkey_service.inject_right_click()
            return True

        if prev == MapperState.GESTURE:
            # right_down was already injected retroactively; let real right_up
            # reach the app so the gesture completes naturally.
            return False

        # SCROLLING: right_down was never sent to any app. Suppress right_up so
        # no context menu appears. OS hardware state (GetAsyncKeyState) is already
        # correct; apps that check GetKeyState may lag briefly but recover on next
        # mouse event — acceptable trade-off vs context menu appearing.
        return True
