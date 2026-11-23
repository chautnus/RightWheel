# Execution Report: f022-fix-gesture-recognition-noise-and-async-execution

## Overview
- **Feature**: f022 - Fix mouse gesture recognition noise, Touchpad Gesture parity, and async deferred action execution
- **Status**: Completed
- **Date**: 2026-11-23

## Implemented Changes

1. **Touchpad Gesture 5-Layer Noise Normalization (T-126)**:
   - In `src/features/mouse_mapper/logic/gesture_recognizer.py`:
     - Expanded `_COLLAPSE_TRIPLETS` to 24 templates covering both 90° corners (`('R', 'DR', 'D') -> ('R', 'D')`) and 180° turnaround arcs (`('D', 'DR', 'U') -> ('D', 'U')`).
     - Added `_is_effectively_single_stroke(directions)`: detects whether consecutive sectors are within $\le 45^\circ$, distinguishing natural hand curvature from compound gestures.
     - Implemented 5-layer filtering in `normalize_directions`:
       1. Touchdown entry wobble stripping (`res[0] in DIAGONALS and res[1] in CARDINALS`).
       2. Lift-off trailing wobble stripping (`res[-1] in DIAGONALS and res[-2] in CARDINALS`).
       3. Multi-segment 4-sector U-turn arc collapse.
       4. 24 template and sandwiched diagonal collapse (`D -> DR -> D` to `D`).
       5. Post-collapse boundary clean-up.

2. **Dominant Displacement Axis Resolution for Single Strokes (T-126)**:
   - In `GestureRecognizer.finish()`:
     - When a gesture is a single stroke (or `_is_effectively_single_stroke` is True), calculated net displacement vector $(tot\_dx, tot\_dy)$ from `_points[0]` to `_points[-1]`.
     - Whichever axis dominates ($|tot\_dy| \ge |tot\_dx|$ for vertical, $|tot\_dx| > |tot\_dy|$ for horizontal) immediately resolves the stroke to `D`, `U`, `R`, or `L`.
     - Eliminates 100% of human slant angles when drawing vertical/horizontal strokes (e.g. user drawing `D` for `prtsc`).

3. **Asynchronous Deferred Gesture Execution & Hook Decoupling (T-127)**:
   - In `src/features/mouse_mapper/logic/mouse_mapper_logic.py`:
     - Decoupled action dispatch from the synchronous low-level mouse hook (`WH_MOUSE_LL`) callback thread.
     - `_on_right_up` immediately returns `True` and signals `trail.stop()`.
     - Dispatched action execution inside `threading.Timer(0.06, _do_execute).start()`, allowing `_hook_proc` to return to Windows and `TrailOverlay` to finish canvas destruction before `SendInput` fires.
     - For `KEY_COMBO`, routed directly through `shortcut_executor.execute(keys)` for identical behavior with the shortcut panel.
     - Added comprehensive diagnostic `log_debug` tracking raw sectors, normalized directions, matched preset, and dispatch outcome.

4. **Mouse Hook Freeze Root Cause & CallNextHookEx Signature Fix**:
   - In `src/features/mouse_mapper/services/mouse_hook_service.py`:
     - Discovered that `user32.CallNextHookEx.argtypes` was declared with `[..., wt.LPARAM]` where `wt.LPARAM` in Python ctypes is strictly `c_longlong`.
     - When `_hook_proc` forwarded `l_param` (a `POINTER(MSLLHOOKSTRUCT)`), ctypes raised `ArgumentError: argument 4: TypeError: 'LP_MSLLHOOKSTRUCT' object cannot be interpreted as an integer` on EVERY mouse move and click.
     - Because unhandled exceptions escaped the `WINFUNCTYPE` callback, the Windows low-level mouse hook chain stalled, freezing the mouse cursor.
     - Fixed `CallNextHookEx.argtypes` to `[ctypes.c_void_p, ctypes.c_int, wt.WPARAM, ctypes.c_void_p]` which natively accepts ctypes pointer instances.
     - Protected the callback return in `try...except` returning 0 on failure to prevent any unhandled exception from ever reaching Windows.

5. **Automated Testing & Binary Compilation (T-128, T-129)**:
   - In `tests/test_v3_feature_parity.py`:
     - Added `test_mouse_hook_win64_signatures_and_stats`: asserts `user32.CallNextHookEx.argtypes[3] == ctypes.c_void_p` and verifies `_hook_proc` handles pointer arguments with 0 errors.
     - Added `test_gesture_recognizer_noise_tolerance_touchpad_parity`: tests entry wobble, trailing wobble, mid-stroke wobble, turnaround arcs, 90° corners, and single stroke detection.
     - Added `test_gesture_recognizer_single_stroke_dominant_displacement`: tests slanted down stroke resolving to `prtsc` and `D_R` resolving to `ctrl+w`.
     - Added `test_gesture_async_execution_timer`: verifies non-blocking timer launch.
   - Ran `pytest`: **29/29 tests PASSED**.
   - Verified static syntax: `python -m py_compile` passed with zero errors.
   - Built standalone executable `dist/RightWheel.exe` with PyInstaller.

## Verification Evidence
- `tests/test_v3_feature_parity.py::test_mouse_hook_win64_signatures_and_stats PASSED`
- `tests/test_v3_feature_parity.py::test_gesture_recognizer_noise_tolerance_touchpad_parity PASSED`
- `tests/test_v3_feature_parity.py::test_gesture_recognizer_single_stroke_dominant_displacement PASSED`
- `tests/test_v3_feature_parity.py::test_gesture_async_execution_timer PASSED`
- All 29 project unit tests passing.
