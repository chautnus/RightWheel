# Context: f021-fix-mouse-hook-and-rmb-hold-other-machines

## Background
- User báo: "chạy ở máy khác không nhận được thao tác bấm và giữ chuột phải".
- Khi chạy trên máy khác, thao tác bấm giữ chuột phải (RMB hold) để vẽ cử chỉ, mở Command Palette (RMB+Scroll Up), hoặc chuyển tab/app (RMB+Scroll Down) không hoạt động.

## Key Insights & Root Causes
1. `move_threshold = 50px`: Quá lớn đối với chuột văn phòng/touchpad và màn hình 1080p, khiến cử chỉ ngắn (<50px) không bao giờ kích hoạt `GESTURE`. Giảm về 16px.
2. `TrailOverlay` `_root` race condition: `panel_window._root` chưa khởi tạo xong tại thời điểm `main.py` gán cho `TrailOverlay`, dẫn đến `self._root` luôn là `None`, không vẽ được vệt cử chỉ.
3. Chuột gaming 1000Hz gây vượt ngưỡng `LowLevelHooksTimeout` (200-300ms) khiến Windows âm thầm unhook `WH_MOUSE_LL`. Cần spatial sampling (delta >= 2px) & rate limit (~125Hz).
4. Win64 HookProc signature mismatch: `c_long` (32-bit) thay vì `LRESULT` (64-bit `c_ssize_t`).
5. UAC / UIPI: Khi RightWheel chạy non-elevated, các cửa sổ chạy quyền Administrator sẽ chặn `WH_MOUSE_LL` và `SendInput`. Cung cấp tùy chọn Restart as Admin và hiển thị trạng thái Hook trên Tray menu.
