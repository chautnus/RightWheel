# Tasks: f021-fix-mouse-hook-and-rmb-hold-other-machines

## Task Summary
- **Total Tasks**: 6
- **Batches**: 1 batch (`.batch-1.md`)

## Task List
- **T-120**: Chuẩn hóa Win64 API signatures và kiểu `LRESULT` cho `_HookProc`, `CallNextHookEx`, `SetWindowsHookExW` trong `mouse_hook_service.py`.
- **T-121**: Bổ sung cơ chế spatial sampling ($\ge 2$px) và rate-limiting (~125Hz) cho `WM_MOUSEMOVE` trong `mouse_hook_service.py` để ngăn chặn `LowLevelHooksTimeout` trên chuột gaming 1000Hz.
- **T-122**: Sửa race condition khởi tạo `TrailOverlay` trong `trail_overlay.py` và `main.py` bằng callable `root_getter`.
- **T-123**: Điều chỉnh `move_threshold` từ 50px xuống 16px trong `mouse_mapper_types.py` và `mouse_mapper_logic.py`, hỗ trợ `SM_SWAPBUTTON`.
- **T-124**: Thêm tính năng "Chạy với quyền Administrator", hiển thị trạng thái Hook và "Sao chép chẩn đoán chuột" trong `tray_ui.py`.
- **T-125**: Viết unit test kiểm thử các cải tiến hook, chạy `pytest`, và recompile `dist/RightWheel.exe`.
