# F-006 — Architecture notes (ADR-005)

Nguồn phân tích: Antigravity (ag-plan), Claude rà soát — 2026-11-09

- Đảo giả định quan trọng: route volume-scroll qua mouse_hook_service.py bị từ chối (vi phạm LOCKED + rủi ro hook timeout) — chọn Tkinter native <MouseWheel> binding + transparent backdrop, tái dùng nguyên pattern PanelWindow._do_show.
- Phân biệt rõ: TrailOverlay (passive, cần WS_EX_NOACTIVATE) vs VolumeOverlay (interactive, cần focus, KHÔNG NOACTIVATE) — áp dụng đúng bài học kiến trúc overlay từ F-005.
- winfo_pointerx()/winfo_pointery() thuần Tkinter đã có sẵn trong panel_window.py — ưu tiên dùng lại thay vì thêm ctypes mới không cần thiết.
