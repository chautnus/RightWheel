# Antigravity Calibration — thống kê chất lượng thực thi per batch
Mục đích: plan-tasks đọc để chỉnh cỡ batch (ADR-002). Lỗi dồn CUỐI batch → batch
đang quá dài, cắt nhỏ lại. Nhiều batch bé pass sạch liên tục → gộp to hơn được.

| date | slug | batch | tasks | files | fails | vị trí fail | loại lỗi | note |
|------|------|-------|-------|-------|-------|------------|----------|------|
| 2026-11-08 | f003-mouse-gesture-tab-control | 1/1 | 9 | 9 | 0 | - | - | full re-run (batch cuối + HOT files config_service.py/mouse_mapper_logic.py); đúng cả phần review tay (inject_right_up chỉ gọi trong GESTURE+matched, không đụng SCROLLING — tránh lặp lại bug lịch sử v2.0.0) |
