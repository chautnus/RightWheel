# Batch 1: f018-sync-settings-commands-to-shortcut-panel

## Tasks
- T-104: Bridge `src/features/shortcut_panel/services/config_service.py` to `profiles.json` (Schema v4).
- T-105: Sync `shortcuts.json` in `src/core/config_service.py:save_unified_profiles()`.
- T-106: Update `PanelLogic` in `src/features/shortcut_panel/logic/panel_logic.py`.
- T-107: Add regression test in `tests/test_v3_feature_parity.py`.
- T-108: Recompile PyInstaller standalone executable `dist/RightWheel.exe`.
