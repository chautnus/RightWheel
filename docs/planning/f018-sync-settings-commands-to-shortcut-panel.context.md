# Context: f018-sync-settings-commands-to-shortcut-panel

## 1. Problem Description
- User modified commands in the Settings table (WebView2 Settings -> Tab Lệnh / CommandsTab).
- However, when triggering the Shortcut Panel on the desktop (outside, via RMB + Scroll UP), the changes did not show up.
- Root Cause:
  1. WebView2 Settings writes changes to `%APPDATA%\RightWheel\profiles.json` (Schema v4).
  2. `PanelLogic` in `src/features/shortcut_panel/logic/panel_logic.py` loads items via `src/features/shortcut_panel/services/config_service.py:load()`.
  3. `src/features/shortcut_panel/services/config_service.py` only reads `%APPDATA%\RightWheel\shortcuts.json` (Schema v3) and has no awareness of `profiles.json`.
  4. In addition, Schema v4 stores commands under `profile["commands"]`, whereas Schema v3 uses `doc["default"]` or `profile["shortcuts"]`.

## 2. Solution Architecture
- Unify configuration source of truth in `src/features/shortcut_panel/services/config_service.py` by delegating `load()` to `src.core.config_service.load_unified_profiles()`.
- Normalize Schema v4 profiles to satisfy legacy consumers (`default`, `shortcuts`, `gestures` keys) while retaining full Schema v4 structure.
- Add dual-write synchronization in `src.core.config_service.save_unified_profiles()`: whenever `profiles.json` is saved from Settings, mirror the active commands and gestures to `shortcuts.json` as a backward-compatibility safeguard.
- Ensure `PanelLogic` in `src/features/shortcut_panel/logic/panel_logic.py` resolves active commands from both `p.get("commands")` and `p.get("shortcuts")`.
