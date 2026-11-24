# Batch 2 — f025-english-only-ui-cleanup (React V3 UI, Tests, Build & Binary)

- **Tasks:** T-0139, T-0140, T-0141
- **Target Files:**
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\views\WelcomeView.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\views\WizardView.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\views\SettingsView.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GeneralTab.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\bridge\mock.ts`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\lib\actionDescriber.ts`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GestureEditorModal.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\CommandEditorModal.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\CommandsTab.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\FolderEditorModal.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GesturesTab.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\KeyRecorderModal.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\MacroBuilderSection.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\ProfileRulesModal.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\ProfileWorkspace.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\ReferenceTab.tsx`
  - `C:\dev\ui-studio\src\projects\rightwheel-v3\components\TouchpadVisualizer.tsx`
  - `tests/test_v3_feature_parity.py`

## Instructions
1. **T-0139 (Hide Language Selectors & Translate Views):**
   - `WelcomeView.tsx`: Remove language `<select>` from top header; replace `"Cài đặt"` / `"Bắt đầu thiết lập"` fallbacks with `"Settings"` / `"Start Setup"`.
   - `SettingsView.tsx`: Remove language `<select>` from sidebar; replace all Vietnamese fallbacks (`"Toàn cục"`, `"RMB + Wheel Active"`, tab titles, `"Save & Close"`).
   - `GeneralTab.tsx`: Hide/remove the Language selector row; replace all Vietnamese fallbacks and toast messages with English.
   - `WizardView.tsx`: Replace all 23 Vietnamese fallback strings with English.
   - `mock.ts`: Switch mock translations, language options, profile name, and gesture descriptions to English.
2. **T-0140 (Modals & Helpers Cleanup):**
   - `actionDescriber.ts`: Force `isVi = false` (or use pure English descriptions) and replace any `"Touchpad Gesture Settings"` with `"RightWheel Settings"`.
   - `GestureEditorModal.tsx`: Translate `PRESETS` labels (`"▲ Up (U)"`, `"↳ Down → Right (D_R)"`, etc.) and all Vietnamese fallbacks to English.
   - `TouchpadVisualizer.tsx`: Force English labels (`UP`, `DOWN`, `LEFT`, `RIGHT`, `Start Point`, `Continuous Draw Gesture`, `Mouse Gesture`).
   - `CommandEditorModal.tsx`, `CommandsTab.tsx`, `FolderEditorModal.tsx`, `GesturesTab.tsx`, `KeyRecorderModal.tsx`, `MacroBuilderSection.tsx`, `ProfileRulesModal.tsx`, `ProfileWorkspace.tsx`, `ReferenceTab.tsx`: Replace all `tr(key, "...")` Vietnamese fallback strings and placeholders with English.
3. **T-0141 (Tests, Vite Build, PyInstaller & Push):**
   - Update `tests/test_v3_feature_parity.py` so language lock tests verify `"en"` enforcement and add test for legacy Vietnamese default description migration.
   - Run `powershell -ExecutionPolicy Bypass -File scripts/build_v3_ui.ps1` to rebuild `src/ui_dist/`.
   - Run `python -m pytest tests/ -q` and ensure 100% pass.
   - Kill running `RightWheel.exe`, run `pyinstaller RightWheel.spec --noconfirm`.
   - Commit and push changes to `origin/main`.

## Done Definition & Verify
- Zero Vietnamese characters remain anywhere in `C:\dev\ui-studio\src\projects\rightwheel-v3`.
- `build_v3_ui.ps1` exits 0 (`tsc --noEmit` + `vite build`).
- `pytest tests/ -q` passes 100%.
- `dist/RightWheel.exe` compiled and pushed to `origin/main`.
