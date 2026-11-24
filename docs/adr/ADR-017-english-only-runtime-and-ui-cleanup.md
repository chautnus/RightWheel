# ADR-017: Non-Destructive English-Only Runtime Lock & UI Cleanup

- **Status:** Accepted
- **Date:** 2026-11-24
- **Feature:** F-025 (`f025-english-only-ui-cleanup`)

## Context
RightWheel currently maintains multi-language dictionaries (`vi`, `en`, `fr`, `es`, `it`, `pt`, `id`, `th`, `zh`) in `src/core/i18n.py`, `src/core/locales/`, and `src/features/i18n/`. However, many React components (`ui-studio/rightwheel-v3`), Tkinter fallback dialogs, `src/main.py` (Gesture Guide Overlay), and `config_service.py` defaults still contain hardcoded Vietnamese strings and fallback values. The user wants to temporarily present an English-only UI and hide all other languages until multi-language support is ready for polish.

## Decision
1. **Non-Destructive Runtime Lock:** Keep all existing translation dictionary files (`src/core/i18n.py`, `src/core/locales/*.py`, `src/features/i18n/*.py`) intact on disk, but restrict `SUPPORTED_LANGUAGES` / `available()` to `[("en", "English")]` and force `load_language_preference()`, `set_language()`, `set_locale()`, and `load_app_settings()` to resolve `"en"`.
2. **UI Language Selector Removal:** Hide/remove the language `<select>` / `Combobox` UI blocks in `WelcomeView.tsx`, `SettingsView.tsx`, `GeneralTab.tsx`, and Tkinter `general_tab.py` so users only see English.
3. **English-Only Fallbacks & Presets:** Replace all Vietnamese fallback strings in React `tr(key, "...")`, `actionDescriber.ts`, `GestureEditorModal.tsx` presets, `TouchpadVisualizer.tsx`, `mock.ts`, `main.py` (`GestureGuideOverlay` lookup using `title_en` and `"Unassigned"`), `tray_ui.py`, `single_instance.py`, and Tkinter UI files.
4. **Safe Default Description Migration:** In `config_service.py`, translate `GESTURE_DESCRIPTIONS`, `DEFAULT_MOUSE_GESTURES`, and `DEFAULT_COMMANDS` to English, and normalize known legacy Vietnamese default descriptions when loading `profiles.json` without altering user-created custom descriptions.

## Consequences
- **Positive:** Immediate 100% consistent English UX across every window; zero risk of breaking i18n keys; easy to re-enable multi-language later by restoring `SUPPORTED_LANGUAGES` and un-hiding the dropdowns.
- **Negative:** Existing unit tests asserting `save_general_settings({"language": "vi"})` or testing multi-language `SUPPORTED_LANGUAGES` switching must be updated to reflect the temporary English-only lock.
