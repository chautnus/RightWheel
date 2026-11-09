## Elicitation — 2026-11-09

Problem:
Tính năng cử chỉ chuột Rocker Gesture (giữ chuột phải RMB + bấm nút phụ X1/X2 để chuyển tab trình duyệt) gây ra các lỗi hệ thống nghiêm trọng: kẹt nút chuột trái (Left click bị vô hiệu hóa), nút chuột phải (RMB) không kích hoạt được context menu do mất đồng bộ trạng thái chuột giữa low-level hook và Windows driver.

Goal:
Loại bỏ triệt để và sạch sẽ toàn bộ code liên quan đến cử chỉ X1/X2 khỏi hệ thống. Trả lại trạng thái hook chuột nguyên bản, nhẹ và ổn định 100% cho RightWheel.

Scope IN:
1. `mouse_hook_service.py`: Xóa bỏ việc chặn và xử lý `WM_XBUTTONDOWN`, xóa các hằng số `WM_XBUTTONDOWN`, `XBUTTON1`, `XBUTTON2`.
2. `mouse_mapper_logic.py`: Xóa bỏ cờ `_xbutton_used`, xóa nhánh `event.kind == "xbutton_down"`, xóa hàm `_on_xbutton_down`, dọn dẹp logic hoàn trả RMB trong `_on_right_up()` và `_on_right_down()`.
3. `hotkey_service.py`: Xóa bỏ hàm `switch_tab_x1x2()`.
4. `mouse_mapper_types.py`: Dọn dẹp loại sự kiện `"xbutton_down"`.
5. `reference_tab.py`: Xóa dòng hướng dẫn "RMB + X1/X2" trong bảng Reference tra cứu phím tắt.
6. Kiểm tra cú pháp, build lại `.exe`.

Scope OUT:
- Giữ nguyên cử chỉ Shift + Cuộn chuột chuyển tab Chromium (`tab_switch_logic.py`).
- Giữ nguyên cử chỉ vẽ chuột 8 hướng (`gesture_recognizer.py`, `trail_overlay.py`).
- Giữ nguyên toàn bộ State Machine chuẩn (Dual-mode scroll UP=Panel, DOWN=Alt+Tab).

Stories: US-027
Constraints: Mọi file mã nguồn ≤ 250 dòng (SYSTEM LOCK).


---

## PRD — 2026-11-09

Path: docs/prd/f009-remove-x1x2-rocker-gesture.md
Version: 1.0
Summary: Loại bỏ hoàn toàn cơ chế chặn nút phụ X1/X2 và hàm xử lý cử chỉ rocker gesture RMB + X1/X2. Khắc phục triệt để lỗi kẹt chuột trái (left click vô tác dụng) và lỗi chuột phải không kích hoạt do mất đồng bộ trạng thái chuột trong low-level hook.

---

## Architecture — 2026-11-09

Pattern: Safe Low-Level Mouse Hook Passthrough (Zero-Interference on Side Buttons)
ADR-008: Loại bỏ Hoàn toàn Cử chỉ Nút phụ X1/X2 (Rocker Gesture) Khắc phục Lỗi Kẹt Nút Chuột → docs/adr/ADR-008-remove-x1x2-rocker-gesture.md


---

## Tasks — 2026-11-09

Total: 4 tasks, 1.5h estimate
Path: docs/planning/f009-remove-x1x2-rocker-gesture.tasks.md
Batch 1: TSK-047, TSK-048
Batch 2: TSK-049, TSK-050
