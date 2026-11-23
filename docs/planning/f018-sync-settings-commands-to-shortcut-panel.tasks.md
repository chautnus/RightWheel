# Tasks: f018-sync-settings-commands-to-shortcut-panel

## Task Summary
- **Total Tasks**: 5
- **Batches**: 1 batch (`.batch-1.md`)

## Task List
- **T-104**: Delegate `src/features/shortcut_panel/services/config_service.py` `load()` and `resolve_profile()` to Schema v4 `profiles.json` with fallback compatibility for `default`, `shortcuts`, and `gestures`.
- **T-105**: Implement dual-write sync in `src/core/config_service.py:save_unified_profiles()` to keep `shortcuts.json` synchronized whenever `profiles.json` is updated.
- **T-106**: Update `PanelLogic` in `src/features/shortcut_panel/logic/panel_logic.py` to seamlessly read `commands` from Schema v4 active profiles.
- **T-107**: Add regression test in `tests/test_v3_feature_parity.py` verifying end-to-end command synchronization from `bridge_api` to `PanelLogic`.
- **T-108**: Rebuild PyInstaller binary `dist/RightWheel.exe` and verify standalone execution.
