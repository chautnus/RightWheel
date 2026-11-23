# Tasks — f020-welcome-screen-copy-command-palette-and-settings-language

## Batch 1: Multilingual i18n Dictionary & Settings Language Selector (Tasks T-114..T-116)
- [ ] **T-114**: Update `src/core/i18n.py` for all 7 locales (`vi`, `en`, `fr`, `es`, `it`, `pt`, `id`) with the 3 rewritten Bento cards and new Wizard strings.
- [ ] **T-115**: Update `WelcomeView.tsx` with updated card titles, icons, and Bento tag bindings.
- [ ] **T-116**: Add persistent Language Selector in `SettingsView.tsx` sidebar with real-time state update.

## Batch 2: Command Palette Configuration in Step 1/2 Wizard & UI Build (Tasks T-117..T-119)
- [ ] **T-117**: Integrate Command Palette sub-tab / segmented control in `WizardView.tsx` Step 1/2 with `CommandEditorModal`.
- [ ] **T-118**: Compile and sync UI bundle with `build:rightwheel-v3` and `build_v3_ui.ps1`.
- [ ] **T-119**: Run `pytest` and verify standalone application build and functionality.
