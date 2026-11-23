# PRD: f021-fix-mouse-hook-and-rmb-hold-other-machines

## 1. Problem Statement
Ứng dụng RightWheel khi đóng gói và chuyển sang máy tính khác (hoặc môi trường mới) không nhận diện được thao tác bấm và giữ chuột phải (RMB hold), dẫn đến không thể vẽ cử chỉ, mở Command Palette, hoặc chuyển đổi ứng dụng.

## 2. Requirements

### FR-001: Chuẩn hóa chữ ký Win64 Hook & Chống nghẽn sự kiện (Anti-timeout)
- Cập nhật `_HookProc` trả về `ctypes.c_ssize_t` (`LRESULT`).
- Khai báo đầy đủ `argtypes` cho `SetWindowsHookExW`, `CallNextHookEx`, `UnhookWindowsHookEx`.
- Áp dụng spatial sampling ($\ge 2$px) và rate-limiting tối đa 125Hz cho `WM_MOUSEMOVE` trong `_hook_proc` để tránh bị Windows unhook do vượt `LowLevelHooksTimeout`.

### FR-002: Khắc phục Race Condition của TrailOverlay
- Cho phép `TrailOverlay` nhận một `root_getter` callable để luôn phân giải `panel_window._root` động tại thời điểm vẽ.
- Đảm bảo vệt vẽ neon hiển thị 100% ngay từ nét vẽ đầu tiên.

### FR-003: Giảm & Tùy biến `move_threshold`
- Giảm `move_threshold` từ 50px xuống 16px.
- Đồng bộ giá trị từ `app_settings.json` nếu có cấu hình.
- Thích ứng với chuột tay trái qua kiểm tra `SM_SWAPBUTTON`.

### FR-004: Chẩn đoán & Quản lý Quyền Administrator
- Bổ sung menu Tray:
  - "Chạy với quyền Administrator (Khuyên dùng)" để khởi động lại elevated qua `runas`.
  - Hiển thị trạng thái Hook trên khay hệ thống.
  - "Sao chép chẩn đoán chuột" vào Clipboard.
- Ghi log chi tiết vào `app_debug.log`.
