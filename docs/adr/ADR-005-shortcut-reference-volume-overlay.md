---
id: ADR-005
title: "Kiến trúc ReferenceTab và VolumeOverlay qua SendInput (F-006)"
status: accepted
date: 2026-11-09
tags: [shortcut-panel, volume-control, reference-tab, send-input, tkinter-overlay, f006]
summary: "ReferenceTab tĩnh 3 cột trong SettingsWindow; VolumeOverlay dùng Tkinter native <MouseWheel> binding + transparent backdrop (không route qua mouse_hook_service.py LOCKED), định vị qua winfo_pointerx/y() có sẵn, gửi VK_VOLUME_UP/DOWN qua SendInput — không pycaw."
---

## Context
User cần tab tham khảo phím tắt Windows trong Settings và 1 cách điều khiển volume bằng cuộn chuột qua HUD nổi ngắn hạn, kích hoạt từ action panel. Phải không ảnh hưởng gesture engine LOCKED, không thêm dependency ngoài.

## Decision
1. **US-017**: `ReferenceTab(tk.Frame)` — `ttk.Treeview` 3 cột (category/shortcut/description), ≥20 dòng tĩnh, tích hợp `_build_reference_tab` trong `settings_window.py` sau tab Gestures.
2. **US-018**: `ActionItem.action` thêm `"show_volume_slider"`. `panel_logic.py` thêm callback `on_show_volume_slider` + nhánh `_handle_action`. `config_service._DEFAULT` thêm mẫu trong 📁 App.
3. **US-019 — Đảo giả định đã xét**: Route scroll qua `mouse_hook_service.py` (vi phạm LOCKED, rủi ro hook timeout) BỊ TỪ CHỐI. Chọn Tkinter native `<MouseWheel>` binding + transparent fullscreen backdrop (tái dùng nguyên pattern `PanelWindow._do_show`). `VolumeOverlay` định vị theo con trỏ qua `root.winfo_pointerx()/winfo_pointery()` (đã có sẵn, dùng trong `panel_window.py:174-175`) — KHÔNG dùng `ctypes.GetCursorPos`. KHÔNG set `WS_EX_NOACTIVATE` (khác `TrailOverlay` passive — đây là UI tương tác cần focus để nhận scroll/ESC). Tuân thủ Rule 4b: `_render() → lift() → focus_force() → _position()`.
4. **Gửi phím volume**: `shortcut_executor.py` thêm `VK_VOLUME_MUTE/DOWN/UP` + `send_volume_step(delta)` qua `SendInput` (tái dùng `_INPUT` struct có sẵn), cờ `KEYEVENTF_EXTENDEDKEY`.
5. **Dismiss**: timer `root.after(3000, hide)` reset mỗi lần scroll qua `after_cancel`; `<Escape>` + backdrop `<ButtonPress>` → `hide()` ngay.

## Rationale
- Tkinter native binding tận dụng tối đa pattern đã kiểm chứng (`PanelWindow`), triệt tiêu rủi ro đụng LOCKED/hook timeout.
- `winfo_pointerx/y()` đã có sẵn, đơn giản hơn ctypes — review Claude phát hiện và sửa so với draft ban đầu của Antigravity.
- Phân biệt rõ passive overlay (TrailOverlay, cần NOACTIVATE) vs interactive overlay (VolumeOverlay, cần focus) — tránh nhầm lẫn áp dụng sai pattern.

## Options Considered
| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Tkinter `<MouseWheel>` binding + backdrop | An toàn, tái dùng pattern có sẵn, không đụng LOCKED | Chỉ bắt scroll khi overlay có focus/hiển thị | ✅ Chosen |
| Route qua mouse_hook_service.py | Bắt scroll toàn màn hình | Vi phạm LOCKED, rủi ro hook timeout, cần liên luồng phức tạp | ❌ Rejected |
| pycaw/Core Audio | Đọc/set % thật | Thêm dependency nặng, COM phức tạp | ❌ Rejected (PRD) |

## Consequences
**Positive**: Cô lập hoàn toàn khỏi gesture engine; mã nguồn đơn giản, dễ bảo trì; tận dụng pattern có sẵn.
**Trade-offs**: Volume hiển thị tương đối (không đọc % thật OS).
**Risks**: Hành vi UI/timer/vị trí cần test tay (không thể unit-test đầy đủ hành vi OS-level).
