---
id: ADR-004
title: "Khắc phục 5 lỗi cốt lõi F-004: Rocker Gesture Context Menu, Win32 NoActivate Overlay, Trail Cursor Anchor, Move Threshold, PyInstaller Restart Detached"
status: accepted
date: 2026-11-08
tags: [gesture, mouse_mapper, trail_overlay, rocker_gesture, pyinstaller, bug-fix, f005]
summary: "Cờ _xbutton_used triệt tiêu context menu sau X1/X2; WS_EX_NOACTIVATE+TRANSPARENT+LAYERED+TOOLWINDOW qua SetWindowLongPtrW 64-bit cho TrailOverlay; _last_point từ GetCursorPos thật; khôi phục move_threshold=50; _restart() dùng subprocess.Popen detached."
---

## Context
Sau F-004, test tay thật phát hiện 5 lỗi: Rocker Gesture X1/X2 chỉ work lần đầu (context menu modal Chromium khoá chết thao tác sau — do _on_xbutton_down không set cờ, _on_right_up coi là click phải thường); TrailOverlay thiếu WS_EX_NOACTIVATE cướp focus Chromium; dây cung thẳng do _last_point neo vào toạ độ _down cũ trong khi Canvas mất 20-50ms khởi tạo; move_threshold=8 hardcode trong main.py đè default 50, kết hợp Silent Drop F-004 nuốt mất context menu thường khi rung tay; os.execve trên Windows giữ handle DLL khiến PyInstaller bootloader lỗi xoá _MEI khi Restart. debug1+debug2 (phán quyết CẢ HAI ĐỀU GÓP PHẦN) định vị chính xác 5 nguyên nhân.

## Decision
1. **US-012**: `self._xbutton_used: bool = False` trong `__init__`, reset `False` trong `_on_right_down`. `_on_xbutton_down`: set `True` khi `switch_tab_x1x2()` gọi thành công. `_on_right_up` nhánh `prev==RIGHT_HELD`: nếu `_xbutton_used` → bỏ qua `inject_right_click()`, reset cờ, `return True`.
2. **US-013**: Lấy HWND thật của overlay qua `GetParent(win.winfo_id())` (Tkinter-on-Windows quirk: `winfo_id()` trả về client-frame HWND, top-level HWND thật nằm ở `GetParent()`). Dùng `SetWindowLongPtrW`/`GetWindowLongPtrW` (fallback `SetWindowLongW` nếu không có, đúng kiểu `c_ssize_t`/`HWND` cho 64-bit) OR thêm `WS_EX_NOACTIVATE(0x08000000)|WS_EX_TRANSPARENT(0x20)|WS_EX_LAYERED(0x80000)|WS_EX_TOOLWINDOW(0x80)` vào `GWL_EXSTYLE(-20)`.
3. **US-014**: Trong `_do_start`, sau khi Canvas sẵn sàng, gọi `GetCursorPos()` thật, gán `_last_point` từ đó (trừ vx,vy) thay vì toạ độ `(x,y)` truyền vào từ `_down` cũ. KHÔNG thêm `SetProcessDpiAwareness` (từ chối — ảnh hưởng DPI toàn app).
4. **US-015**: `main.py`: `MouseMapperLogic()` không truyền `move_threshold`, dùng default 50 từ `HotkeyConfig`.
5. **US-016**: `tray_ui.py _restart()`: `subprocess.Popen(cmd, shell=True, env=env, creationflags=DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP)` với `cmd` dùng `ping 127.0.0.1 -n 2 > nul & "<exe>" <args>` (ping thay vì `timeout` vì `timeout.exe` lỗi "Input redirection not supported" khi chạy từ process detached không có console thật) rồi `sys.exit(0)`.

## Rationale
- Cờ `_xbutton_used` giải quyết triệt để root cause chính (context menu modal khoá chết input) mà không đổi cấu trúc `MapperState`.
- `GetParent()` cho đúng HWND top-level thật — áp style vào sai handle (chỉ `winfo_id()`) sẽ khiến fix US-013 không có tác dụng.
- `GetCursorPos` thật tại thời điểm Canvas sẵn sàng loại bỏ toàn bộ chuỗi nguyên nhân latency+DPI mà không cần đổi DPI awareness toàn app.
- `ping` thay `timeout` tránh lỗi console redirection trên process detached — bài học thực tế triển khai Windows.

## Options Considered
N/A — 5 quyết định đã chốt ở elicitation (user đã xác nhận hướng sửa cụ thể từ debug2), ADR này ghi lại thiết kế chi tiết + lý do kỹ thuật, không đề xuất lại hướng khác.

## Consequences
**Positive**: Context menu không còn bật nhầm sau X1/X2; Chromium không mất focus khi vẽ gesture; trail mượt không dây cung; click phải thường hoạt động đúng; Restart không lỗi.
**Trade-offs**: Điểm bắt đầu nét vẽ hụt ~10-20px đầu tiên (đổi lấy việc không có đường thẳng dị thường) — chấp nhận được.
**Risks**: Không refactor mouse_hook_service.py đợt này — rủi ro treo hook do gọi Win32 đồng bộ (GetWindowTextW/SendInput) trong _hook_proc vẫn còn, theo dõi tiếp ở phiên sau nếu triệu chứng tái diễn.
