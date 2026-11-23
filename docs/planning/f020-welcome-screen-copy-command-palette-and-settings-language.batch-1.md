# BATCH 1/2: i18n Dictionary, Welcome Bento Cards & Settings Language

## Task T-114: Multilingual i18n Updates in `src/core/i18n.py`
- **File**: `src/core/i18n.py`
- **Goal**:
  - Update `welcome_bento_1_title`, `welcome_bento_1_tag`, `welcome_bento_1_desc`: "Hold Right mouse, Draw gestures, Get task done"
  - Update `welcome_bento_2_title`, `welcome_bento_2_tag`, `welcome_bento_2_desc`: "Unlimited quick command, adapt by application"
  - Update `welcome_bento_3_title`, `welcome_bento_3_tag`, `welcome_bento_3_desc`: "A series of action in one click"
  - Mirror to `bento_1-3` fallback keys.
  - Add wizard strings: `wiz_tab_gestures`, `wiz_tab_commands`, `wiz_add_command`, `wiz_commands_desc`, `wiz_commands_empty`.
- **Verify**: `pytest` passes with 0 syntax or encoding issues.

## Task T-115: Update `WelcomeView.tsx`
- **File**: `C:\dev\ui-studio\src\projects\rightwheel-v3\views\WelcomeView.tsx`
- **Goal**:
  - Render Card 1 (Draw Gestures), Card 2 (Quick Commands & Adaptive App Profiles), Card 3 (One-Click Multi-Action Macros).
  - Use appropriate modern icons (`✏️` / `🖱️`, `⚡`, `🚀`).
- **Verify**: Types check cleanly.

## Task T-116: Add Persistent Language Selector to `SettingsView.tsx`
- **File**: `C:\dev\ui-studio\src\projects\rightwheel-v3\views\SettingsView.tsx`
- **Goal**:
  - Add `<Globe />` and language `<select>` in sidebar.
  - Implement `handleLanguageChange(lang)` to call `bridgeClient.saveGeneralSettings({ language: lang })` and propagate changes to state and translations.
- **Verify**: Language selector renders in Settings and updates active translations.
