---
id: ADR-002
title: "Kiến trúc GestureRecognizer độc lập, cơ chế Hủy Ngược RMB (Reverse Cancellation) và mở rộng X1/X2 Tab Switch"
status: accepted
date: 2026-11-08
tags: [gesture, mouse_mapper, architecture, chromium-tab, f003]
summary: "Tách GestureRecognizer thành module độc lập gọi từ MouseMapperLogic; xử lý OQ-2 bằng inject_right_up() tagged INJECTED_MARKER khi khớp preset để đóng sạch phiên drag Edge; bổ sung switch_tab_x1x2 độc lập; nâng version config lên v3."
---

## Context
F-003 cần 2 cơ chế thuần chuột khi giữ RMB: (1) X1/X2 chuyển tab (US-003), (2) gesture 8-hướng thực thi shortcut (US-004..US-006). Ràng buộc: không sửa switch_tab() gốc (F-001); Shift+Scroll giữ nguyên; LOCKED Behavior #1 chỉ đổi đúng phần state GESTURE (đã user phê duyệt); form cấu hình là dialog riêng, không đụng settings_window.py (149/150 dòng).

## Decision
1. **Module hóa Gesture Engine**: `src/features/mouse_mapper/logic/gesture_recognizer.py`, class `GestureRecognizer` (Streaming Incremental Vector Quantizer, O(1)/điểm). `MouseMapperLogic` sở hữu 1 instance, chuyển giao tọa độ trong `_on_move` khi RIGHT_HELD/GESTURE. Sửa `wants_moves()` trả `True` cho cả `RIGHT_HELD` và `GESTURE` (BUG THẬT đã phát hiện: hiện tại trả `False` khi GESTURE → không nhận move events).
2. **Cơ chế Hủy Ngược RMB (OQ-2)**: thêm `hotkey_service.inject_right_up()` (MOUSEEVENTF_RIGHTUP + dwExtraInfo=INJECTED_MARKER). Khi `right_up` ở state GESTURE và khớp preset: gọi `inject_right_up()` → `shortcut_executor.execute(keys)` → suppress right_up thật. Không khớp → fallback giữ nguyên hành vi hiện tại.
3. **Kênh X1/X2**: `WM_XBUTTONDOWN (0x020B)` mới trong `mouse_hook_service.py`, trích HIWORD(mouseData). `MouseMapperLogic._on_xbutton_down()` suppress nếu `_state != IDLE` (mọi app, theo OQ-3), gọi `switch_tab_x1x2()` nếu Chromium.
4. **Config v3**: version 2→3, thêm `"gestures"`: `[{"directions":["D","R"],"keys":"ctrl+w","enabled":true}]`, migration 2 chiều bảo toàn "default"/"profiles".
5. **UI Settings**: `GestureSettingsDialog` trong `gesture_settings_dialog.py` riêng, mở từ Tray menu, 0 dòng thêm vào `settings_window.py`.

## Rationale
- `inject_right_up()` tagged INJECTED_MARKER tránh Edge bị kẹt "RMB vẫn giữ" sau khi right_down đã inject sớm cho nó theo dõi.
- Tách GestureRecognizer giữ `mouse_mapper_logic.py` dưới ngưỡng 150 dòng (SRP).
- Hàm riêng `switch_tab_x1x2` cách ly hoàn toàn rủi ro với F-001.

## Options Considered
| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Streaming GestureRecognizer riêng + inject_right_up cleanup | O(1) latency, giữ giới hạn dòng, giải quyết kẹt Edge | +1 hàm mới trong hotkey_service | ✅ Chosen |
| Batch processing nhúng trong mouse_mapper_logic | Ít file mới | Vi phạm giới hạn 150 dòng, trễ lúc right_up | ❌ Rejected |
| Trì hoãn inject_right_down tới khi không khớp | Không cần cơ chế hủy ngược | Phá native gesture Edge (trái OQ-2) | ❌ Rejected |

## Consequences
**Positive**: Đạt đủ US-003..US-006; giải quyết xung đột trạng thái với Edge; không hỏng F-001; file ≤150 dòng.
**Trade-offs**: Edge có thể vẫn nhận diện gesture riêng của nó trước khi app đóng tab (trade-off đã chấp nhận ở elicitation).
**Risks**: Di chuột giật cục tạo hướng ngoài ý muốn → giảm bằng ngưỡng nét 18px + nén nét lặp.
