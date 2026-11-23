# BATCH 2/3: React UI Updates & Gesture Descriptions

## Task T-99: Update `WelcomeView.tsx` Bento Cards and Actions
- **File**: `C:\dev\ui-studio\src\projects\rightwheel-v3\views\WelcomeView.tsx`
- **Goal**:
  - Ensure Bento card 1, 2, 3 explicitly teach:
    1. RMB + Scroll UP: Bảng phím tắt nhanh (Shortcut Panel / Radial Command Palette).
    2. RMB + Drag / Draw: Cử chỉ vẽ chuột & vệt sáng Neon (Mouse Gestures & Trail).
    3. RMB + Scroll DOWN: Chuyển đổi ứng dụng (Task Switcher) & Hồ sơ theo ứng dụng (Per-App Profiles).
- **Verify**: `npm run build:rightwheel-v3` succeeds with 0 errors.

## Task T-100: Update `WizardView.tsx` and `GesturesTab.tsx`
- **File**: `C:\dev\ui-studio\src\projects\rightwheel-v3\views\WizardView.tsx`, `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GesturesTab.tsx`
- **Goal**:
  - In `WizardView.tsx`: Render each gesture with:
    - Gesture stroke name and visual trigger: `🖱️ Giữ chuột phải + Kéo vẽ: [Shape]` / `🖱️ Giữ chuột phải + Cuộn: [UP/DOWN]`
    - Description of command: `{g.description || g.label || "Thao tác phím tắt"}`
    - Key combo badge: `<Badge variant="kbd">{g.target}</Badge>`
  - In `GesturesTab.tsx`:
    - Show description `{g.description || g.label}` in the gesture row list and details preview.
- **Verify**: `npm run build:rightwheel-v3` succeeds.

## Task T-101: Update `GestureEditorModal.tsx`
- **File**: `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GestureEditorModal.tsx`
- **Goal**:
  - Add "Mô tả / Tên chức năng (Description / Action Name)" input field.
  - When saving, persist `description` and `label` to the gesture object.
- **Verify**: Modal opens and edits description cleanly.
