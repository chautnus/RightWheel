# F-007 — Architecture notes (ADR-006)

Nguồn phân tích: thực thi qua kênh khác (không qua MCP bridge của session này) — Claude validate độc lập 2026-11-10.

- Redesign toàn diện Settings Window từ `ttk.Notebook` tab ngang sang layout 2 cột Sidebar Navigation (190px sidebar + content area) — xem `settings_window.py`.
- Tách `general_volume_tab.py` làm module riêng cho General (startup/language) + Volume (step %, show_panel_volume) thay vì nhồi vào settings_window.py.
- Quick Volume Bar tích hợp trên đỉnh Shortcut Panel + Capsule Volume HUD (224x46px) — không đụng `mouse_mapper/` LOCKED (xác nhận qua `git show --stat`).
