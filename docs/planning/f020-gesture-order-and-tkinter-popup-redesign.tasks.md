# Tasks: f020-gesture-order-and-tkinter-popup-redesign

## Task Summary
- **Total Tasks**: 6
- **Batches**: 1 batch (`.batch-1.md`)

## Task List
- **T-114**: Sửa hàm `save()` trong `src/features/shortcut_panel/services/config_service.py` để đồng bộ hai chiều `data["default"]` vào `data["profiles"][0]["commands"]`, khắc phục lỗi mất phím tắt khi thêm từ ReferenceTab và IntentPickerDialog.
- **T-115**: Bổ sung nút hành động 1-click `[+ Thêm vào Lệnh]` trên mỗi dòng trong `C:\dev\ui-studio\src\projects\rightwheel-v3\components\ReferenceTab.tsx` và kết nối với `onAddCommand` trong `SettingsView.tsx`.
- **T-116**: Cập nhật `PRESETS` trong `C:\dev\ui-studio\src\projects\rightwheel-v3\components\GestureEditorModal.tsx` thành 16 cử chỉ nhóm theo nét đầu (U, D, L, R) tối đa 2 đoạn, loại bỏ hình khối (tam giác, vuông, tròn).
- **T-117**: Nâng cấp `sort_gestures()` và `_DRAW_GESTURE_ORDER` trong `src/core/config_service.py` theo đúng thứ tự phân cấp nét đầu.
- **T-118**: Thiết kế lại `panel_window.py` (bo tròn các góc popup bằng Win32 SetWindowRgn) và `panel_item_renderer.py` (highlight hàng được chọn màu xanh dương `#0078d4`, thanh cyan `#38bdf8`, padding hàng thoáng).
- **T-119**: Viết test hồi quy kiểm tra lưu phím từ Reference, chạy `scripts/build_v3_ui.ps1`, chạy `pytest` và biên dịch `dist/RightWheel.exe`.
