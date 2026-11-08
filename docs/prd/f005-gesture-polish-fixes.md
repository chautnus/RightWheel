---
id: prd_f005-gesture-polish-fixes_20261108
title: "Fix 5 bug cốt lõi sau kiểm thử thực tế Mouse Gesture & Rocker (F-005)"
status: draft
version: 1.0
author: Antigravity / Claude
created: 2026-11-08
updated: 2026-11-08
tags: [mouse-mapper, gesture-trail, rocker-gesture, focus-management, pyinstaller-restart, bug-fix]
summary: "Sửa dứt điểm 5 bug phát sinh sau test tay F-004: X1/X2 khoá context menu, trail vẽ dây cung thẳng, overlay cướp focus Chromium, rung tay nuốt context menu, và lỗi xoá thư mục tạm khi Restart."
---

# PRD: Fix 5 bug cốt lõi sau kiểm thử thực tế Mouse Gesture & Rocker (F-005)

## 1. Overview
**Problem**: Sau kiểm thử thực tế bản .exe F-004, 5 lỗi nghiêm trọng xuất hiện:
1. Rocker Gesture (RMB+X1/X2) chỉ work lần đầu — nhả RMB gọi inject_right_click() bật Context Menu modal Chromium, khoá cứng thao tác chuột tiếp theo.
2. TrailOverlay thiếu WS_EX_NOACTIVATE, cướp Foreground Focus của Chromium.
3. Nét vẽ đầu tiên là 1 đường thẳng/dây cung dị thường do neo vào toạ độ _down cũ thay vì cursor thật lúc Canvas sẵn sàng.
4. main.py hardcode move_threshold=8 đè default 50px, kết hợp Silent Drop của F-004 khiến rung tay nhẹ nuốt mất Context Menu thường.
5. tray_ui.py dùng os.execve giữ handle DLL khiến PyInstaller bootloader báo lỗi "Failed to remove temporary folder" khi Restart.

**Solution**: Thêm cờ `_xbutton_used` triệt tiêu inject_right_click() sai; set 4 Win32 extended styles (NOACTIVATE/TRANSPARENT/LAYERED/TOOLWINDOW) cho overlay; neo `_last_point` từ GetCursorPos thật; bỏ hardcode threshold; đổi `_restart()` sang subprocess.Popen detached.

**Success Metrics**: 100% X1/X2 liên tiếp hoạt động không bị khoá; 0% mất focus Chromium; 0% dây cung thẳng; 100% click phải thường hiện context menu; 0 lỗi "Failed to remove temporary folder".

## 2. Background & Context
F-004 hoàn thành kiến trúc gesture/trail nhưng test tự động (mock/headless) không phát hiện được hành vi cấp OS (Active Window Focus, Win32 Modal Menu Loop, PyInstaller process lifecycle). Debug1+debug2 (docs/debug/gesture-trail-x1x2-flaky.debug1.md, .debug2.md, phán quyết "CẢ HAI ĐỀU GÓP PHẦN") định vị chính xác 5 nguyên nhân tới từng dòng code.

## 3. Jobs To Be Done (JTBD)
> **When** tôi dùng RightWheel hàng ngày để chuyển tab bằng RMB+X1/X2, vẽ gesture, hoặc Restart từ tray, **I want to** các thao tác liên tục không bị kẹt menu, nét vẽ bám sát chuột, click phải không bị nuốt, Restart êm ái, **so I can** làm việc tin cậy không gặp phiền toái.

## 4. Stakeholders
| Role | Name | Responsibility |
|---|---|---|
| Product Owner | User/Claude | Phê duyệt PRD |
| Tech Lead | Claude/Antigravity | Kiến trúc |
| Developer | Antigravity | Triển khai |
| Tester | User | Test tay thật trên Windows |

## 5. User Stories & Acceptance Criteria

### US-012: Cờ _xbutton_used ngăn rò rỉ inject_right_click sau Rocker Gesture
**As a** người dùng chuyển tab bằng RMB+X1/X2, **I want to** nhả RMB không bật Context Menu, **So that** thao tác tiếp theo không bị khoá.
**Acceptance Criteria:**
- [ ] Given RIGHT_HELD, When bấm X1/X2 chuyển tab thành công, Then `_xbutton_used=True`.
- [ ] Given `_xbutton_used=True`, When nhả RMB, Then KHÔNG gọi inject_right_click(), reset cờ về False.
- [ ] Given bắt đầu chu kỳ RMB mới (_on_right_down), Then `_xbutton_used` luôn reset False.
- [ ] Given click phải thường (không dùng X1/X2), When nhả RMB, Then inject_right_click() vẫn gọi, Context Menu vẫn hiện.

### US-013: WS_EX_NOACTIVATE cho TrailOverlay ngăn cướp Focus
**As a** người dùng vẽ gesture, **I want to** overlay không cướp Active Window của Chromium, **So that** phím tắt/X1X2 gửi đúng tới trình duyệt.
**Acceptance Criteria:**
- [ ] Given overlay hiển thị, Then set đủ WS_EX_NOACTIVATE|TRANSPARENT|LAYERED|TOOLWINDOW qua SetWindowLongPtrW.
- [ ] Given Chromium là Foreground, When overlay xuất hiện, Then GetForegroundWindow() vẫn là Chromium.
- [ ] Given overlay đang hiển thị, Then mọi sự kiện chuột xuyên thấu xuống dưới.

