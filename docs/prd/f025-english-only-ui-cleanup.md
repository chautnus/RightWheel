# PRD — f025-english-only-ui-cleanup

## 1. Objective
Temporarily switch the entire RightWheel user interface to English-only, hide all other language options/selectors from the UI, and eliminate every hardcoded Vietnamese string across all windows (Gesture Guide Overlay, Welcome, Onboarding Wizard, Settings, Modals, Tray Menu, and Tkinter Fallback) while preserving the underlying i18n dictionary files for future re-activation.

---

## 2. User Stories
- **US-068**: As a user opening RightWheel, I want all screens (Welcome, Onboarding Wizard, Settings, Modals, System Tray, and Gesture Guide Overlay) to display clean, consistent English text without any stray Vietnamese words or fallback strings.
- **US-069**: As a user navigating Welcome, Settings, or General Preferences, I want the language selector hidden (or locked to English) so I am not confused by unfinished multi-language UI states.
- **US-070**: As an existing user upgrading from a previous version where `app_settings.json` had `"language": "vi"` and default Vietnamese gesture descriptions, I want my app to automatically switch to English and update default system descriptions to English without losing any custom gestures or commands I created.

---

## 3. Acceptance Criteria
1. **Runtime Language Lock (`en`)**:
   - `src/core/i18n.py` (`load_language_preference`, `set_language`, `_CURRENT_LANG`) and `src/features/i18n/__init__.py` (`init`, `set_locale`, `_code`) always resolve to `"en"`.
   - `SUPPORTED_LANGUAGES` in `src/core/i18n.py` and `available()` in `src/features/i18n/__init__.py` expose only `("en", "English")`, while `_TRANSLATIONS` and `locales/*.py` remain intact on disk.
   - `src/core/config_service.py` `load_app_settings()` defaults `"language": "en"` and overrides `"language"` to `"en"` at runtime.
2. **Legacy Config Migration (Default Labels Only)**:
   - When loading unified `profiles.json`, known default Vietnamese `GESTURE_DESCRIPTIONS` / `DEFAULT_MOUSE_GESTURES` / `DEFAULT_COMMANDS` descriptions are normalized to English equivalents, while user-authored custom labels/descriptions remain untouched.
3. **Zero Hardcoded Vietnamese in Guide, Overlay, Tray & Tkinter**:
   - `src/main.py`: `_guide_keys_to_text()` uses `it.title_en`; `"Chưa gán"` fallback becomes `"Unassigned"`.
   - `src/features/mouse_mapper/ui/tray_ui.py` & `src/core/single_instance.py`: English fallback strings.
   - `src/features/shortcut_panel/ui/gestures_tab.py`, `intent_picker_dialog.py`, `reference_tab.py`, `general_tab.py`: 100% English UI labels and hidden language selector card.
4. **Zero Hardcoded Vietnamese in WebView2 V3 UI (`ui-studio/rightwheel-v3`)**:
   - Hide language selector in `WelcomeView.tsx`, `SettingsView.tsx`, and `GeneralTab.tsx`.
   - Replace all Vietnamese fallback strings in `tr(key, "...")`, presets in `GestureEditorModal.tsx`, labels in `TouchpadVisualizer.tsx`, descriptions in `actionDescriber.ts`, and `mock.ts` with English.
5. **Build & Verification**:
   - `scripts/build_v3_ui.ps1` compiles and syncs `src/ui_dist/` cleanly.
   - `pytest tests/ -q` passes 100% (including updated/new assertions for English-only lock).
   - `pyinstaller RightWheel.spec --noconfirm` builds `dist/RightWheel.exe` cleanly.
