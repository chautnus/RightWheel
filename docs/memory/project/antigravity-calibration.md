# Antigravity Calibration — thống kê chất lượng thực thi per batch
Mục đích: plan-tasks đọc để chỉnh cỡ batch (ADR-002). Lỗi dồn CUỐI batch → batch
đang quá dài, cắt nhỏ lại. Nhiều batch bé pass sạch liên tục → gộp to hơn được.

| date | slug | batch | tasks | files | fails | vị trí fail | loại lỗi | note |
|------|------|-------|-------|-------|-------|------------|----------|------|
| 2026-11-08 | f003-mouse-gesture-tab-control | 1/1 | 9 | 9 | 0 | - | - | full re-run (batch cuối + HOT files config_service.py/mouse_mapper_logic.py); đúng cả phần review tay (inject_right_up chỉ gọi trong GESTURE+matched, không đụng SCROLLING — tránh lặp lại bug lịch sử v2.0.0) |
| 2026-11-08 | f004-gesture-fix-settings-merge | 1/1 | 10 | 10 | 0 | - | - | full re-run; code review tay khớp 100% ADR-003. LƯU Ý: batch "manual-test" field của T-017 chỉ là Antigravity diễn giải lại code, KHÔNG phải quan sát runtime thật — verify-cmd/unit-test không bắt được bug context-menu cấp OS (đã xảy ra đúng ở F-003 dù validate PASS lúc đó); test thị giác thật vẫn cần user làm tay sau khi build. |
