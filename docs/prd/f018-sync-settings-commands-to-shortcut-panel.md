# PRD: f018-sync-settings-commands-to-shortcut-panel

## 1. Executive Summary
Ensure that any command modifications made by users in the Settings UI (WebView2 Commands Tab) immediately reflect on the external Shortcut Panel (Command Palette) when summoned on the desktop.

## 2. User Stories
- **US-055**: As a user, when I add, edit, reorder, or delete commands in the Settings window, those changes must immediately appear in the Shortcut Panel when I hold Right Mouse and scroll UP.
- **US-056**: As a user, if I customize application-specific profile commands in Settings, the Shortcut Panel must display those customized commands when that application is active.

## 3. Acceptance Criteria
1. Changing commands in Settings immediately writes to `%APPDATA%\RightWheel\profiles.json` and updates `%APPDATA%\RightWheel\shortcuts.json`.
2. `src/features/shortcut_panel/services/config_service.py:load()` reads from `profiles.json` (Schema v4) and provides backwards-compatible access (`default`, `shortcuts`, `gestures`).
3. `PanelLogic.show()` and `PanelLogic.reload()` parse commands correctly from the active profile's `commands` array.
4. Automated pytest regression tests confirm that modifying commands via `bridge_api` is immediately reflected when querying `PanelLogic` or `config_service`.
5. Standalone executable `dist/RightWheel.exe` is recompiled and validated.
