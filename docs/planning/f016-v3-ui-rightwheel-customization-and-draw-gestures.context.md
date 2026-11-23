# Feature Context: f016-v3-ui-rightwheel-customization-and-draw-gestures

## Background & Scope
Following the porting of core kernel services and Fluent V3 UI in f015, the UI currently retains several legacy Touchpad Gesture labels, controls, and onboarding flows (such as "Touchpad Gesture", "Precision Touchpad", "3 & 4-finger swipes", "PTP Hardware Ready"). RightWheel is a mouse productivity utility centered on Right Mouse Button (RMB) + Wheel scroll and Right Mouse + Draw Gestures.

The goal of this feature is to completely customize the UI and Command Palette for RightWheel:
1. **Welcome Screen & Onboarding**: Rebuild `WelcomeView.tsx` & `WizardView.tsx` to showcase RMB + Scroll UP (Command Palette), RMB + Scroll DOWN (Alt+Tab Switcher), and RMB + Drag (Draw Gestures). Disable legacy Tkinter welcome pop-up from `panel_window.py`.
2. **Command Palette Modernization**: Upgrade `src/features/shortcut_panel/ui/panel_window.py` and item renderer to 320px width, integrate with `ActionDispatcher` for all 8 action types, and enable live config reloading. Clean up any remaining "Touchpad" placeholders in `CommandEditorModal.tsx` and `CommandsTab.tsx`.
3. **Settings Branding & Customization**: Remove all Touchpad Gesture references from `SettingsView.tsx` and `GeneralTab.tsx`. Replace Windows Touchpad OS gestures with RightWheel-specific settings (startup, trail visualizer, tab switch).
4. **Draw Gestures**: Reconfigure `GestureEditorModal.tsx` and `GesturesTab.tsx` to eliminate finger count selection and focus 100% on mouse draw gestures (single strokes, corners, zigzags, and custom shapes).
5. **Mouse Trigger Consistency**: Transition all UI descriptions from "vuốt 3 ngón" to "Giữ chuột phải và vẽ (Hold Right Mouse & Draw)".
6. **Pattern Directional Arrows**: Upgrade `TouchpadVisualizer.tsx` to `DrawGestureVisualizer.tsx` featuring clear start indicators (`● Start`) and directional SVG arrowheads (`marker-end="url(#arrowhead)"`) on stroke paths so users immediately see drawing direction.
