# Context: f022-fix-gesture-recognition-noise-and-async-execution

## User Report
User reported:
"không đúng. Tất cả các gesture draw đều không được. Ví dụ tao đã thử nút prt scr: nếu gọi từ command thì ok, nhưng nếu gọi từ gesture thì không được."
(Translation: "Not right. All gesture draws do not work at all. For example I tried the prt scr button: if called from command then ok, but if called from gesture then not working.")

## Root Causes Identified Through Debug Investigation

1. **Failure to Match Due to Human Analog Wobble / Diagonal Sectors**:
   - `GestureRecognizer` quantizes micro-movements every 18 pixels into 8 sectors: `['R', 'DR', 'D', 'DL', 'L', 'UL', 'U', 'UR']`.
   - The 16 user presets only consist of cardinal directions (`U`, `D`, `L`, `R`). There are zero diagonal presets.
   - Any physical mouse stroke by a human hand on a mousepad inevitably produces micro-lateral wobbles at start, turnaround, or button release (e.g., `['DR', 'D']`, `['D', 'DR']`, `['D', 'DR', 'D']`, `['D', 'DR', 'R']`).
   - `normalize_directions` only collapsed 8 hardcoded triplets (`('R', 'DR', 'D') -> ('R', 'D')`), completely failing to collapse start noise, end release flick, turnaround curves between opposite directions (`D` to `U`), and intermediate wobble (`['D', 'DR', 'D']`).
   - As a result, `normalize_directions(preset_dirs) == current_dirs` evaluated to `False` on almost 100% of real user mouse strokes, silently dropping the gesture without executing any action.

2. **Synchronous Hook Execution Blocking Windows Message Handling & Overlay Conflict**:
   - When a gesture finished in `_on_right_up`, `ActionDispatcher.execute(action_cfg)` was called synchronously inside the Windows low-level mouse hook (`WH_MOUSE_LL`) callback thread.
   - At this exact moment, `_hook_proc` had not returned to Windows, so Windows was still processing the mouse up event.
   - Furthermore, `trail.stop()` had just scheduled overlay window destruction on Tkinter's thread (`root.after(0, ...)`), meaning `TrailOverlay`'s full-screen transparent canvas was still active and covering the entire screen.
   - In contrast, the shortcut panel command executor uses `threading.Timer(0.25, ...)` in a background thread, giving Windows time to restore foreground focus before sending keystrokes.
   - Calling `SendInput` synchronously in the hook proc while the overlay window is alive caused keystrokes (such as `VK_SNAPSHOT` / `prtsc`) to be swallowed or dropped.
