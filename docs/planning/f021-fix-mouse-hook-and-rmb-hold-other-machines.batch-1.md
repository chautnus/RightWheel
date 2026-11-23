# Batch 1: f021-fix-mouse-hook-and-rmb-hold-other-machines

## Tasks
- T-120: Chuẩn hóa Win64 API signatures trong `src/features/mouse_mapper/services/mouse_hook_service.py`.
- T-121: Chống tràn sự kiện chuột 1000Hz (anti-timeout sampling) và bổ sung diagnostic logging trong `mouse_hook_service.py`.
- T-122: Khắc phục race condition khởi tạo `TrailOverlay` trong `trail_overlay.py` & `main.py`.
- T-123: Giảm `move_threshold` về 16px trong `mouse_mapper_types.py` & `mouse_mapper_logic.py`, hỗ trợ chuột tay trái.
- T-124: Bổ sung "Chạy dưới quyền Administrator" và "Sao chép chẩn đoán" trong `tray_ui.py`.
- T-125: Chạy unit tests, static syntax validation, và recompile `dist/RightWheel.exe`.
