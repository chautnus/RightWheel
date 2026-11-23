# Product Requirements Document (PRD)
## Feature: f016-v3-ui-rightwheel-customization-and-draw-gestures
**Title**: RightWheel V3 UI Customization, Draw Gestures & Command Palette Modernization  
**Status**: Approved  
**Author**: Antigravity Planning Engine  

---

### 1. Goals & Problem Statement
The V3 WebView2 interface was ported from the Touchpad Gesture repository. While the underlying architecture and build work, the user-facing text, visual cues, and controls still reflect Touchpad hardware ("vuốt 3 ngón", "PTP Hardware Ready", "Touchpad Settings").

RightWheel must reflect its mouse identity:
1. **Welcome Screen & Wizard**: Explain RightWheel's 3 core interactions:
   - RMB + Wheel UP: Quick Command Palette
   - RMB + Wheel DOWN: Task & Tab Switcher
   - RMB + Draw: Neon Mouse Gestures
2. **Command Palette**: Fully aligned with the modern HUD from Touchpad Gesture (width 320px, ActionDispatcher integration, auto-reload).
3. **Settings**: Pure RightWheel branding without Windows PTP Touchpad buttons.
4. **Draw Gestures**: Replace 3/4 finger selectors with clean stroke shape presets.
5. **Pattern Visualization**: Visualizer showing stroke start point and directional arrowheads so the user knows exact drawing paths.

---

### 2. User Stories & Acceptance Criteria

#### US-50: Welcome & Setup Wizard Customized for Mouse
- **As a** RightWheel user,
- **I want** the Welcome screen and Setup Wizard to clearly instruct me on holding Right Mouse Button and scrolling or drawing,
- **So that** I understand how to use RightWheel without confusion about touchpad gestures.
- **Acceptance Criteria**:
  - `WelcomeView.tsx` and `WizardView.tsx` describe mouse operations (RMB + Scroll UP/DOWN, RMB + Draw).
  - No PTP hardware check or 3-finger swipe text in Wizard.
  - Legacy Tkinter welcome popup in `panel_window.py` is removed so only modern WebView2 Welcome appears on launch.

#### US-51: Command Palette Modernization & Dispatcher Integration
- **As a** RightWheel user,
- **I want** the Command Palette (RMB + Scroll UP) to trigger all 8 action types via `ActionDispatcher` with modern 320px HUD styling,
- **So that** macros, shell scripts, web clips, and apps execute reliably.
- **Acceptance Criteria**:
  - `panel_window.py` uses `_W = 320` and delegates action execution to `ActionDispatcher`.
  - Live configuration changes from WebView2 Settings reload without app restart via `ConfigReloadWatcher`.
  - In React `CommandEditorModal.tsx` and `CommandsTab.tsx`, placeholders and options reference "RightWheel Settings" instead of "Touchpad Settings".

#### US-52: Settings UI Branding & General Tab Cleanup
- **As a** RightWheel user,
- **I want** the Settings interface to show "RightWheel" with mouse status badges,
- **So that** the experience is consistent and professional.
- **Acceptance Criteria**:
  - `SettingsView.tsx` displays "RightWheel v3" and "RMB + Wheel Active" badge.
  - `GeneralTab.tsx` removes the Windows Touchpad OS gestures card and focuses on Startup, Language, and Mouse Gesture Trail settings.
  - `ProfileWorkspace.tsx` tab label is "Cử chỉ vẽ chuột (Draw Gestures)".

#### US-53: Draw Gesture Presets & Editor Without Finger Count
- **As a** RightWheel user,
- **I want** the Gesture Editor to let me choose drawing shapes without asking for finger count,
- **So that** setting up mouse gestures is natural.
- **Acceptance Criteria**:
  - In `GestureEditorModal.tsx`, the finger count button group is removed.
  - Preset shapes are categorized into: Nét đơn (UP, DOWN, LEFT, RIGHT), Góc vuông (D_R, D_L, U_R, U_L, R_U, R_D, L_U, L_D), Zigzag (U_R_D, D_R_U, L_D_R, R_D_L), và Hình vẽ (CIRCLE, SQUARE, TRIANGLE, Z_SHAPE, N_SHAPE).
  - In `GesturesTab.tsx`, gestures are titled `Vẽ: [Tên hình]`.

#### US-54: Pattern Visualizer with Directional Arrows & Start Point
- **As a** RightWheel user,
- **I want** the pattern simulation box to display directional arrows and a start dot,
- **So that** I know exactly where to start and which way to draw each stroke.
- **Acceptance Criteria**:
  - `TouchpadVisualizer.tsx` is updated to a Mouse Draw Visualizer:
    - Displays a glowing `● Start` indicator at the starting coordinate.
    - SVG paths include `marker-end="url(#arrowhead)"` and directional arrow markers.
    - Finger dots in the corner are replaced with a Mouse Right-Click & Drag icon badge.
