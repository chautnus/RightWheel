# ADR-015: Draw Gesture UI & Command Palette Modernization Architecture

## Status
Accepted

## Context
RightWheel previously shared common UI modules with Touchpad Gesture. However:
1. RightWheel's hardware trigger is mouse-based (Right Mouse Button + Wheel scroll for palette/tab-switch, RMB + Drag for draw gestures).
2. The UI components still had Touchpad terminology (finger count selector, PTP hardware checks, "vuốt 3 ngón").
3. The floating Command Palette in Python (`panel_window.py`) was still the older 264px window not yet connected to the unified `ActionDispatcher` or `ConfigReloadWatcher`.
4. Gestures lacked directional visualizers, making it hard for users to know which direction a stroke runs.

## Decisions

### 1. Dedicated Mouse Draw Visualizer with Directional Markers
We update `TouchpadVisualizer.tsx` to render an SVG viewport (180x110) containing:
- `<defs>` with SVG arrowhead markers (`marker-end="url(#arrowhead)"`).
- A prominent start dot (`<circle cx={x0} cy={y0} r="4.5" fill="#10b981" />`) labeled "Start".
- Stroke path with directional arrows pointing in the direction of drag motion.
- Mouse interaction badge (`🖱️ Giữ chuột phải & kéo vẽ`).

### 2. Elimination of Finger Count in Gesture Schema UI
RightWheel gestures in config service are stored with `kind: "draw"`. While schema v4 supports `finger_count`, for mouse gestures it defaults to 1 internally. The UI will completely remove finger count selectors from `GestureEditorModal.tsx` and `GesturesTab.tsx`, presenting only stroke patterns.

### 3. Modernize Python Command Palette
Update `src/features/shortcut_panel/ui/panel_window.py`:
- Increase width to `_W = 320`.
- Delegate execution to `ActionDispatcher` (`KEY_COMBO`, `RUN_APP`, `OPEN_URL`, `RUN_SHELL`, `FOLDER`, `SEQUENCE`, `TYPE_TEXT`, `WEB_CLIP`).
- Wire `ConfigReloadWatcher` to listen for external profile edits from WebView2 without needing application restarts.
- Remove legacy Tkinter `show_welcome(self._root)` on startup.

### 4. Clean General Settings
Remove Touchpad OS gesture cards from `GeneralTab.tsx`. Keep RightWheel settings: Windows startup, language selector, and mouse trail overlay.

## Consequences
- Clean, consistent mental model for RightWheel users.
- Full parity between Command Palette execution capabilities and Gesture Dispatcher capabilities.
- Beautiful, intuitive visualizer with directional arrows for all 25+ gesture shapes.
