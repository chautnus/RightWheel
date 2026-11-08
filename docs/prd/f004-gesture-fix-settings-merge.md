---
id: prd_f004-gesture-fix-settings-merge_20261108
title: "Fix + hoàn thiện Mouse Gesture Engine (F-004)"
status: draft
version: 1.0
author: Antigravity / Claude
created: 2026-11-08
updated: 2026-11-08
tags: [mouse-mapper, gesture-engine, settings-merge, bug-fix, trail-overlay]
summary: "Sửa 3 lỗi cốt lõi của Mouse Gesture Engine (F-003), bổ sung đường vẽ trực quan (trail line) và gộp cài đặt vào SettingsWindow."
---

# PRD: Fix + hoàn thiện Mouse Gesture Engine (F-004)

## 1. Overview
**Problem**: Mouse Gesture Engine (F-003) không hoạt động ổn định do 3 lỗi cộng hưởng: (1) double-click vô tình tắt preset trong GestureSettingsDialog; (2) GestureRecognizer sinh hướng chéo giả "DR" ở góc cua (Anchor Residual Vector Addition, >60% trường hợp kể cả góc vuông hoàn hảo); (3) inject_right_down()+inject_right_up() tạo thành click phải hoàn chỉnh, kích hoạt WM_CONTEXTMENU, nuốt mất Ctrl+W. Thiếu phản hồi trực quan khi vẽ, UI phân tán ngoài tray.

**Solution**: Bỏ binding double-click toggle; thêm normalize_directions() chuẩn hoá hướng chéo dư; loại bỏ hoàn toàn inject_right_down() sớm trong _on_move() và inject_right_up() khi matched (Silent Drop khi không khớp) — chấp nhận mất khả năng RMB-drag gốc của mọi app trong lúc gesture active; thêm Trail Line Overlay (Tkinter transparent Toplevel + polling GetCursorPos); gộp GestureSettingsDialog thành tab "Gestures" thứ 4 trong SettingsWindow.

**Success Metrics**: 100% cử chỉ góc vuông (Down→Right) khớp preset; 100% Ctrl+W thực thi không bị context menu chen; 0% tắt nhầm preset do double-click; trail overlay <2ms overhead; settings tập trung 1 cửa sổ.

## 2. Background & Context
F-003 xây nền tảng gesture 8-hướng nhưng debug1+debug2 (docs/debug/gesture-no-trigger.debug1.md, .debug2.md) xác nhận 3 lỗi cộng hưởng qua thực nghiệm trực tiếp trên máy dev. F-004 sửa triệt để, đồng thời hoàn thiện UX.

## 3. Jobs To Be Done (JTBD)
> **When** tôi lướt web và muốn đóng tab bằng cách giữ RMB kéo Down→Right, **I want to** cử chỉ nhận diện chính xác, thấy vệt vẽ trực quan, tab đóng ngay không bị menu chen, **so I can** thao tác thuần chuột đáng tin cậy.

## 4. Stakeholders
| Role | Name/Team | Responsibility |
|------|-----------|----------------|
| Product Owner | User / Claude | Phê duyệt PRD |
| Tech Lead | Antigravity / Claude | Kiến trúc |
| Dev | Antigravity Subagent | Triển khai |

## 5. User Stories & Acceptance Criteria

### US-007: Fix UX toggle nguy hiểm trong danh sách cử chỉ
**As a** người dùng cấu hình RightWheel, **I want to** danh sách cử chỉ không tự đảo trạng thái khi double-click, hiển thị rõ trạng thái, **So that** không vô tình tắt nhầm.
**Acceptance Criteria:**
- [ ] Given tab Gestures, When double-click vào mục, Then trạng thái KHÔNG đổi (chỉ chọn dòng).
- [ ] Given danh sách, When hiển thị, Then mỗi dòng thể hiện rõ [Bật]/[Tắt].
- [ ] Given mục được chọn, When bấm nút "Bật/Tắt", Then đảo trạng thái, lưu ngay, giữ nguyên selection.

### US-008: Fix thuật toán nhận diện hướng — chuẩn hoá nét chéo dư
**As a** người dùng vẽ Down→Right, **I want to** hệ thống lọc hướng chéo dư ở góc cua, **So that** khớp đúng preset ["D","R"].
**Acceptance Criteria:**
- [ ] Given chuỗi [..., A, diag(A,B), B, ...] cho 8 cặp trực giao, When normalize_directions() chạy, Then gộp thành [..., A, B, ...].
- [ ] Given preset chéo có chủ đích (["DR"], ["D","DR"], ["DR","R"], ["UR","DL"]), When normalize chạy, Then GIỮ NGUYÊN không bị nuốt.
- [ ] Given nhiều khúc cua liên tiếp (["U","UR","R","DR","D"]), When normalize chạy, Then ra ["U","R","D"].

### US-009: Fix xung đột context menu khi gesture khớp preset
**As a** người dùng vẽ gesture đóng tab, **I want to** Ctrl+W gửi thẳng không bị context menu chen, **So that** tab đóng ngay lập tức.
**Acceptance Criteria:**
- [ ] Given state GESTURE, When right_up và khớp preset, Then execute(keys) trực tiếp, KHÔNG inject_right_down/up, KHÔNG context menu.
- [ ] Given state GESTURE, When right_up KHÔNG khớp preset nào, Then Silent Drop — không gửi gì, không context menu.
- [ ] Given click phải tại chỗ (không vượt move_threshold), When thả RMB, Then context menu vẫn xuất hiện bình thường (bảo toàn 100%).
- [ ] Given 2 mode scroll SCROLLING (panel/Alt+Tab), When kích hoạt, Then hoàn toàn không đổi.

