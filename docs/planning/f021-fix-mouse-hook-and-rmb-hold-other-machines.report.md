# Execution Report: f021-fix-mouse-hook-and-rmb-hold-other-machines

## Overview
- **Feature**: f021 - Fix mouse hook and RMB hold on other machines, Win64 hook types, 1000Hz gaming mouse anti-timeout, and add admin diagnostics
- **Status**: Completed
- **Date**: 2026-11-23

## Implemented Changes

1. **Win64 CallNextHookEx & HookProc Signature Correction (T-120)**:
   - In `src/features/mouse_mapper/services/mouse_hook_service.py`:
     - Explicitly specified 64-bit argument types and return type `ctypes.c_ssize_t` (`LRESULT`) for `user32.CallNextHookEx`:
       `[ctypes.c_void_p, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM]` returning `ctypes.c_ssize_t`.
     - Specified return type `ctypes.c_ssize_t` for `_HookProc` callback instead of default 32-bit `ctypes.c_long`.
     - Specified explicit signatures for `SetWindowsHookExW`, `UnhookWindowsHookEx`, and `GetMessageW`.
     - Prevents silent pointer/register truncation and access violations on 64-bit Windows systems.

2. **Gaming Mouse Anti-Timeout & Rate-Limiting (T-121)**:
   - In `src/features/mouse_mapper/services/mouse_hook_service.py`:
     - Added spatial and temporal filtering on `WM_MOUSEMOVE` when RMB is held: only dispatches to Python queue if cursor moved $\ge 2$ pixels or $\ge 8$ms elapsed since the previous event (~125Hz max cap).
     - Solves Windows `LowLevelHooksTimeout` (200-300ms) silent unhook caused by event queue backlog on 500Hz/1000Hz gaming mice.
     - Added `is_hook_alive` property and `stats` counter dictionary (`rmb_down`, `rmb_up`, `scroll`, `moves`, `rehook_count`) for runtime introspection.

3. **Resolve Visual Trail Overlay Startup Race Condition (T-122)**:
   - In `src/features/mouse_mapper/ui/trail_overlay.py`:
     - Updated `TrailOverlay.__init__` to accept a callable `root_getter` in addition to a raw Tk root.
     - Dynamic resolution in `_get_root()` retrieves `_root` on demand whenever a gesture begins.
   - In `src/main.py`:
     - Passed `root_getter=lambda: getattr(panel_window, "_root", None)` to `TrailOverlay`, ensuring that delayed initialization of Tkinter root in `PanelWindow` thread does not break the gesture visual trail.

4. **Lower Movement Threshold & Add Dynamic App Settings Configuration (T-123)**:
   - In `src/features/mouse_mapper/types/mouse_mapper_types.py`:
     - Reduced default `move_threshold` from 50px to 16px.
   - In `src/features/mouse_mapper/logic/mouse_mapper_logic.py`:
     - Added dynamic loading of `move_threshold` / `swipe_threshold` from `app_settings.json` with 16px fallback.
     - Enables low-DPI (800 DPI) office mice, laptop touchpads, and subtle short gestures to immediately transition from `RIGHT_HELD` to `GESTURE` mode.

5. **Admin Run Check, Elevation Menu & 1-Click Diagnostic Clipboard Copy (T-124)**:
   - In `src/features/mouse_mapper/ui/tray_ui.py`:
     - Added `is_admin()` utility via `shell32.IsUserAnAdmin()`.
     - Added tray menu action `🛡️ Chạy với quyền Administrator` (`_run_as_admin`) using `ShellExecuteW(..., "runas", ...)` to bypass Windows UIPI restrictions over elevated target apps (Task Manager, Registry Editor, Admin Terminals).
     - Added tray menu action `📋 Sao chép chẩn đoán chuột` (`_copy_diagnostics`) exporting OS version, Admin privileges, swapped mouse button state, mapper state, threshold, hook status, and event counters directly into the clipboard.
   - In `src/main.py`:
     - Injected `hook_service` into `TrayUI` to power real-time diagnostic reporting.

6. **Unit Testing & Standalone PyInstaller Compilation (T-125)**:
   - In `tests/test_v3_feature_parity.py`:
     - Added unit tests:
       - `test_mouse_hook_win64_signatures_and_stats`
       - `test_trail_overlay_root_getter`
       - `test_move_threshold_default_and_config`
   - Verified static compilation: `python -m py_compile ...` passed with zero errors.
   - Pytest: **25/25 unit tests PASSED**.
   - Recompiled `dist/RightWheel.exe` via PyInstaller (31,258,600 bytes).

## Verification Evidence
- `tests/test_v3_feature_parity.py::test_mouse_hook_win64_signatures_and_stats PASSED`
- `tests/test_v3_feature_parity.py::test_trail_overlay_root_getter PASSED`
- `tests/test_v3_feature_parity.py::test_move_threshold_default_and_config PASSED`
- `tests/test_intent_service.py` (5 tests PASSED)
- `tests/test_render_flicker.py` (1 test PASSED)
- `tests/test_sequence_integration.py` (7 tests PASSED)
- `tests/test_v3_feature_parity.py` (12 tests PASSED)
- PyInstaller: `dist/RightWheel.exe` built successfully with code 0 (size: 31,258,600 bytes).
