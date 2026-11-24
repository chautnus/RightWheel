# Execution Report: f025-english-only-ui-cleanup

## Overview
- **Feature:** F-025 — English-Only Runtime & Hardcoded Vietnamese UI Cleanup
- **Status:** Completed
- **Date:** 2026-11-24

## Completed Tasks
- **T-0136**: Locked `src/core/i18n.py`, `src/features/i18n/__init__.py`, and `src/features/webview_ui/bridge_api.py` runtime language to `"en"` and restricted `SUPPORTED_LANGUAGES` / `available()` to English only while keeping all translation dictionary files intact on disk.
- **T-0137**: Translated `GESTURE_DESCRIPTIONS`, `DEFAULT_MOUSE_GESTURES`, and `DEFAULT_COMMANDS` in `src/core/config_service.py` to English; enforced `"language": "en"` in `load_app_settings()`; added `_LEGACY_VI_DESCRIPTIONS` migration in `load_unified_profiles()` to normalize legacy default Vietnamese descriptions without altering custom user labels.
- **T-0138**: Switched `GestureGuideOverlay` lookup in `src/main.py` to `it.title_en` and `"Unassigned"`; translated fallbacks in `tray_ui.py` and `single_instance.py`; hid the language selector card in `general_tab.py`; translated all Vietnamese UI labels in `gestures_tab.py`, `intent_picker_dialog.py`, `reference_tab.py`, and `intent_service.py`.
- **T-0139 & T-0140**: Hid language selectors in `WelcomeView.tsx`, `SettingsView.tsx`, and `GeneralTab.tsx`; replaced all hardcoded Vietnamese fallbacks, presets, and descriptions across 17 files in `C:\dev\ui-studio\src\projects\rightwheel-v3` with English.
- **T-0141**: Updated assertions in `tests/test_v3_feature_parity.py` and `tests/test_intent_service.py`, added `test_legacy_vi_config_migrates_default_descriptions_to_en`, rebuilt Vite UI (`scripts/build_v3_ui.ps1`), verified `35 passed` in `pytest`, and compiled `dist/RightWheel.exe`.

## Verification Evidence
- `scripts/build_v3_ui.ps1`: `tsc --noEmit && vite build --mode rightwheel-v3` exited 0 (built in 1.15s).
- `python -m pytest tests/ -q`: `35 passed, 1 warning in 1.66s`.
- `pyinstaller RightWheel.spec --noconfirm`: exited 0, produced `dist/RightWheel.exe`.
