# BATCH 2: Directional Pattern Visualizer & Command Palette Sync

feature: f016-v3-ui-rightwheel-customization-and-draw-gestures
batch: 2
tasks: T-92, T-93, T-94

## Tasks

### T-92: Upgrade TouchpadVisualizer.tsx to Mouse Draw Visualizer with Directional Arrows
- In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\TouchpadVisualizer.tsx`:
  - Định nghĩa SVG `<defs>` chứa marker mũi tên (`<marker id="arrowhead" ...>`).
  - Gắn điểm xuất phát: Chấm tròn xanh phát sáng (`● Bắt đầu / Start`) tại tọa độ ban đầu `(x0, y0)` của từng nét vẽ.
  - Gắn `marker-end="url(#arrowhead)"` cho các path để người dùng thấy rõ hướng kéo chuột.
  - Cho các nét nhiều đoạn (như `D_R`, `U_R_D`, `Z_SHAPE`), bổ sung mũi tên chỉ hướng dọc theo từng phân đoạn.
  - Thay thế các dấu chấm ngón tay bằng huy hiệu chuột `🖱️ Giữ chuột phải & kéo vẽ`.

### T-93: Clean CommandEditorModal.tsx & CommandsTab.tsx
- In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\CommandEditorModal.tsx`:
  - Thay placeholder `Touchpad Settings...` thành `RightWheel Settings...`.
  - Thay option `open_settings (Touchpad Settings)` thành `open_settings (Cài đặt RightWheel)`.
- In `C:\dev\ui-studio\src\projects\rightwheel-v3\components\CommandsTab.tsx`:
  - Đảm bảo các nhãn và badge đồng bộ với RightWheel.

### T-94: Rebuild UI Studio Production Bundle & Sync
- Chạy script `scripts/build_v3_ui.ps1`:
  - Build `C:\dev\ui-studio` với target `build:rightwheel-v3`.
  - Đồng bộ sản phẩm build từ `C:\dev\ui-studio\dist-rightwheel-v3` sang `src/ui_dist/`.
  - Kiểm tra các file `index.html`, `index-*.js`, `index-*.css` đã được cập nhật mới.

## Verification
- Test-Path `src/ui_dist/index.html` và kiểm tra timestamp mới nhất.
