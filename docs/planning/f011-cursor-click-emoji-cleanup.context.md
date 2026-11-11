## Elicitation — 2026-11-11

Problem: Cửa sổ Shortcut Panel bị căn giữa dọc đẩy lên đỉnh màn hình cách xa con trỏ chuột; nút chuột trái (left click) bị vô hiệu hóa do z-order backdrop che khuất cửa sổ chính; menu và cửa sổ cài đặt còn chứa các emoticon gây rườm rà.
Goal: Cửa sổ mở ngay tại tọa độ chuột, khắc phục triệt để lỗi click chuột trái qua việc ép `self._win.lift(self._overlay)`, và loại bỏ toàn bộ emoticon khỏi menu và cửa sổ cài đặt.
Scope IN:
- Sửa thuật toán `_position()` trong `panel_window.py` mở trực tiếp tại `(px, py)`.
- Ép z-order `self._win.lift(self._overlay)` trong `panel_window.py`.
- Xóa bỏ icon emoji trong `panel_item_renderer.py`, `panel_volume_widget.py`, `settings_window.py`.
- Lọc bỏ emoji khỏi nhãn item tự động và trong default presets `config_service.py`.
Scope OUT:
- Không thay đổi logic RMB mouse hook và các phím điều hướng bàn phím.
- Không thay đổi backend volume Core Audio.
Stories:
- US-031: Cửa sổ shortcut mở chính xác tại vị trí con trỏ chuột khi kích hoạt.
- US-032: Chuột trái hoạt động hoàn hảo để click chọn shortcut và kéo slider âm lượng.
- US-033: Toàn bộ menu và cửa sổ cài đặt không còn emoticon, sạch sẽ và tối giản.

---

## PRD — 2026-11-11

Path: docs/prd/f011-cursor-click-emoji-cleanup.md
Version: 1.0
Summary: Đặc tả sửa lỗi vị trí con trỏ, z-order chuột trái và dọn dẹp emoticon.

---

## Architecture — 2026-11-11

Pattern: Z-Order Stacking & Clean Typography
ADR-010: Z-Order Lifting and Clean Typographic Layout → docs/adr/ADR-010-cursor-position-zorder-clean-ui.md

---

## Tasks — 2026-11-11

Total: 4 tasks in docs/planning/f011-cursor-click-emoji-cleanup.tasks.md

---

## Verify record — 2026-11-11 (Claude)

task: T-059..T-062 (code thực tế đã khớp spec dù tasks.md chưa tick — có lẽ thực thi qua kênh khác không ghi report chuẩn)
risk: MEDIUM
checks: 8/8 PASS (xem docs/map/pending-verify.md đã tick đủ kèm bằng chứng lệnh thật)
tests: py_compile PASS, PyInstaller build PASS, emoji scan 0 hits
contracts: panel_window.py/panel_item_renderer.py/panel_volume_widget.py/settings_window.py/config_service.py không đổi contract ra ngoài (fan-in giữ nguyên)
result: PASS — /verify-done chạy tay, pending-verify.md đã chuyển status: verified
