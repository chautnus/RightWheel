# F-005 — Architecture notes (ADR-004)

Nguồn phân tích: Antigravity (ag-plan), Claude rà soát — 2026-11-08

- Root cause CHÍNH của "X1/X2 chỉ work lần đầu" không phải TrailOverlay cướp focus (debug1 nghĩ vậy) mà là thiếu cờ triệt tiêu sau Rocker Gesture khiến inject_right_click() tự bật context menu thật, menu modal khoá chết input — debug2 tìm ra qua đào vùng mù debug1 bỏ sót.
- WS_EX_NOACTIVATE/TRANSPARENT/LAYERED/TOOLWINDOW cho overlay — ghi nhớ: phải áp style vào HWND lấy qua GetParent(winfo_id()), không phải winfo_id() trực tiếp (quirk Tkinter Windows).
- Quyết định từ chối SetProcessDpiAwareness (ảnh hưởng DPI toàn app) — chỉ fix riêng việc neo _last_point từ GetCursorPos thật.
- Đây là lần thứ 3 liên tiếp (F-003→F-004→F-005) một thiết kế tưởng đã validate PASS vẫn lộ bug cấp OS khi test tay thật — củng cố NFR "test tay thật bắt buộc" cho mọi thay đổi liên quan Win32 window/focus/context-menu.
