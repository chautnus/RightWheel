---
id: prd_f003-mouse-gesture-tab-control_20261108
title: "Mouse-only tab switch + gesture engine (F-003)"
status: draft
version: 1.0
author: Antigravity / Claude
created: 2026-11-08
updated: 2026-11-08
tags: [mouse-mapper, gesture, tab-control, chromium, xbutton]
summary: "Điều khiển chuyển và đóng tab thuần chuột bằng nút phụ X1/X2 và nhận diện cử chỉ vẽ chuột 8 hướng khi giữ chuột phải (RMB) trên trình duyệt Chromium."
---

# PRD: Mouse-only tab switch + gesture engine (F-003)

## 1. Overview
**Problem**: Chuyển tab / đóng tab trong các trình duyệt Chromium (Chrome, Edge, Brave, Opera, Vivaldi) hiện tại bắt buộc phải dùng Shift+Scroll (F-001) hoặc rời tay sang bàn phím (Ctrl+Tab, Ctrl+W). Người dùng không thể thao tác thuần chuột bằng một tay khi đang giữ nút chuột phải (RMB).

**Solution**: Bổ sung 2 cơ chế tương tác thuần chuột khi người dùng đang giữ nút chuột phải (RMB):
1. Nhấn nút chuột phụ X1 (Back) để chuyển về tab trước (`Ctrl+Shift+Tab`) và X2 (Forward) để chuyển sang tab kế tiếp (`Ctrl+Tab`) trên cửa sổ Chromium đang active.
2. Vẽ cử chỉ chuột (chuỗi nét định hướng 8 hướng liên tiếp) khi giữ RMB để kích hoạt phím tắt tùy chỉnh (mặc định: nét Kéo Xuống → Sang Phải `["D", "R"]` = `Ctrl+W` đóng tab). Nếu cử chỉ không khớp preset nào, tự động fallback trả lại sự kiện chuột cho trình duyệt (Edge/extension) xử lý.

**Success Metrics**:
- X1/X2 chuyển đúng tab trước/sau trên 100% trình duyệt Chromium hỗ trợ.
- Gesture nhận diện chính xác 8 hướng; mặc định Down→Right đóng đúng tab hiện tại.
- Không phá vỡ 2 mode cuộn RMB+Scroll đã lock, không phá Shift+Scroll (F-001), không phá Back/Forward gốc của X1/X2 khi KHÔNG giữ RMB.

## 2. Background & Context
RightWheel hiện hỗ trợ mở shortcut panel (RMB+Scroll UP) và Alt+Tab switcher (RMB+Scroll DOWN), cùng Shift+Scroll chuyển tab (F-001). Power user dùng chuột gaming có X1/X2 muốn chuyển tab cực nhanh không cần chạm bàn phím. Mouse gesture đóng tab là thói quen phổ biến từ Edge/extension — tích hợp vào RMB session tạo trải nghiệm đồng nhất.

## 3. Jobs To Be Done (JTBD)
> **When** đang lướt web trên nhiều tab Chromium bằng tay giữ chuột, **I want to** chuyển tab bằng X1/X2 và vẽ cử chỉ để đóng tab/chạy shortcut mà không rời tay sang bàn phím, **so I can** duy trì nhịp làm việc liên tục.

## 4. Stakeholders
| Role | Name/Team | Responsibility |
|------|-----------|----------------|
| Product Owner | User / Claude | Phê duyệt PRD |
| Tech Lead | Antigravity / Claude | Kiến trúc kỹ thuật |
| Dev | Antigravity Subagent | Triển khai + test |

## 5. User Stories & Acceptance Criteria

### US-003: Chuyển tab trước/sau bằng nút phụ X1/X2 khi đang giữ RMB
**As a** power user có chuột X1/X2, **I want to** giữ RMB và nhấn X1/X2, **So that** chuyển tab nhanh không rời tay khỏi chuột.
**Acceptance Criteria:**
- [ ] Given Chromium foreground + giữ RMB, When nhấn X1, Then Ctrl+Shift+Tab (previous), nuốt event.
- [ ] Given Chromium foreground + giữ RMB, When nhấn X2, Then Ctrl+Tab (next), nuốt event.
- [ ] Given KHÔNG giữ RMB (IDLE), When nhấn X1/X2 (app nào cũng vậy), Then pass-through nguyên vẹn (Back/Forward gốc).
- [ ] Given đang giữ RMB nhưng app foreground KHÔNG phải Chromium, When nhấn X1/X2, Then LUÔN suppress (không pass-through dù không phải Chromium) — không gửi shortcut, không crash.

### US-004: Nhận diện cử chỉ chuột 8 hướng khi giữ RMB và thực thi phím tắt
**As a** người dùng, **I want to** vẽ chuỗi nét 8 hướng khi giữ RMB, **So that** thực thi phím tắt tương ứng (mặc định Down→Right = Ctrl+W).
**Acceptance Criteria:**
- [ ] Given giữ RMB + di chuyển Down rồi Right vượt ngưỡng, When thả RMB, Then nhận diện ["D","R"], inject_right_up() hủy ngược, execute("ctrl+w"), suppress right_up thật.
- [ ] Given 8 hướng U/D/L/R/UR/DR/DL/UL, ngưỡng nét tối thiểu 15-20px, nén nét lặp liên tiếp.
- [ ] Given đang vẽ, WM_MOUSEMOVE xử lý <1ms, không block hook >300ms.

