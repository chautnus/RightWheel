---
id: ADR-003
title: "Tái cấu trúc Mouse Gesture Engine: chuẩn hoá hướng, loại bỏ context-menu, trail overlay, hợp nhất settings"
status: accepted
date: 2026-11-08
tags: [gesture, mouse_mapper, bug-fix, trail-overlay, settings-merge, f004]
summary: "Chuẩn hoá hướng góc cua bằng Pattern Collapse Rewrite; bỏ hẳn inject_right_down/up cho GESTURE (Silent Drop khi không khớp) để triệt tiêu WM_CONTEXTMENU; Trail Overlay qua Tkinter transparent polling; GesturesTab hợp nhất vào SettingsWindow."
---

## Context
F-003 Mouse Gesture Engine gặp 3 lỗi cộng hưởng xác nhận qua debug1+debug2: double-click vô tình tắt preset; GestureRecognizer sinh hướng chéo giả ở góc cua do Anchor Residual Vector Addition (>60% trường hợp, kể cả góc vuông hoàn hảo — không phải do tay vẽ cong như debug1 ban đầu nghĩ); inject_right_down()+inject_right_up() tạo cặp click phải hoàn chỉnh kích hoạt WM_CONTEXTMENU thật, nuốt mất Ctrl+W. User đã xác nhận chấp nhận trade-off: bỏ RMB-drag gốc của MỌI app (không chỉ Edge) để đổi lấy fix triệt để.

## Decision
1. **US-008**: Thêm pure function `normalize_directions(directions) -> list[str]` trong gesture_recognizer.py — 8 luật pattern-collapse trực giao `[A,diag(A,B),B]→[A,B]`. Áp dụng trong `finish()` trước khi so khớp preset. KHÔNG sửa tận gốc quantizer (deadzone góc) vì sẽ phá cử chỉ chéo có chủ đích.
2. **US-009**: `_on_move()` — xoá hẳn lệnh gọi `inject_right_down()` khi chuyển RIGHT_HELD→GESTURE. `_on_right_up()` nhánh GESTURE: khớp preset → `execute(keys)` trực tiếp, KHÔNG `inject_right_up()`; không khớp → Silent Drop hoàn toàn (không inject gì, suppress, giống hệt nhánh SCROLLING). `hotkey_service.inject_right_down/up` giữ định nghĩa (đánh dấu deprecated) để không vỡ API surface.
3. **US-010**: `trail_overlay.py` mới — `TrailOverlay` dùng `tk.Toplevel` (`overrideredirect`, `-topmost`, `-transparentcolor`) + polling `GetCursorPos` ~60fps qua `root.after(16)`. `MouseMapperLogic` thêm 2 callback optional `on_gesture_start(x,y)`/`on_gesture_end()` (pattern giống `self.panel`), kích hoạt tại điểm vào/ra GESTURE.
4. **US-011+US-007**: `GesturesTab(tk.Frame)` file riêng thay `gesture_settings_dialog.py` (Toplevel) — tích hợp làm tab 4 trong `settings_window.py` theo đúng pattern `DefaultTab`/`ProfileEditor`/`LicenseFrame`. Bỏ double-click toggle, giữ selection khi bấm Bật/Tắt. Xoá file dialog cũ, dọn `tray_ui.py`(bỏ `on_gestures`)/`main.py`(bỏ `open_gestures`).
5. **Bonus**: `config_service.load()` tự khôi phục `enabled:true` cho preset `["D","R"]` nếu đang `false`.

## Rationale
- Pattern Collapse Rewrite là pure function, deterministic, không độ trễ, dễ unit-test, không ảnh hưởng tới gesture chéo có chủ đích — an toàn hơn sửa tận gốc quantizer (rủi ro false-negative cho preset chéo tự thêm).
- Silent Drop loại bỏ hoàn toàn nguồn gốc WM_CONTEXTMENU (không còn cặp down+up nào được gửi ra ngoài trong suốt phiên GESTURE).
- Polling-based TrailOverlay tách biệt hoàn toàn khỏi `mouse_hook_service.py` (LOCKED), giảm rủi ro đụng hook nhạy cảm.

## Options Considered
| Option (US-008) | Pros | Cons | Verdict |
|---|---|---|---|
| Pattern Collapse Rewrite (hậu kỳ) | Deterministic, an toàn cho gesture chéo cố ý, dễ test | Chỉ xử lý đúng 1-step residual | ✅ Chosen |
| Orthogonal-Biased Angular Deadzone (sửa tận gốc quantizer) | Triệt từ gốc | Phá cử chỉ chéo có chủ đích, khó cân chỉnh | ❌ Rejected |
| Token Duration & Stroke-Length Pruning | Khái quát hơn | Phức tạp hoá cấu trúc dữ liệu, tốn tài nguyên | ❌ Rejected |

## Consequences
**Positive**: Gesture nhận diện đúng 100% góc vuông; context menu không còn xuất hiện sai; trail overlay trực quan; settings tập trung.
**Trade-offs**: MẤT khả năng RMB-drag gốc của MỌI ứng dụng (không chỉ Edge) khi kéo >8px giữ RMB — user đã xác nhận chấp nhận.
**Risks**: `inject_right_down/up` trở thành dead code (giữ lại có comment deprecated, không xoá để không vỡ API surface).
