# ADR Index

| id | summary | tags | status | file |
|----|---------|------|--------|------|
| ADR-001 | Poll VK_SHIFT ngay trong callback WM_MOUSEWHEEL đã có; inject Ctrl+Tab với kỹ thuật blind-release modifier (chuẩn AutoHotkey) thay vì thêm WH_KEYBOARD_LL hook. | hook, keyboard, architecture, browser-gesture | accepted | [ADR-001-poll-shift-blind-release.md](ADR-001-poll-shift-blind-release.md) |
| ADR-002 | Tách GestureRecognizer thành module độc lập gọi từ MouseMapperLogic; xử lý OQ-2 bằng inject_right_up() tagged INJECTED_MARKER khi khớp preset để đóng sạch phiên drag Edge; bổ sung switch_tab_x1x2 độc lập; nâng version config lên v3. | gesture, mouse_mapper, architecture, chromium-tab, f003 | accepted | [ADR-002-gesture-engine-architecture.md](ADR-002-gesture-engine-architecture.md) |
