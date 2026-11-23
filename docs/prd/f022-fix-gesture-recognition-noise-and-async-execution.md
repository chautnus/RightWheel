# PRD: f022-fix-gesture-recognition-noise-and-async-execution

## Objective
Make all mouse draw gestures (single-segment `U`, `D`, `L`, `R` and two-segment combos like `D_R`, `D_U`, `U_R`, etc.) recognize reliably under real-world human hand movements, and execute their bound actions (including `prtsc`, shortcuts, and macros) asynchronously without being dropped or blocked by the mouse hook and overlay canvas.

## Functional Requirements
1. **Robust Gesture Stroke Normalization & Fallback**:
   - `normalize_directions`:
     - Collapse sandwiched diagonal wobbles (e.g. `['D', 'DR', 'D'] -> ['D']`, `['R', 'DR', 'R'] -> ['R']`).
     - Collapse turnaround curves between opposite directions (e.g. `['D', 'DR', 'U'] -> ['D', 'U']`).
     - Trim start diagonal jitter when followed by a cardinal direction (e.g. `['DR', 'D'] -> ['D']`).
     - Trim end release flick when preceded by a cardinal direction (e.g. `['D', 'DR'] -> ['D']`).
   - Add net displacement fallback for 1-stroke gestures using total `(dx, dy)` from `self._points` when directions contain residual noise.
2. **Asynchronous Gesture Execution with Delay**:
   - In `mouse_mapper_logic.py`, defer action execution to a background thread (`threading.Timer(0.06, _do_execute).start()`).
   - Immediate return of `_on_right_up` allows `_hook_proc` to complete and Windows to finish `WM_RBUTTONUP`.
   - Allows `TrailOverlay` to finish destruction before sending keystrokes or macros.
   - For `KEY_COMBO` actions, execute via `shortcut_executor.execute(keys)` with fallback to `ActionDispatcher`.
3. **Comprehensive Diagnostic Logging**:
   - Add `log_debug` entries in `mouse_mapper_logic.py` logging the raw directions, normalized directions, matched preset, and action execution result.
