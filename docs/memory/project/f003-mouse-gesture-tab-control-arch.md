# F-003 — Architecture notes (ADR-002)

Nguồn phân tích: Antigravity (ag-plan), Claude rà soát — 2026-11-08

- GestureRecognizer tách module riêng (`gesture_recognizer.py`) — Streaming Incremental Vector Quantizer, O(1)/điểm, KHÔNG nhúng vào `mouse_mapper_logic.py` (tránh vượt 150 dòng, giữ SRP).
- So sánh 3 option: streaming (chosen), batch polyline simplification (reject — trễ lúc right_up, vi phạm giới hạn dòng), DFA/automata (reject — overengineering cho 1-5 preset).
- Cơ chế "hủy ngược" (`inject_right_up()` tagged INJECTED_MARKER) giải quyết vấn đề Edge bị kẹt trạng thái RMB sau khi `right_down` đã inject sớm — đây là điểm kỹ thuật quan trọng nhất của ADR, cần nhớ khi debug sau này nếu Edge có hành vi lạ sau khi đóng tab bằng gesture.
- `wants_moves()` bug (GESTURE state không nhận move) được phát hiện qua "vòng mở rộng biến" của Antigravity — minh chứng giá trị của bước này trong pipeline ag-plan-arch.
