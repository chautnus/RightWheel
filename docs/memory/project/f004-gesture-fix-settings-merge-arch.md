# F-004 — Architecture notes (ADR-003)

Nguồn phân tích: Antigravity (ag-plan), Claude rà soát — 2026-11-08

- Pattern Collapse Rewrite (hậu kỳ) chọn thay vì sửa tận gốc quantizer — tránh phá cử chỉ chéo có chủ đích (preset tự thêm như ["DR"]).
- Silent Drop (không inject gì khi gesture không khớp) là chìa khoá triệt tiêu WM_CONTEXTMENU — khác hẳn thiết kế F-003 (giữ inject sớm + hủy ngược), đã chứng minh KHÔNG đủ (debug2 xác nhận context menu vẫn bật).
- Trade-off quan trọng cần nhớ: bỏ inject_right_down() sớm làm mất RMB-drag gốc của MỌI ứng dụng (Explorer, Photoshop, game...), không chỉ Edge — user đã xác nhận chấp nhận sau khi được hỏi rõ phạm vi thật.
- inject_right_down()/inject_right_up() trong hotkey_service.py trở thành dead code sau F-004, giữ lại có comment deprecated (không xoá, tránh vỡ API surface).
