# Execution Report: f020-gesture-order-and-tkinter-popup-redesign

## Overview
- **Feature**: f020 - Fix reference key binding, gesture execution matching, sort 16 2-segment gestures, and redesign rounded Tkinter popup with blue highlight
- **Status**: Completed
- **Date**: 2026-11-23

## Implemented Changes

1. **Fix Reference / Intent Key Save Synchronization (T-114)**:
   - In `src/features/shortcut_panel/services/config_service.py:save()` and `src/core/config_service.py:save_unified_profiles()`:
     - Implemented two-way synchronization before saving Schema v4: whenever `data["default"]` or `data["shortcuts"]` or `data["gestures"]` is mutated by legacy or UI consumers (such as `reference_tab.py` or `default_tab_crud.py`), those items are copied directly into `data["profiles"][0]["commands"]` and `data["profiles"][0]["gestures"]`.
     - Completely prevents `save_unified_profiles` from wiping out newly attached commands and gestures when saving to `shortcuts.json` and `profiles.json`.

2. **Add 1-Click [+ Thêm vào Lệnh] in WebView2 ReferenceTab (T-115)**:
   - In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\ReferenceTab.tsx`:
     - Added 1-click `[+ Thêm vào Lệnh]` action button on each non-mouse row with visual feedback (`✓ Đã thêm`).
   - In `C:\dev\ui-studio\src\projects\rightwheel-v3\views\SettingsView.tsx`:
     - Added `handleAddCommandFromReference` calling `bridgeClient.saveProfileCommands(activeProfile.id, nextCommands)` and updating local state.

3. **Fix Gesture Recognition Matching & ActionDispatcher Execution**:
   - In `src/features/mouse_mapper/logic/gesture_recognizer.py`:
     - Updated `finish()` to resolve gesture directions from either `preset.get("directions")` OR `preset.get("shape")` (handling `"D_R"`, `"U_R"`, etc.).
     - Resolved keys from `preset.get("keys")` or `preset.get("target")`.
     - Returned the full matched `preset` in `res["data"]["preset"]`.
   - In `src/features/mouse_mapper/logic/mouse_mapper_logic.py`:
     - Resolved active profile gestures using `profile_service.resolve_active_profile_full(hwnd)` with fallback to global gestures.
     - Routed matched gestures through `ActionDispatcher.execute(action_cfg)` with fallback to `shortcut_executor.execute(keys)` for basic key combinations.
   - In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GestureEditorModal.tsx`:
     - Populated both `directions` and `keys` when saving entries to guarantee two-way compatibility across legacy and Schema v4 consumers.

4. **16 Gestures Grouped by First Stroke & 2-Segment Limit (T-116, T-117)**:
   - In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GestureEditorModal.tsx`:
     - Replaced `PRESETS` with the strict 16 gestures grouped by first stroke (`U`, `D`, `L`, `R` with sub-order: đơn, ngược chiều, rẽ phải, rẽ trái).
     - Removed all geometric shapes (circle, square, triangle, Z, N) and 3-stroke paths.
   - In `src/core/config_service.py`:
     - Updated `GESTURE_DESCRIPTIONS` with action labels for all 16 gestures.
     - Updated `sort_gestures()` with `_DRAW_GESTURE_ORDER` mapping so wheel gestures appear first followed by draw gestures in exact first-stroke hierarchy.

5. **Redesign Tkinter Popup with Rounded Corners & Vivid Blue Selection (T-118)**:
   - In `src/features/shortcut_panel/ui/panel_window.py`:
     - Added `_apply_rounded_corners()` calling Win32 `CreateRoundRectRgn(0, 0, w + 1, h + 1, 14, 14)` and `SetWindowRgn` on the window and parent HWND.
     - Called after positioning and rendering to apply rounded corners.
   - In `src/features/shortcut_panel/ui/panel_item_renderer.py`:
     - Configured selected row highlight: `_BG_SEL = "#0078d4"`, `_ACCENT_BAR = "#38bdf8"`, `_FG_SEL = "#ffffff"`, `_FG_SUB_SEL = "#e0f2fe"`.
     - Applied row padding `padx=6, pady=2` for spacing.

6. **Automated Testing, UI Rebuild & Standalone Binary Compilation (T-119)**:
   - Added unit test cases `test_reference_save_and_config_sync` and `test_gesture_recognizer_shape_and_sort` in `tests/test_v3_feature_parity.py`.
   - Rebuilt UI via `scripts/build_v3_ui.ps1`: bundled and synced to `src/ui_dist`.
   - Ran `pytest`: 22/22 unit tests passing in 1.82s.
   - Recompiled `dist/RightWheel.exe` via PyInstaller (31,258,600 bytes).

## Verification Evidence
- `tests/test_v3_feature_parity.py::test_reference_save_and_config_sync PASSED`
- `tests/test_v3_feature_parity.py::test_gesture_recognizer_shape_and_sort PASSED`
- `tests/test_v3_feature_parity.py::test_command_sync_settings_to_panel PASSED`
- `tests/test_sequence_integration.py::test_chatgpt_macro_execution_flow PASSED`
- Vite build: `dist-rightwheel-v3/index.html` + assets built and synced successfully.
- PyInstaller: `dist/RightWheel.exe` recompiled successfully (code 0).
