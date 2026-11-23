# Context — f017-welcome-screen-draw-gestures-and-action-descriptions

## User Request
1. "Bỏ cử chỉ 3.4 ngón. Đổi thành: Giữ chuột phải, Draw gesture (lưu ý đa ngôn ngữ)"
2. "Ở các phần cử chỉ, có thể thêm phần mô tả chức năng của câu lệnh được ko"

## Analysis & Current State
1. **Welcome Screen (`WelcomeView.tsx` & `src/core/i18n.py`)**:
   - `src/core/i18n.py` had leftover strings referencing "3 & 4 fingers" and "Precision Touchpad" in `welcome_step1-4`, `welcome_bento_1_title` ("Vuốt 3 ngón lên"), `welcome_bento_2_title` ("Tùy biến cử chỉ 3 & 4 ngón"), across all 7 supported languages.
   - We need to completely eliminate any remaining references to 3-finger or 4-finger gestures across all language dictionaries (`vi`, `en`, `fr`, `es`, `it`, `pt`, `id`), replacing them with Right Mouse & Wheel / Draw gestures ("Giữ chuột phải + Cuộn", "Giữ chuột phải & Vẽ cử chỉ").
2. **Gesture Function / Action Description**:
   - Currently, in `WizardView.tsx` and `GesturesTab.tsx`, gestures only show their shape or direction (`Vẽ: D_R`, `Vẽ: U_R`, `Vẽ: L`, `Vẽ: R`) and raw key target (`ctrl+w`, `ctrl+t`, `alt+left`).
   - Users cannot immediately know WHAT the command does without memorizing shortcuts.
   - We will:
     a) Add a dedicated `description` / `label` field to each gesture item in `DEFAULT_MOUSE_GESTURES` and `bridge/types.ts`.
     b) Provide human-readable, multilingual action descriptions:
        - `D_R` (`ctrl+w`) -> "Đóng tab hiện tại / Close current tab"
        - `U_R` (`ctrl+t`) -> "Mở tab mới / Open new tab"
        - `L` (`alt+left`) -> "Quay lại trang trước / Back"
        - `R` (`alt+right`) -> "Đi tới trang kế / Forward"
        - `wheel_UP` (`COMMAND_PALETTE`) -> "Bảng phím tắt nhanh / Quick Shortcut Panel"
        - `wheel_DOWN` (`ALT_TAB`) -> "Chuyển đổi ứng dụng / Task Switcher"
     c) Update `WizardView.tsx` and `GesturesTab.tsx` to render this description prominently with a badge or subtitle.
     d) Add a description/label input in `GestureEditorModal.tsx` so users can edit the command description.
