# Tasks: Remove X1/X2 Rocker Gesture & Fix Mouse Button Hangs (f009-remove-x1x2-rocker-gesture)

Total: 4 tasks | Estimate: 1.5h | Status: 4/4 Done

## Tasks List

### Batch 1: Core Hook & State Machine Cleanup
- [x] **TSK-047**: Gỡ bỏ can thiệp `WM_XBUTTONDOWN` trong `src/features/mouse_mapper/services/mouse_hook_service.py` (US-027).
- [x] **TSK-048**: Dọn dẹp cờ `_xbutton_used` và xóa bỏ `_on_xbutton_down` trong `src/features/mouse_mapper/logic/mouse_mapper_logic.py` (US-027).

### Batch 2: Support Services, UI & Rebuild
- [x] **TSK-049**: Dọn dẹp `hotkey_service.py` (xóa `switch_tab_x1x2`), `mouse_mapper_types.py` và `reference_tab.py` (US-027).
- [x] **TSK-050**: Kiểm tra tĩnh cú pháp (py_compile), kiểm tra giới hạn dòng (≤ 250 dòng), đóng tiến trình và build lại `dist/RightWheel.exe` (US-027).