### US-005: Fallback pass-through khi cử chỉ không khớp preset
**As a** người dùng dùng Edge native gesture/extension, **I want to** cử chỉ không khớp preset nào vẫn pass-through cho trình duyệt, **So that** không mất tính năng gesture ngoài.
**Acceptance Criteria:**
- [ ] Given cử chỉ không khớp preset nào, When thả RMB, Then right_down đã inject sớm vẫn còn hiệu lực, right_up thật đi qua bình thường (không đổi hành vi hiện tại).
- [ ] Given chỉ click nhẹ (không vượt move_threshold), When thả RMB, Then context menu hiện bình thường.
- [ ] Given cuộn chuột trong phiên RMB, Then lock vào SCROLLING (panel/Alt+Tab), bỏ qua gesture logic.

### US-006: Giao diện cấu hình riêng cho Gesture Presets
**As a** người dùng, **I want to** UI riêng xem/thêm/sửa/bật/tắt/xoá preset gesture→shortcut, **So that** cá nhân hoá cử chỉ.
**Acceptance Criteria:**
- [ ] Given mở Settings/Tray, When chọn quản lý gesture, Then `GestureSettingsDialog` độc lập hiện ra, liệt kê preset + phím tắt + trạng thái.
- [ ] Given dialog, When thêm/sửa preset, Then lưu vào shortcuts.json qua config_service.
- [ ] Given settings_window.py đang 149/150 dòng, When triển khai UI gesture, Then KHÔNG thêm dòng vào file này — toàn bộ nằm trong gesture_settings_dialog.py riêng.

## 6. Functional Requirements
| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-001 | WM_XBUTTONDOWN (0x020B) trong mouse_hook_service._hook_proc, trích X1/X2 từ HIWORD(mouseData) | Must Have | |
| FR-002 | Gate Chromium cho HÀNH ĐỘNG chuyển tab; SUPPRESS X1/X2 ở MỌI app khi giữ RMB (không chỉ Chromium) | Must Have | OQ-3 |
| FR-003 | Hàm riêng `switch_tab_x1x2(forward)` trong hotkey_service.py, KHÔNG sửa switch_tab() gốc | Must Have | OQ-1 |
| FR-004 | Suppress X1/X2 khi đã xử lý | Must Have | |
| FR-005 | Bảo toàn X1/X2 khi KHÔNG giữ RMB (pass-through) | Must Have | |
| FR-006 | mouse_mapper_logic.py: track toạ độ trong RIGHT_HELD/GESTURE qua GestureRecognizer, fix wants_moves() | Must Have | LOCKED Behavior #1 đã duyệt đổi |
| FR-007 | GestureRecognizer 8-hướng, ngưỡng 15-20px, nén nét lặp | Must Have | |
| FR-008 | Khớp preset → shortcut_executor.execute(keys), mặc định ["D","R"]→"ctrl+w" | Must Have | |
| FR-009 | Fallback: không khớp → giữ hành vi GESTURE hiện tại (pass-through) | Must Have | US-005 |
| FR-010 | config_service.py version 2→3, thêm "gestures", migrate_to_v3() 2 chiều | Must Have | |
| FR-011 | GestureSettingsDialog file riêng, không đụng settings_window.py | Should Have | OQ-4 |
| FR-012 | Cơ chế "hủy ngược": inject_right_up() tagged INJECTED_MARKER khi gesture khớp preset | Must Have | OQ-2 |

## 7. Non-Functional Requirements
| Category | Requirement | Metric |
|----------|-------------|--------|
| Performance | WM_MOUSEMOVE + gesture recognition không block hook | <1ms/move event, <5ms tại right_up |
| Reliability | Hook không treo/rớt | Watchdog 10s hiện có vẫn hoạt động |
| Compatibility | switch_tab()/execute()/MouseHookService.__init__ giữ signature | Config v1/v2 tự migrate lên v3 |
| Resource | Buffer move points | Tối đa 200 điểm/phiên RMB, tự giải phóng |
| Maintainability | File ≤150 dòng | settings_window.py không thêm dòng; gesture_recognizer.py/gesture_settings_dialog.py mới ≤150 dòng |

## 8. Out of Scope
- Firefox/Safari.
- Gesture/X1-X2 khi KHÔNG giữ RMB (giữ hành vi gốc).
- Thay thế Shift+Scroll (F-001) — giữ nguyên song song.
- Gesture hình tự do ngoài 8 hướng (vòng tròn, chữ cái).

## 9. Dependencies
- `mouse_hook_service.py`, `mouse_mapper_logic.py`, `tab_switch_logic.py`, `hotkey_service.py`, `shortcut_executor.py`, `config_service.py`, `settings_window.py` (không đổi), `tray_ui.py`, `main.py`.
- Windows User32 API (WH_MOUSE_LL, WM_XBUTTONDOWN, SendInput, GetForegroundWindow).

## 10. Definition of Done (Feature-level)
- [ ] US-003..US-006 Acceptance Criteria pass.
- [ ] LOCKED Behaviors #1-#8 giữ nguyên trừ phần GESTURE đã duyệt đổi.
- [ ] Shift+Scroll (F-001) và RMB+Scroll (Panel/Alt+Tab) không bị ảnh hưởng.
- [ ] X1/X2 khi không giữ RMB hoạt động Back/Forward bình thường.
- [ ] Không file nào vượt 150 dòng.
- [ ] PRD status draft → approved.

## 11. Timeline
| Milestone | Date | Notes |
|-----------|------|-------|\
| M1 PRD/ADR | 2026-11-08 | Done |
| M2 Implementation | 2026-11-08/09 | Batch 1 (9 tasks) |
| M3 Validate & release | 2026-11-09 | v2.11.0 |

## 12. Open Questions
- Không có (đã chốt hết ở elicitation/PRD review).

## 13. Changelog
| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-11-08 | Antigravity/Claude | Initial draft, rà soát + chốt OQ-1..OQ-4 |
