# F-009 — Architecture notes (ADR-008)

Nguồn phân tích: thực thi qua kênh khác (không qua MCP bridge của session này) — Claude validate độc lập 2026-11-10.

- Loại bỏ hoàn toàn cơ chế X1/X2 rocker gesture (thêm ở F-003, vá tạm ở restart-dll-gesture-dead fix với cờ `_xbutton_used`) — nguyên nhân gốc "left-click stuck/RMB tê liệt" là lệch pha WM_XBUTTONDOWN/UP trong driver Windows, không thể vá triệt để bằng app-level flag, quyết định bỏ hẳn tính năng.
- Xoá sạch: `WM_XBUTTONDOWN` interception (`mouse_hook_service.py`), `_on_xbutton_down`/`_xbutton_used` (`mouse_mapper_logic.py`), `switch_tab_x1x2` (`hotkey_service.py`). `git grep xbutton` = 0 kết quả, xác nhận dọn sạch.
- KHÔNG đụng core state machine LOCKED (`_on_right_down`/`_on_move`/`_on_scroll`/`_on_right_up` giữ cấu trúc nguyên vẹn, chỉ bỏ nhánh check đã không còn tồn tại). Watchdog `is_alive()` fix (từ restart-dll-gesture-dead) vẫn còn nguyên sau đợt này.
