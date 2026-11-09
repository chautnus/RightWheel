---
id: prd_f006-shortcut-reference-volume-control_20261109
title: "Shortcut Reference List + Volume Control via Scroll (F-006)"
status: draft
version: 1.0
author: Antigravity / Claude
created: 2026-11-09
updated: 2026-11-09
tags: [shortcut-panel, settings, reference-guide, volume-control, mouse-wheel, overlay, sendinput]
summary: "Bổ sung tab tra cứu các tổ hợp phím tắt Windows phổ biến trong Settings và cung cấp Action 'show_volume_slider' hiển thị HUD điều khiển âm lượng hệ thống bằng cuộn chuột, tự ẩn sau 3 giây hoặc click ngoài."
---

# PRD: Shortcut Reference List + Volume Control via Scroll (F-006)

## 1. Overview
**Problem**: (1) User cấu hình shortcut panel thường không nhớ hết tổ hợp phím Windows hữu ích. (2) User muốn điều chỉnh nhanh volume hệ thống hoàn toàn bằng chuột.

**Solution**: (1) Tab tĩnh "Reference" trong SettingsWindow liệt kê tổ hợp phím Windows + mô tả tiếng Anh/song ngữ. (2) Action type mới `show_volume_slider` mở HUD `VolumeOverlay` (Toplevel bán trong suốt), cuộn chuột gửi `VK_VOLUME_UP`(0xAF)/`VK_VOLUME_DOWN`(0xAE) qua `SendInput`, slider bắt đầu 50% neutral, tự đóng sau 3s/ESC/click-ngoài.

**Success Metrics**: User tra cứu được ≥20 shortcut ngay trong Settings; cuộn chuột đổi volume hệ thống thật với độ trễ thấp; 0 dependency mới; không ảnh hưởng gesture engine/action cũ.

## 2. Background & Context
RightWheel đã có kiến trúc panel phím tắt (F-002), gesture engine (F-003..F-005), settings tabbed UI. F-006 mở rộng thành trung tâm tiện ích chuột mà không đụng tới state machine LOCKED, tận dụng SendInput + overlay pattern đã kiểm chứng.

## 3. Jobs To Be Done (JTBD)
> **When** tôi cấu hình phím tắt hoặc muốn tăng/giảm volume tức thì, **I want to** có bảng tham khảo phím tắt Windows và 1 slider volume điều khiển bằng cuộn chuột, **so I can** thao tác nhanh mà không rời tay khỏi chuột.

## 4. Stakeholders
| Role | Name | Responsibility |
|---|---|---|
| Product Owner | User/Claude | Phê duyệt PRD |
| Tech Lead | Claude/Antigravity | Kiến trúc |
| Developer | Antigravity | Triển khai |
| Tester | User | Test tay trên Windows |

## 5. User Stories & Acceptance Criteria

### US-017: Tab tra cứu phím tắt Windows trong Settings
**As a** user cấu hình RightWheel, **I want to** xem danh sách tổ hợp phím Windows thông dụng trong 1 tab Settings, **So that** tự ghép phím tắt đúng mà không cần tra web.
**Acceptance Criteria:**
- [ ] Given SettingsWindow mở, When chuyển tab "Reference", Then hiện bảng tĩnh read-only ≥20 tổ hợp phím (cột Category/Shortcut/Description).
- [ ] Bảng hỗ trợ cuộn khi nội dung vượt chiều cao cửa sổ.
- [ ] Dữ liệu read-only, không chỉnh sửa trực tiếp.

### US-018: Action "show_volume_slider" trong Panel Logic & Config
**As a** user tùy biến Shortcut Panel, **I want to** gán 1 mục Action "show_volume_slider", **So that** chọn mục này kích hoạt điều khiển volume.
**Acceptance Criteria:**
- [ ] `ActionItem.action` hỗ trợ `"show_volume_slider"`.
- [ ] Chọn mục này trên panel → panel ẩn, gọi callback `on_show_volume_slider()`.
- [ ] `_DEFAULT` có sẵn mẫu `{"type":"action","label":"🔊 Volume Control","action":"show_volume_slider"}`.
- [ ] Không phá schema `shortcuts.json` hiện có.

