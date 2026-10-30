# PRD — Shift+Scroll chuyển tab (F-001, slug: f001-shift-scroll-tab-switch) v1.0

**Date:** 2026-10-30

## Overview
**Problem:** Chuyển tab trong Chrome/Edge/Chromium bắt buộc rời chuột để bấm Ctrl+Tab hoặc click tab bar — gây gián đoạn khi tay đang để trên chuột.
**Success Metrics:** Giữ Shift + lăn wheel chuyển đúng tab kế tiếp/trước trong cửa sổ Chromium đang active, mỗi tick = 1 lần chuyển, không phá vỡ hệ gesture RMB+scroll hiện có, không phá các hành vi Shift khác trong trình duyệt (Shift+Click, gõ chữ HOA, Shift+Tab trong form).

## JTBD
Khi đang lướt nhiều tab trình duyệt và tay đang ở trên chuột, tôi muốn chuyển tab bằng cách giữ Shift + lăn wheel, để không phải rời tay sang bàn phím.

## User Stories
- **US-001:** As a user, I want giữ Shift + scroll UP để chuyển sang tab kế tiếp (next, Ctrl+Tab) và scroll DOWN để chuyển về tab trước (previous, Ctrl+Shift+Tab), khi cửa sổ Chrome/Edge/Chromium-based đang active.
- **US-002:** As a user, I want gesture này ưu tiên tuyệt đối trên hành vi scroll-ngang native (Shift+wheel) trong trình duyệt — không cuộn ngang khi Shift đang giữ trong cửa sổ browser — nhưng KHÔNG ảnh hưởng tới các dùng Shift khác (Shift+Click, gõ chữ HOA, Shift+Tab trong form, Shift+mũi tên chọn text).

## Out of Scope
- Toggle on/off trong Settings UI (luôn bật sẵn, không cấu hình).
- Trình duyệt không phải Chromium (Firefox, Safari...).
- Xử lý nhiều cửa sổ Chromium song song (chỉ tab của cửa sổ đang foreground).
- Logging/lưu trữ bất kỳ phím nào ngoài kiểm tra tức thời VK_SHIFT.
- Keyboard hook mới / watchdog mở rộng (loại bỏ sau ADR-001 rev2 — xem phần Architecture).

## Dependencies / Constraints
- Windows-only, `ctypes` thuần (không psutil) — nhất quán với `window_service.py`.
- Tái dùng `window_service.get_hwnd_info()` để lấy `exe_basename` gate theo danh sách Chromium (chrome.exe, msedge.exe, brave.exe, opera.exe, vivaldi.exe).
- KHÔNG tái dùng pattern `begin_switch/cycle/end_switch` (đó là cho Alt+Tab có overlay UI giữ Alt qua nhiều Tab) — Ctrl+Tab chuyển tab ngay lập tức, không cần giữ phím qua nhiều lần, nên chỉ cần 1 hàm `switch_tab(forward)` gửi đủ 1 combo mỗi lần gọi.
- KHÔNG thêm hook mới — dùng `GetAsyncKeyState(VK_SHIFT)` polling ngay trong callback `WM_MOUSEWHEEL` đã có ở `mouse_hook_service.py`.
- Không được phá vỡ LOCKED behaviors #1-#8 trong `CLAUDE.md` (state machine RMB+scroll) — không sửa `mouse_mapper_logic.py`.

## Non-Functional Requirements
- **Performance:** Logic Shift+scroll chỉ chạy khi có `WM_MOUSEWHEEL` thật (không phải sự kiện tần suất cao như `WM_MOUSEMOVE`), nên không cần fast-path riêng như `wants_moves()`.
- **Security/Privacy:** Không log/lưu bất kỳ phím nào — chỉ đọc tức thời `GetAsyncKeyState(VK_SHIFT)` tại đúng thời điểm scroll, không có state/buffer lưu trữ phím.
- **Compatibility:** Không đổi chữ ký hàm/constructor hiện có (`MouseHookService.__init__`, các hàm trong `hotkey_service.py`) — chỉ thêm tham số optional / hàm mới.
