# F-013 — Architecture notes (ADR-011)

Nguồn phân tích: Antigravity (ag-plan), Claude rà soát — 2026-11-11.

- Nguyên nhân flicker/lag khi scroll panel: `_render()` cũ `winfo_children().destroy()` toàn bộ + tạo lại `PanelVolumeWidget` (2 lệnh COM Core Audio đồng bộ) MỖI LẦN `navigate()`. Fix: `PanelWindow` lưu snapshot (`_last_items`/`_last_breadcrumb`/`_last_profile`/`_last_paused`/`_last_index`), chỉ full `_render()` khi cấu trúc thật sự đổi; đổi index chỉ gọi `PanelItemRenderer.update_selection(old_idx,new_idx)` — restyle 2 hàng qua widget reference lưu trong `_row_views`, không destroy/recreate gì. Có test hồi quy `tests/test_render_flicker.py`.
- Xóa sạch 100% Volume subsystem: 3 file xóa (`volume_service.py`/`panel_volume_widget.py`/`volume_overlay.py`), `general_volume_tab.py`→`general_tab.py` (`GeneralVolumeTab`→`GeneralTab`, chỉ giữ Startup+Language), dọn 12 file source + 9 i18n + dead code `send_volume_step`/`VK_VOLUME_*` + config thật user.
- Fan-in thấp (ReferenceTab/GeneralTab chỉ dùng trong settings_window.py) — không có contract ngoài bị ảnh hưởng.
