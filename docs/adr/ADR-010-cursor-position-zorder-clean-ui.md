# ADR-010: Z-Order Lifting, Cursor Positioning and Clean Typography

## Status
Accepted

## Context
Khi nâng cấp giao diện Raycast (F-010):
1. Chiều cao của panel tăng từ ~240px lên ~420px. Công thức cũ `y = py - h // 2` khiến `y` bị âm khi chuột ở nửa trên màn hình, dẫn đến việc cửa sổ nhảy lên đỉnh màn hình (`y = 0`).
2. Tkinter `toplevel.lift()` không có tham số không đảm bảo `self._win` xếp trên `self._overlay` khi cả hai đều mang cờ `-topmost True`, dẫn đến việc `self._overlay` nuốt toàn bộ sự kiện click chuột trái.
3. Người dùng yêu cầu loại bỏ hoàn toàn các biểu tượng emoticon / emoji trong toàn bộ giao diện menu và cửa sổ cài đặt.

## Decision
1. **Định vị góc trên-trái tại con trỏ chuột**:
   `x = max(10, min(px - 10, sw - _W - 10))`
   `y = max(10, min(py - 10, sh - h - 30))`
   Đảm bảo con trỏ chuột nằm ngay bên trong vùng trên-trái của panel, thao tác cuộn và nhả chuột tự nhiên.
2. **Khắc phục z-order**:
   Gọi `self._win.lift(self._overlay)` tường minh. Đã kiểm chứng qua Windows API `WindowFromPoint` trả về chính xác HWND của `self._win`.
3. **Typography thuần khiết (No Emoticons)**:
   - Xóa bỏ toàn bộ từ điển `_ICON` và nhãn emoji.
   - Thêm hàm `_strip_emojis` loại bỏ emoji khỏi nhãn người dùng.
   - Dọn sạch emoji trong sidebar `settings_window.py` và default presets trong `config_service.py`.

## Consequences
- Chuột trái hoạt động tin cậy 100%.
- Cửa sổ xuất hiện chuẩn xác ngay tại chuột.
- Giao diện đạt độ tinh tế, tối giản, chuyên nghiệp cao.
