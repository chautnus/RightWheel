from __future__ import annotations

from collections.abc import Callable
import threading

from ..services import hotkey_service
from ..types.mouse_mapper_types import (
    HotkeyConfig,
    MapperState,
    MouseEvent,
    ScrollDirection,
)
from ...shortcut_panel.services import (
    config_service,
    shortcut_executor,
)
from .gesture_recognizer import CARDINAL_NAMES, GestureRecognizer


class MouseMapperLogic:
    def __init__(self, config: HotkeyConfig | None = None) -> None:
        if config is None:
            try:
                from src.core.config_service import load_app_settings
                st = load_app_settings()
                val = st.get("swipe_threshold") or st.get("move_threshold")
                if val and isinstance(val, (int, float)) and val > 0:
                    self._cfg = HotkeyConfig(move_threshold=int(val))
                else:
                    self._cfg = HotkeyConfig()
            except Exception:
                self._cfg = HotkeyConfig()
        else:
            self._cfg = config

        self._state      = MapperState.IDLE
        self._lock       = threading.Lock()
        self._alt_held   = False
        self._panel_mode = False   # True = this scroll session opened the panel
        self._down_x     = 0
        self._down_y     = 0
        self.enabled     = True
        self.on_gesture_start: Callable[[int, int], None] | None = None
        self.on_gesture_end: Callable[[], None] | None = None
        # Fires the moment RMB goes down (before any movement) — lets the Gesture
        # Guide Overlay show immediately on hold, matching the touchpad app's
        # 3/4-finger-hold trigger instead of waiting for move_threshold to be crossed.
        self.on_hold_start: Callable[[], None] | None = None
        # Fires with the cardinal-only (U/D/L/R) direction path so far, each time the
        # recognizer commits a NEW sector while the gesture is still being held — used
        # by the Gesture Guide Overlay to show "what happens next" live. Diagonal
        # sectors (DR/DL/UL/UR) are not reported here (the overlay only shows 4
        # cardinal arrows); the real 8-direction matching in finish() is unaffected.
        self.on_sector_change: Callable[[list[str]], None] | None = None
        self._cardinal_path: list[str] = []
        self._gesture_recognizer = GestureRecognizer(threshold=18)

    def handle(self, event: MouseEvent) -> bool:
        if not self.enabled:
            return False
        with self._lock:
            if event.kind == "right_down":   return self._on_right_down(event.x, event.y)
            if event.kind == "right_up":     return self._on_right_up()
            if event.kind == "scroll":       return self._on_scroll(event.scroll_dir)
            if event.kind == "move":         return self._on_move(event.x, event.y)
        return False

    def wants_moves(self) -> bool:
        """Fast check (no lock) — True while waiting to decide gesture vs scroll or tracking gesture."""
        return self._state in (MapperState.RIGHT_HELD, MapperState.GESTURE)

    # ── state transitions ──────────────────────────────────────────────────

    def _on_right_down(self, x: int, y: int) -> bool:
        self._state  = MapperState.RIGHT_HELD
        self._down_x = x
        self._down_y = y
        if self.on_hold_start:
            try:
                self.on_hold_start()
            except Exception:
                pass
        return True   # always suppress; re-inject on right_up or move

    def _maybe_report_sector_change(self, res: dict) -> None:
        if not (res.get("ok") and res.get("data", {}).get("stroke_added") and self.on_sector_change):
            return
        sector = self._gesture_recognizer._directions[-1] if self._gesture_recognizer._directions else None
        cardinal = CARDINAL_NAMES.get(sector) if sector else None
        if cardinal and (not self._cardinal_path or self._cardinal_path[-1] != cardinal):
            self._cardinal_path.append(cardinal)
            try:
                self.on_sector_change(list(self._cardinal_path))
            except Exception:
                pass

    def _on_move(self, x: int, y: int) -> bool:
        if self._state == MapperState.GESTURE:
            res = self._gesture_recognizer.feed_point(x, y)
            self._maybe_report_sector_change(res)
            return False
        if self._state != MapperState.RIGHT_HELD:
            return False
        dx = abs(x - self._down_x)
        dy = abs(y - self._down_y)
        if dx >= self._cfg.move_threshold or dy >= self._cfg.move_threshold:
            self._state = MapperState.GESTURE
            self._cardinal_path = []
            self._gesture_recognizer.reset()
            self._gesture_recognizer.feed_point(self._down_x, self._down_y)
            res0 = self._gesture_recognizer.feed_point(x, y)
            if self.on_gesture_start:
                self.on_gesture_start(self._down_x, self._down_y)
            self._maybe_report_sector_change(res0)
        return False   # never suppress mouse moves

    def _on_scroll(self, direction: ScrollDirection | None) -> bool:
        if self._state not in (MapperState.RIGHT_HELD, MapperState.SCROLLING):
            return False
        self._state = MapperState.SCROLLING
        panel   = getattr(self, "panel", None)
        forward = (direction == ScrollDirection.DOWN)

        if not self._alt_held:
            # First scroll in this RMB session — direction decides mode
            if direction == ScrollDirection.UP and panel:
                # Scroll UP → open shortcut panel
                panel.show()
                self._panel_mode = True
            else:
                # Scroll DOWN (or no panel) → Alt+Tab
                if panel and panel.visible:
                    panel.hide()
                hotkey_service.begin_switch(forward)
                self._panel_mode = False
            self._alt_held = True
        else:
            # Subsequent scrolls — stay in chosen mode
            if self._panel_mode and panel:
                panel.navigate(-1 if direction == ScrollDirection.UP else 1)
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
            if self._panel_mode:
                self._panel_mode = False   # panel stays open; user interacts freely
            else:
                hotkey_service.end_switch()
            self._alt_held = False

        if prev == MapperState.RIGHT_HELD:
            # Short tap (no drag) — on_hold_start already showed the guide overlay;
            # hide it since no gesture actually happened.
            if self.on_gesture_end:
                try:
                    self.on_gesture_end()
                except Exception:
                    pass
            # Short tap — re-inject clean down+up so context menu appears
            hotkey_service.inject_right_click()
            return True

        if prev == MapperState.GESTURE:
            if self.on_gesture_end:
                self.on_gesture_end()

            # Check gesture against active profile presets (with global fallback)
            presets = []
            try:
                import ctypes
                from src.core.profile_service import resolve_active_profile_full
                hwnd = ctypes.windll.user32.GetForegroundWindow() if hasattr(ctypes, "windll") else 0
                prof_res = resolve_active_profile_full(hwnd)
                if prof_res.get("ok"):
                    presets = prof_res.get("data", {}).get("effective_gestures", [])
            except Exception:
                pass
            if not presets:
                presets = config_service.load().get("gestures", [])

            res = self._gesture_recognizer.finish(presets)
            from src.core.app_paths import log_debug

            if res.get("ok") and res.get("data", {}).get("matched"):
                data = res.get("data", {})
                preset = data.get("preset") or {}
                keys = data.get("keys", "")
                act_type = preset.get("type") or ("KEY_COMBO" if keys else "")
                target = preset.get("target") or keys

                log_debug(
                    f"GESTURE matched: directions={data.get('directions')} "
                    f"raw={data.get('raw_directions')} shape={preset.get('shape')} "
                    f"target={target} type={act_type}"
                )

                # Execute asynchronously after a brief 60ms delay so that:
                # 1. _hook_proc returns immediately and finishes WM_RBUTTONUP in Windows.
                # 2. TrailOverlay finishes canvas destruction on Tkinter thread before keystrokes are sent.
                def _do_execute() -> None:
                    executed = False
                    # For pure keyboard shortcuts, shortcut_executor has identical proven behavior with command panel
                    if act_type == "KEY_COMBO" and (target or keys):
                        try:
                            shortcut_executor.execute(target or keys)
                            executed = True
                            log_debug(f"GESTURE executed via shortcut_executor: {target or keys}")
                        except Exception as exc:
                            log_debug(f"GESTURE shortcut_executor error: {exc}")

                    if not executed and act_type:
                        try:
                            from src.features.action_dispatcher.dispatcher import ActionDispatcher
                            action_cfg = {**preset, "type": act_type, "target": target}
                            disp = ActionDispatcher()
                            disp_res = disp.execute(action_cfg)
                            if disp_res.get("ok"):
                                executed = True
                                log_debug(f"GESTURE executed via ActionDispatcher: {action_cfg}")
                        except Exception as exc:
                            log_debug(f"GESTURE ActionDispatcher error: {exc}")

                    if not executed and keys:
                        try:
                            shortcut_executor.execute(keys)
                            log_debug(f"GESTURE executed via fallback shortcut_executor: {keys}")
                        except Exception as exc:
                            log_debug(f"GESTURE fallback error: {exc}")

                threading.Timer(0.06, _do_execute).start()
                return True

            # Unmatched: Silent Drop — suppress completely (no context menu)
            log_debug(
                f"GESTURE unmatched: raw={res.get('data', {}).get('raw_directions')} "
                f"norm={res.get('data', {}).get('directions')}"
            )
            return True

        # SCROLLING: right_down was never sent to any app. Suppress right_up so
        # no context menu appears. OS hardware state (GetAsyncKeyState) is already
        # correct; apps that check GetKeyState may lag briefly but recover on next
        # mouse event — acceptable trade-off vs context menu appearing.
        return True
