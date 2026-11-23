# Tasks Breakdown — f016-v3-ui-rightwheel-customization-and-draw-gestures

## Batch 1: React UI Customization for RightWheel & Draw Gestures
- [ ] **T-89**: Update `WelcomeView.tsx` & `WizardView.tsx` to 100% RightWheel mouse interactions (RMB + Scroll UP/DOWN, RMB + Draw).
- [ ] **T-90**: Update `SettingsView.tsx`, `GeneralTab.tsx`, and `ProfileWorkspace.tsx` to remove Touchpad PTP labels and Windows OS gesture controls.
- [ ] **T-91**: Reconfigure `GestureEditorModal.tsx` and `GesturesTab.tsx` to remove finger counts and focus on Draw Gestures.

## Batch 2: Directional Pattern Visualizer & Command Palette Sync
- [ ] **T-92**: Upgrade `TouchpadVisualizer.tsx` with start indicator point (`● Start`), mouse drag badge, and SVG directional arrowheads (`marker-end`).
- [ ] **T-93**: Update `CommandsTab.tsx` and `CommandEditorModal.tsx` labels and placeholders to reference RightWheel.
- [ ] **T-94**: Rebuild UI Studio production bundle and sync into `src/ui_dist/` via `scripts/build_v3_ui.ps1`.

## Batch 3: Python Command Palette Modernization & Build
- [ ] **T-95**: Modernize `src/features/shortcut_panel/ui/panel_window.py` (320px width, `ActionDispatcher` execution, `ConfigReloadWatcher`, remove Tkinter welcome pop-up).
- [ ] **T-96**: Run pytest suite, re-compile standalone `dist/RightWheel.exe` via PyInstaller, verify build and push to Git.