### US-019: VolumeOverlay — điều khiển volume bằng cuộn chuột
**As a** user sau khi kích hoạt action volume, **I want to** 1 HUD hiện tại vị trí con trỏ, cuộn để chỉnh volume, **So that** điều khiển trực quan và tự biến mất khi xong.
**Acceptance Criteria:**
- [ ] HUD hiện tại vị trí con trỏ chuột (không phải giữa màn hình), always-on-top, không có WS_EX_NOACTIVATE (cần nhận focus).
- [ ] Slider bắt đầu 50% neutral, KHÔNG hiện % label.
- [ ] Cuộn lên → gửi VK_VOLUME_UP; cuộn xuống → gửi VK_VOLUME_DOWN qua SendInput; mỗi lần cuộn reset timer tự ẩn.
- [ ] Không tương tác 3s → tự ẩn. ESC hoặc click ngoài → ẩn ngay.
- [ ] Chạy an toàn trên Tkinter thread hiện có (queue pump qua PanelWindow).

## 6. Functional Requirements
| ID | Requirement | Priority | Story |
|----|-------------|----------|-------|
| FR-001 | ReferenceTab(tk.Frame) mới, ttk.Treeview 3 cột, ≥20 dòng tĩnh | Must Have | US-017 |
| FR-002 | `_build_reference_tab` tích hợp settings_window.py sau tab Gestures | Must Have | US-017 |
| FR-003 | `ActionItem.action` docstring thêm "show_volume_slider" | Must Have | US-018 |
| FR-004 | `panel_logic.py`: callback `on_show_volume_slider` + nhánh `_handle_action` | Must Have | US-018 |
| FR-005 | `config_service._DEFAULT` thêm mẫu Volume Control trong 📁 App | Should Have | US-018 |
| FR-006 | `shortcut_executor.py`: `VK_VOLUME_*` + `send_volume_step(delta)` qua SendInput | Must Have | US-019 |
| FR-007 | `volume_overlay.py` mới: 2 Toplevel (backdrop+slider), định vị qua `winfo_pointerx/y()`, Rule 4b order | Must Have | US-019 |
| FR-008 | Timer tự ẩn 3000ms (root.after/after_cancel), ESC + click-outside dismiss | Must Have | US-019 |
| FR-009 | Wiring `panel_window.py` (queue "volume" + `_do_volume`) + `main.py` | Must Have | US-018, US-019 |

## 7. Non-Functional Requirements
| Category | Requirement | Metric |
|---|---|---|
| Zero Dependency | Không pycaw/comtypes | 0 dependency mới |
| Isolation | Không đụng mouse_mapper_logic.py/gesture engine LOCKED | 0 thay đổi file đó |
| Thread Safety | Mọi Tkinter call qua queue pump/root.after | Không treo Tcl interpreter |
| Compatibility | Schema shortcuts.json, action open_settings/toggle_pause giữ nguyên | Không đổi |
| Manual Verification | Hành vi UI/timer/vị trí HUD cần test tay | Báo cáo test tay 100% |

## 8. Out of Scope
- Windows Core Audio/pycaw. Tích hợp vào gesture engine RMB. Auto-fill form từ danh sách tham khảo. Hiện % label trên slider.

## 9. Dependencies
- `ctypes.windll.user32.SendInput`, `tkinter`/`ttk` chuẩn. Module hiện có: `panel_logic.py`, `panel_types.py`, `panel_window.py`, `config_service.py`, `shortcut_executor.py`.

## 10. Definition of Done
- [ ] US-017..US-019 AC pass. Tab Reference hiển thị đủ, cuộn mượt. Action volume hoạt động từ panel. Cuộn chuột đổi volume thật, slider phản hồi đúng chiều. Tự ẩn đúng theo 3 cơ chế. Không crash thread. Không file nào vượt 250 dòng.

## 11. Timeline
| Milestone | Date | Notes |
|---|---|---|
| PRD+ADR | 2026-11-09 | Done |
| Implementation | 2026-11-09 | Batch 1 (6 task) |
| Test tay + release | 2026-11-09 | v2.15.0 |

## 12. Open Questions
- Không có (đã chốt hết ở elicitation/PRD review: vị trí HUD theo con trỏ, không hiện %).

## 13. Changelog
| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-11-09 | Antigravity/Claude | Initial draft |
