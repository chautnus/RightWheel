# BATCH 1: React UI Customization for RightWheel & Draw Gestures

feature: f016-v3-ui-rightwheel-customization-and-draw-gestures
batch: 1
tasks: T-89, T-90, T-91

## Tasks

### T-89: Update WelcomeView.tsx & WizardView.tsx
- Rewrite `C:\dev\ui-studio\src\projects\rightwheel-v3\views\WelcomeView.tsx` & `WizardView.tsx`:
  - Highlight 3 core mouse actions:
    1. Chuột phải + Cuộn lên (RMB + Scroll UP): Mở Bảng lệnh nhanh (Command Palette).
    2. Chuột phải + Cuộn xuống (RMB + Scroll DOWN): Trình chuyển đổi Tab & Tác vụ (Task Switcher).
    3. Chuột phải + Kéo vẽ (RMB + Draw): Kích hoạt cử chỉ vẽ chuột (Draw Gestures) với vệt vẽ neon.
  - Wizard Step 1: Chuột & Cử chỉ mặc định (thay vì kiểm tra Precision Touchpad).
  - Wizard Step 2: Hướng dẫn giữ chuột phải và vẽ hoặc cuộn chuột.
  - Xóa mọi thông điệp về "PTP Hardware Ready" và "Vuốt 3 ngón".

### T-90: Clean SettingsView.tsx, GeneralTab.tsx & ProfileWorkspace.tsx
- In `C:\dev\ui-studio\src\projects\rightwheel-v3\views\SettingsView.tsx`:
  - Thay title fallback `"Touchpad Gesture"` thành `"RightWheel"`.
  - Thay badge PTP thành `"RMB + Wheel Sẵn sàng"`.
- In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GeneralTab.tsx`:
  - Loại bỏ hoàn toàn card "Cử chỉ Precision Touchpad mặc định của Windows" và các nút Windows Touchpad settings.
  - Giữ lại các cài đặt: Khởi động cùng Windows, Ngôn ngữ, và Hiển thị vệt vẽ cử chỉ chuột (Trail Overlay).
- In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\ProfileWorkspace.tsx`:
  - Đổi tab title thành `"Cử chỉ vẽ chuột"` / `"Draw Gestures"`.

### T-91: Reconfigure GestureEditorModal.tsx & GesturesTab.tsx
- In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GestureEditorModal.tsx`:
  - Xóa bộ chọn số ngón tay (`[3 ngón] [4 ngón]`).
  - Cập nhật `PRESETS` chỉ bao gồm các nét vẽ chuột:
    - Nét thẳng: Lên (U), Xuống (D), Trái (L), Phải (R).
    - Góc vuông: Xuống-Phải (D_R), Xuống-Trái (D_L), Lên-Phải (U_R), Lên-Trái (U_L), Phải-Lên (R_U), Phải-Xuống (R_D), Trái-Lên (L_U), Trái-Xuống (L_D), Hai chiều (U_D, D_U, L_R, R_L).
    - Zigzag: Lên-Phải-Xuống (U_R_D), Xuống-Phải-Lên (D_R_U), Trái-Xuống-Phải (L_D_R), Phải-Xuống-Trái (R_D_L).
    - Hình vẽ: CIRCLE, SQUARE, TRIANGLE, Z_SHAPE, N_SHAPE.
- In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GesturesTab.tsx`:
  - Hiển thị danh sách dạng: `Vẽ: ${g.label || g.shape || g.direction}`.
  - Bỏ kiểm tra khóa "cử chỉ 3-ngón-LÊN".

## Verification
- Run `npm --prefix "C:\dev\ui-studio" run build:rightwheel-v3` to ensure no TypeScript compilation errors.
