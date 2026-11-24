## Elicitation — 2026-11-24

Problem: RightWheel UI contains numerous hardcoded Vietnamese strings across WebView2 React components, Python backend defaults, Tkinter fallback dialogs, and Gesture Guide Overlay, while multi-language selectors still expose unfinished/mixed translations.
Goal: Temporarily enforce English-only UI across all windows (Gesture Guide Overlay, Welcome, Wizard, Settings, Modals, Tray, Tkinter fallback) and hide other language selectors while preserving i18n dictionary files for future re-enablement.
Scope IN:
- Force runtime language to "en" in `src/core/i18n.py`, `src/features/i18n/__init__.py`, `src/core/config_service.py`, `src/features/webview_ui/bridge_api.py`.
- Hide language selector UI in `WelcomeView.tsx`, `SettingsView.tsx`, `GeneralTab.tsx`, and Tkinter `general_tab.py`.
- Translate all hardcoded Vietnamese strings/fallbacks in Python backend (`main.py`, `config_service.py`, `tray_ui.py`, `single_instance.py`, `intent_service.py`, `gestures_tab.py`, `intent_picker_dialog.py`, `reference_tab.py`) and React UI (`rightwheel-v3` components, views, `actionDescriber.ts`, `mock.ts`).
- Auto-migrate default gesture/command descriptions in existing user config to English while preserving user-created custom labels.
Scope OUT:
- Deleting `src/core/i18n.py` or `src/core/locales/*.py` or `src/features/i18n/*.py` dictionary files.
- Changing non-UI internal logic (mouse hooks, gesture recognition, action execution).
Constraints: Maintain UTF-8, rebuild `ui_dist/` and `dist/RightWheel.exe`, update/pass pytest suite.

---

## PRD — 2026-11-24

Path: docs/prd/f025-english-only-ui-cleanup.md
Version: 1.0
Summary: Enforce English-only runtime, hide non-English language selectors, and replace all hardcoded Vietnamese UI strings with English across WebView2 and Tkinter.

---

## Architecture — 2026-11-24

Pattern: Non-destructive Runtime English Lock + UI Fallback Normalization
ADR-017: Force runtime language to English & hide language selectors → docs/adr/ADR-017-english-only-runtime-and-ui-cleanup.md

---

## Tasks — 2026-11-24

Total: 6 tasks (T-0136..T-0141), 6h estimate
Batches: 2 (batch-1: Python backend & Tkinter; batch-2: React V3 UI, tests, build & release)