### US-010: Trail line overlay theo chuột khi vẽ gesture
**As a** người dùng vẽ gesture, **I want to** thấy vệt vẽ theo con trỏ, **So that** biết mình đang vẽ gì.
**Acceptance Criteria:**
- [ ] Given state GESTURE, When di chuyển, Then overlay trong suốt topmost vẽ line nối điểm.
- [ ] Given thả RMB, When kết thúc, Then overlay biến mất ngay lập tức (không fade).
- [ ] Given tần suất move cao, When vẽ, Then không giật lag, <2ms overhead, không sửa mouse_hook_service.py.

### US-011: Gộp Gestures vào tab thứ 4 settings_window.py, bỏ tray menu riêng
**As a** người dùng, **I want to** quản lý gesture trong cùng cửa sổ Settings, **So that** gọn gàng tập trung.
**Acceptance Criteria:**
- [ ] Given SettingsWindow, When mở, Then có 4 tab: Default/Profiles/Gestures/License.
- [ ] Given tab Gestures, When tương tác, Then đủ chức năng xem/thêm/bật-tắt/xoá, đồng bộ shortcuts.json.
- [ ] Given mã nguồn, When cài đặt, Then logic nằm ở gestures_tab.py riêng.
- [ ] Given tray menu, When mở, Then không còn mục "Cử chỉ chuột" riêng.
- [ ] Given main.py, When khởi động, Then không còn import/wiring open_gestures cũ.

## 6. Functional Requirements
| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-001 | Bỏ `<Double-Button-1>` toggle trong gesture list | Must Have | US-007 |
| FR-002 | Hiển thị trạng thái [Bật]/[Tắt] rõ ràng | Must Have | US-007 |
| FR-003 | `normalize_directions(dirs)` pure function, 8 luật pattern-collapse trực giao | Must Have | US-008 |
| FR-004 | Tích hợp normalize vào `GestureRecognizer.finish()` | Must Have | US-008 |
| FR-005 | Bỏ `inject_right_down()` trong `_on_move()` khi vào GESTURE | Must Have | US-009 |
| FR-006 | `_on_right_up()` GESTURE matched: execute() trực tiếp, không inject_right_up() | Must Have | US-009 |
| FR-007 | `_on_right_up()` GESTURE không matched: Silent Drop hoàn toàn | Must Have | US-009 |
| FR-008 | `TrailOverlay` module mới, Toplevel trong suốt + polling GetCursorPos | Must Have | US-010 |
| FR-009 | `on_gesture_start`/`on_gesture_end` callback read-only trên MouseMapperLogic | Must Have | US-010 |
| FR-010 | `GesturesTab(tk.Frame)` file riêng, tích hợp tab 4 settings_window.py | Must Have | US-011 |
| FR-011 | Xoá gesture_settings_dialog.py, dọn tray_ui.py/main.py | Must Have | US-011 |
| FR-012 | Auto-restore enabled:true cho preset ["D","R"] trong config_service.load() | Should Have | Bonus |

## 7. Non-Functional Requirements
| Category | Requirement | Metric |
|----------|-------------|--------|
| Performance | normalize + trail overlay không chậm thao tác chuột | <2ms/move event |
| Reliability | Context-menu triệt tiêu 100% trên Windows/Chromium | 0 lần xuất hiện sai |
| Compatibility | Schema shortcuts.json, switch_tab()/switch_tab_x1x2()/execute() signature giữ nguyên | Không đổi |
| Maintainability | File giới hạn dòng | gestures_tab.py/trail_overlay.py ≤150 dòng; settings_window.py <165 dòng |

## 8. Out of Scope
- Đổi schema shortcuts.json; đổi preset mặc định; đổi X1/X2; fade animation cho trail; giữ lại RMB-drag gốc cho app khác (Edge/Photoshop/Explorer...) — đã chấp nhận trade-off.

## 9. Dependencies
- gesture_recognizer.py, mouse_mapper_logic.py, hotkey_service.py, mouse_hook_service.py (không sửa), settings_window.py, gestures_tab.py (mới), trail_overlay.py (mới), tray_ui.py, main.py, config_service.py.

## 10. Definition of Done
- [ ] US-007..US-011 Acceptance Criteria pass.
- [ ] Vẽ Down→Right (tự nhiên lẫn vuông góc) khớp preset, đóng tab, không context menu.
- [ ] Double-click không đổi trạng thái.
- [ ] Trail overlay mượt, biến mất ngay khi thả RMB.
- [ ] SettingsWindow 4 tab, tray không còn mục riêng, main.py sạch.
- [ ] Preset cũ trong shortcuts.json bảo toàn.
- [ ] Không file nào vượt 250 dòng.

## 11. Timeline
| Milestone | Date | Notes |
|-----------|------|-------|
| PRD+ADR | 2026-11-08 | Done |
| Implementation | 2026-11-08 | Batch 1 (10 task) |
| Validate + release | 2026-11-08/09 | v2.14.1 |

## 12. Open Questions
- Không có (đã chốt hết ở elicitation/PRD/ADR review).

## 13. Changelog
| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-11-08 | Antigravity/Claude | Initial draft, rà soát + chốt trade-off RMB-drag |
