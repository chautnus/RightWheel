# Batch 1 — f025-english-only-ui-cleanup (Python Backend, Guide Overlay & Tkinter Fallback)

- **Tasks:** T-0136, T-0137, T-0138
- **Target Files:**
  - `src/core/i18n.py`
  - `src/features/i18n/__init__.py`
  - `src/features/webview_ui/bridge_api.py`
  - `src/core/config_service.py`
  - `src/main.py`
  - `src/features/mouse_mapper/ui/tray_ui.py`
  - `src/core/single_instance.py`
  - `src/features/shortcut_panel/services/intent_service.py`
  - `src/features/shortcut_panel/ui/general_tab.py`
  - `src/features/shortcut_panel/ui/gestures_tab.py`
  - `src/features/shortcut_panel/ui/intent_picker_dialog.py`
  - `src/features/shortcut_panel/ui/reference_tab.py`

## Instructions
1. **T-0136 (i18n Runtime Lock):**
   - `src/core/i18n.py`: Keep `_TRANSLATIONS` intact, set `SUPPORTED_LANGUAGES = [("en", "English")]`, `_CURRENT_LANG = "en"`, make `load_language_preference()` and `set_language()` force `"en"`.
   - `src/features/i18n/__init__.py`: Keep `_SUPPORTED` intact for dict loading, restrict `available()` to `[("en", "English")]`, force `set_locale()` and `init()` to `"en"`.
   - `src/features/webview_ui/bridge_api.py`: Default `"language"` to `"en"` in `_load_app_settings()`, `get_initial_state()`, `save_general_settings()`, and `search_intents()` fallback.
2. **T-0137 (Config Defaults & Safe Migration):**
   - `src/core/config_service.py`: Replace Vietnamese strings in `GESTURE_DESCRIPTIONS`, `DEFAULT_MOUSE_GESTURES`, and `DEFAULT_COMMANDS` with English equivalents. Set `load_app_settings()` default `"language": "en"` and force `defaults["language"] = "en"`. In `load_unified_profiles()`, normalize any legacy Vietnamese default descriptions matching the known old map to English, without touching user-created custom descriptions.
3. **T-0138 (Guide Overlay, Tray, Single Instance & Tkinter UI):**
   - `src/main.py`: `_guide_keys_to_text()` returns `it.title_en`; `"Chưa gán"` fallback becomes `"Unassigned"`.
   - `src/features/mouse_mapper/ui/tray_ui.py`: Change fallback `"Chạy với quyền Administrator"` -> `"Run as Administrator"`, `"Sao chép chẩn đoán chuột"` -> `"Copy Mouse Diagnostics"`.
   - `src/core/single_instance.py`: Change fallback `"RightWheel đã đang chạy..."` and `"RightWheel — Đang chạy"` to English.
   - `src/features/shortcut_panel/services/intent_service.py`: Change default `lang: str = "en"` in `get_title`.
   - `src/features/shortcut_panel/ui/general_tab.py`: Hide/remove the Language selector card (`c_lang`), keeping only System Startup.
   - `src/features/shortcut_panel/ui/gestures_tab.py`, `intent_picker_dialog.py`, `reference_tab.py`: Translate all Vietnamese labels, hints, buttons, status texts, and dialog titles to English.

## Done Definition & Verify
- Static syntax check (`python -m py_compile`) passes on all modified Python files.
- Zero Vietnamese characters remain in non-dictionary UI code (`src/main.py`, `tray_ui.py`, `single_instance.py`, `config_service.py`, `shortcut_panel/ui/*.py`).
