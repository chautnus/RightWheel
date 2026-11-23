# Tasks Breakdown — f017-welcome-screen-draw-gestures-and-action-descriptions

## Batch 1: Multilingual i18n Dictionary & Core Schema
- [ ] **T-97**: Update `src/core/i18n.py` to remove all 3/4-finger and touchpad references across all 7 languages (`vi`, `en`, `fr`, `es`, `it`, `pt`, `id`), replacing them with "Giữ chuột phải & Vẽ (Right Mouse & Draw)" and mouse wheel interactions.
- [ ] **T-98**: Enhance `src/core/config_service.py` (`DEFAULT_MOUSE_GESTURES`) and `src/features/webview_ui/bridge_api.py` to include rich functional action descriptions (`description` / `label`).

## Batch 2: React UI Updates & Gesture Descriptions
- [ ] **T-99**: Update `WelcomeView.tsx` bento cards and feature pills to strictly use localized mouse action texts.
- [ ] **T-100**: Update `WizardView.tsx` and `GesturesTab.tsx` to display command function descriptions alongside stroke names and shortcut keys.
- [ ] **T-101**: Update `GestureEditorModal.tsx` to allow adding and editing custom command descriptions.

## Batch 3: UI Build, Standalone Packaging & Verification
- [ ] **T-102**: Rebuild UI Studio production bundle and sync into `src/ui_dist/` via `scripts/build_v3_ui.ps1`.
- [ ] **T-103**: Run `pytest` test suite, compile standalone `dist/RightWheel.exe` via PyInstaller, verify clean startup and push to remote Git.