### US-014: Khắc phục dây cung thẳng ban đầu của Trail
**As a** người dùng bắt đầu vẽ gesture, **I want to** nét vẽ xuất phát từ vị trí chuột thật lúc Canvas sẵn sàng, **So that** không có đường thẳng dị thường.
**Acceptance Criteria:**
- [ ] Given Canvas sẵn sàng trong _do_start, Then `_last_point` lấy từ GetCursorPos() thật, KHÔNG dùng toạ độ `_down` truyền vào.
- [ ] Given kéo nhanh 1 đường cong, Then nét vẽ bám quỹ đạo thật, không nối tắt từ toạ độ cũ.

### US-015: Khôi phục move_threshold=50 mặc định
**As a** người dùng click phải/dùng X1/X2, **I want to** rung tay <50px không kích hoạt GESTURE, **So that** không bị Silent Drop nuốt Context Menu.
**Acceptance Criteria:**
- [ ] Given main.py, When khởi tạo MouseMapperLogic, Then KHÔNG truyền move_threshold=8, dùng default 50.
- [ ] Given rung tay <50px khi click phải, Then vẫn ở RIGHT_HELD, Context Menu hiện bình thường.

### US-016: Restart an toàn cho PyInstaller onefile
**As a** người dùng bấm Restart trong tray, **I want to** không gặp lỗi xoá thư mục tạm, **So that** restart ổn định 100%.
**Acceptance Criteria:**
- [ ] Given bấm Restart, Then dùng subprocess.Popen (shell=True, detached) thay os.execve, kèm delay để process cũ thoát hẳn.
- [ ] Given tiến trình đã spawn xong, Then gọi sys.exit(0) để bootloader dọn _MEI sạch.
- [ ] Given bản .exe PyInstaller onefile, When Restart, Then không còn lỗi "Failed to remove temporary folder".

## 6. Functional Requirements
| ID | Requirement | Priority | Story |
|----|-------------|----------|-------|
| FR-001 | `_xbutton_used: bool = False` trong __init__, reset trong _on_right_down | Must Have | US-012 |
| FR-002 | Set `_xbutton_used=True` trong _on_xbutton_down sau switch_tab_x1x2 thành công | Must Have | US-012 |
| FR-003 | _on_right_up nhánh RIGHT_HELD: nếu _xbutton_used thì skip inject_right_click(), reset cờ | Must Have | US-012 |
| FR-004 | SetWindowLongPtrW thêm WS_EX_NOACTIVATE\|TRANSPARENT\|LAYERED\|TOOLWINDOW cho overlay HWND | Must Have | US-013 |
| FR-005 | _last_point lấy từ GetCursorPos() thật trong _do_start thay vì toạ độ (x,y) truyền vào | Must Have | US-014 |
| FR-006 | main.py: MouseMapperLogic() không truyền move_threshold, dùng default 50 | Must Have | US-015 |
| FR-007 | tray_ui.py _restart(): subprocess.Popen(shell=True, detached) + delay + sys.exit(0) thay os.execve | Must Have | US-016 |

## 7. Non-Functional Requirements
| Category | Requirement | Metric |
|---|---|---|
| OS-Level Stability | TrailOverlay không đổi Foreground Window | GetForegroundWindow() không đổi |
| No Ghost Clicks | Rocker Gesture không rò rỉ click phải | 0 lần Context Menu sau X1/X2 |
| Process Lifecycle | Restart không giữ handle _MEI | 0 lỗi "Failed to remove temporary folder" |
| Compatibility | Schema config, 2 mode scroll LOCKED giữ nguyên | Không đổi |
| Mandatory Verification | Test tay thật bắt buộc cho US-012/013/014/016 | Báo cáo test thật 100% PASS |

## 8. Out of Scope
- Refactor mouse_hook_service.py (rủi ro hook timeout — điểm 6 debug2, để sau).
- SetProcessDpiAwareness toàn app.
- Fade animation cho trail. Bảo toàn RMB-drag cho app thứ 3.

## 9. Dependencies
- Win32 API (GetCursorPos, SetWindowLongPtrW, GetWindowLongPtrW, GetParent, GetSystemMetrics), subprocess, sys, os, tkinter, pystray.
- mouse_mapper_logic.py, trail_overlay.py, main.py, tray_ui.py.

## 10. Definition of Done
- [ ] US-012..US-016 AC pass.
- [ ] X1/X2 liên tục không khoá; trail mượt không dây cung; context menu thường vẫn hiện; Restart không lỗi.
- [ ] File ≤250 dòng (LOCK), ≤150 dòng khuyến nghị.
- [ ] PRD status → approved.

## 11. Timeline
| Milestone | Date | Notes |
|---|---|---|
| PRD+ADR | 2026-11-08 | Done |
| Implementation | 2026-11-08 | Batch 1 (5 task) |
| Test tay thật + release | 2026-11-08/09 | v2.14.2 |

## 12. Open Questions
- Không có.

## 13. Changelog
| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-11-08 | Antigravity/Claude | Initial draft, dựa trên debug1+debug2 |
