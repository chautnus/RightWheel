# Tasks: Modern Minimalist UI & Volume Fronting (f007-modern-ui-volume-front)

Total: 6 tasks | Estimate: 4h | Status: 6/6 Done

## Tasks List

### Batch 1: Core Config & Volume Components
- [x] **TSK-036**: Cập nhật `config_service.py` hỗ trợ `volume_step`, `show_panel_volume` và đưa action `show_volume_slider` ra root `_DEFAULT` (US-023, US-020).
- [x] **TSK-037**: Nâng cấp `volume_overlay.py` thành Capsule HUD hiện đại, icon loa động theo mức âm lượng, nhãn %, bo cong Canvas (US-021).
- [x] **TSK-038**: Nâng cấp `panel_window.py` tích hợp Quick Volume Widget trên đỉnh panel và styling items dạng modern dark minimalist (US-020).

### Batch 2: Modern Settings UI & Verification
- [x] **TSK-039**: Tạo mới `general_volume_tab.py` cho cấu hình General & Volume (US-023).
- [x] **TSK-040**: Tái cấu trúc `settings_window.py` sang giao diện Modern Sidebar Navigation 2 cột (US-022).
- [x] **TSK-041**: Chạy kiểm tra tĩnh syntax (py_compile), kiểm tra giới hạn dòng ≤ 250 dòng cho toàn bộ file, release-validation (US-020..US-023).
