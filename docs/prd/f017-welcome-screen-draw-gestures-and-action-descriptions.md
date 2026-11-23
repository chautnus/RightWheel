# PRD — f017-welcome-screen-draw-gestures-and-action-descriptions

## 1. Goal
Modernize and customize the first Welcome Screen (`WelcomeView.tsx` / `welcome_window.py`) and Onboarding Wizard (`WizardView.tsx`) to 100% RightWheel mouse interactions, eliminate all remaining 3/4-finger touchpad terminology across all 7 supported languages, and add clear, localized action descriptions to every gesture in both the wizard and the main settings editor.

## 2. Requirements
- **FR-1: Multilingual Mouse Terminology across All 7 Locales**:
  - Replace all remaining references to 3-finger, 4-finger, and Touchpad in `src/core/i18n.py` (locales: `vi`, `en`, `fr`, `es`, `it`, `pt`, `id`) with Right Mouse & Wheel / Draw Gesture equivalents:
    - Vietnamese: "Giữ chuột phải & Vẽ (Draw Gesture)", "Giữ chuột phải + Cuộn bánh xe"
    - English: "Hold Right-Click & Draw Gesture", "Hold Right-Click + Scroll"
    - French, Spanish, Italian, Portuguese, Indonesian: equivalent localized terms.
- **FR-2: Action Descriptions for Gestures**:
  - In `WizardView.tsx`: Display both the trigger gesture (with shape icon/badge) AND the command's functional description (e.g., "Đóng tab hiện tại / Close Tab", "Mở tab mới / New Tab", "Quay lại trang trước / Back") alongside the keyboard shortcut badge `<Badge variant="kbd">`.
  - In `GesturesTab.tsx`: Show the gesture description in the row title and preview panel so users know what the action does at a glance.
  - In `GestureEditorModal.tsx`: Provide an editable "Mô tả lệnh (Description / Action Name)" input field so custom gestures can have meaningful descriptions.
- **FR-3: Configuration & Bridge Support**:
  - Ensure `DEFAULT_MOUSE_GESTURES` in `src/core/config_service.py` provides meaningful localized or descriptive labels.
  - Support `description?: string` and `label?: string` in `bridge/types.ts` and `bridge_api.py`.
- **FR-4: Production Build & Validation**:
  - Rebuild UI Studio with Vite and sync to `src/ui_dist/`.
  - Recompile standalone `dist/RightWheel.exe` and test clean startup without errors.

## 3. Non-Functional Requirements
- Strictly maintain UTF-8 encoding across all i18n dictionaries (zero mojibake).
- Do not affect global low-level mouse hooks or input latencies.
- Ensure all 16 automated pytest unit tests pass.
