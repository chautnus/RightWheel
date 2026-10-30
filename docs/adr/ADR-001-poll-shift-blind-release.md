---
id: ADR-001
title: "Dùng GetAsyncKeyState polling + blind-release-modifier cho gesture Shift+Scroll chuyển tab, không thêm keyboard hook riêng"
status: accepted
date: 2026-10-30
tags: [hook, keyboard, architecture, browser-gesture]
summary: "Poll VK_SHIFT ngay trong callback WM_MOUSEWHEEL đã có; inject Ctrl+Tab với kỹ thuật blind-release modifier (chuẩn AutoHotkey) thay vì thêm WH_KEYBOARD_LL hook."
---

## Context
Gesture Shift+scroll cần biết Shift đang giữ và gửi Ctrl+Tab (next)/Ctrl+Shift+Tab (previous) sạch. Phân tích ban đầu đề xuất thêm keyboard hook để chặn Shift thật — nhưng khi viết chi tiết task, phát hiện: (1) chặn Shift liên tục sẽ phá Shift+Click, gõ chữ HOA, Shift+Tab trong form — phạm vi hỏng lớn hơn mục tiêu; (2) hướng Ctrl+Shift+Tab (previous) không cần inject Shift gì cả vì Shift thật đã có sẵn; (3) chỉ hướng Ctrl+Tab (next) cần "ẩn" Shift thật — làm được bằng 1 lần inject KEYEVENTF_KEYUP cho VK_SHIFT ngay trước combo (không cần nhấn lại, vì phần cứng không tự phát lại sự kiện down khi tay giữ nguyên).

## Decision
Không thêm hook mới. Poll `GetAsyncKeyState(VK_SHIFT)` + `GetForegroundWindow()` ngay trong nhánh `WM_MOUSEWHEEL` của `mouse_hook_service.py` qua 1 callback mới `on_scroll_modifier` (optional, default `None` — không phá constructor hiện tại). Logic gating + inject nằm trong module logic mới `tab_switch_logic.py` + 1 hàm mới `switch_tab(forward)` trong `hotkey_service.py`.

## Rationale
Ít code hơn, không thêm diện rủi ro kernel hook, không có nguy cơ AV flag keylogger, không phá các hành vi Shift khác trong trình duyệt — vì ta chỉ suppress đúng 1 tick `WM_MOUSEWHEEL`, không suppress phím Shift liên tục.

## Options Considered
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Poll + blind-release | Ít code, không hook mới, không phá Shift+Click/HOA | Dựa vào hành vi OS-level (blind-release) cần test kỹ | ✅ Chosen |
| WH_KEYBOARD_LL suppress liên tục | Có hook riêng rõ ràng | Phá Shift+Click, gõ HOA, Shift+Tab form; thêm diện rủi ro hook | ❌ Rejected |
| Không hook, dùng Ctrl+PageUp/Down | Không cần hook | Shift thật lẫn vào → Ctrl+Shift+PageDown/Up = lệnh đảo chỗ tab (destructive) | ❌ Rejected |

## Consequences
Positive: Giữ nguyên mọi hành vi Shift khác trong browser; không đụng watchdog hiện có; ít file thay đổi hơn.
Trade-offs: Phải test kỹ hành vi "blind-release" trên Windows thật (không có overlay UI để confirm như Alt+Tab).
Risks: Nếu `GetAsyncKeyState` đọc sai thời điểm (race với lúc user vừa nhả Shift) có thể gửi nhầm combo ở tick cuối — chấp nhận được, tick kế tiếp (nếu còn) sẽ đúng lại.

### Test Contract
- `resolve_tab_direction(scroll_dir: ScrollDirection) -> bool` — pure, `AI-test:` gọi trực tiếp với `ScrollDirection.UP`/`ScrollDirection.DOWN`, assert `True`/`False`.
- `is_chromium_browser(exe_basename: str) -> bool` — pure, `AI-test:` gọi trực tiếp với `"chrome.exe"`, `"MSEDGE.EXE"` (case-insensitive), `"notepad.exe"`, assert kết quả đúng.
- Không có input người dùng dạng form/API nên không cần shape `{ok, data} | {ok:false, error:{...}}` đầy đủ — chỉ cần bool trả về đúng.
