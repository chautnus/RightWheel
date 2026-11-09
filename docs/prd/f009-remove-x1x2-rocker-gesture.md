---
id: prd_f009-remove-x1x2-rocker-gesture_20261109
title: "Remove X1/X2 Rocker Gesture & Fix Mouse Button Hangs (F-009)"
status: draft
version: 1.0
author: Antigravity / Claude
created: 2026-11-09
updated: 2026-11-09
tags: [mouse-mapper, rocker-gesture, bug-fix, cleanup, reliability, left-click-stuck]
summary: "Loại bỏ hoàn toàn cơ chế chặn nút phụ X1/X2 và hàm xử lý cử chỉ rocker gesture RMB + X1/X2. Khắc phục triệt để lỗi kẹt chuột trái (left click vô tác dụng) và lỗi chuột phải không kích hoạt do mất đồng bộ trạng thái chuột trong low-level hook."
---

# PRD: Remove X1/X2 Rocker Gesture & Fix Mouse Button Hangs (F-009)

## 1. Overview
**Problem**:
Từ khi đưa vào tính năng Rocker Gesture (RMB + X1/X2 để chuyển tab trình duyệt ở F-003/F-005), người dùng thường xuyên gặp lỗi nghiêm trọng:
1. Nút chuột trái thỉnh thoảng bị kẹt, click chuột trái hoàn toàn mất tác dụng trên toàn hệ thống.
2. Nút chuột phải (RMB) không kích hoạt được context menu hoặc rơi vào trạng thái lệch pha.
3. Nút phụ X1/X2 khó bấm đồng thời khi đang giữ RMB, gây vướng víu và trải nghiệm kém.
4. Cơ chế chặn `WM_XBUTTONDOWN` nhưng không xử lý `WM_XBUTTONUP` làm mất cân bằng chuỗi sự kiện chuột cấp thấp trong `WH_MOUSE_LL`.

**Solution**:
Loại bỏ hoàn toàn việc chặn và xử lý sự kiện `WM_XBUTTONDOWN` trong `mouse_hook_service.py`, dọn dẹp logic liên quan trong `mouse_mapper_logic.py`, `hotkey_service.py`, `mouse_mapper_types.py` và bảng tra cứu `reference_tab.py`.
Trả các nút phụ X1/X2 về cho Windows và driver chuột gốc xử lý bình thường (Back/Forward).

**Success Metrics**:
- Triệt tiêu 100% hiện tượng kẹt chuột trái hoặc RMB không kích hoạt sau khi bấm chuột.
- 0 can thiệp vào sự kiện X1/X2 trong `mouse_hook_service.py`.
- Các tính năng khác (Shortcut Panel, Dual-mode scroll, Vẽ cử chỉ 8 hướng, Shift+Scroll tab switch) hoạt động mượt mà, không hồi quy.

## 2. User Stories & Acceptance Criteria

### US-027: Loại bỏ hoàn toàn hook X1/X2 và xử lý cử chỉ rocker
**As a** người dùng RightWheel,  
**I want to** ứng dụng không can thiệp vào các nút phụ X1/X2,  
**So that** chuột trái và chuột phải không bao giờ bị kẹt hoặc mất tác dụng.
**Acceptance Criteria:**
- [ ] `mouse_hook_service.py` không còn lắng nghe hoặc chặn `WM_XBUTTONDOWN` (bỏ `WM_XBUTTONDOWN`, `XBUTTON1`, `XBUTTON2`).
- [ ] `mouse_mapper_logic.py` không còn cờ `_xbutton_used`, bỏ nhánh `xbutton_down` trong `handle()` và xóa phương thức `_on_xbutton_down()`.
- [ ] `hotkey_service.py` xóa bỏ hàm `switch_tab_x1x2()`.
- [ ] `reference_tab.py` bỏ mục hướng dẫn "RMB + X1/X2".
- [ ] Toàn bộ mã nguồn biên dịch sạch không có lỗi hay cảnh báo.

## 3. Constraints
- Không làm ảnh hưởng đến State Machine cốt lõi:
  - `_on_right_down` -> `RIGHT_HELD`
  - `_on_scroll` -> UP mở panel, DOWN mở Alt+Tab
  - `_on_move` -> `GESTURE`
  - `_on_right_up` -> nhả đúng và sạch sẽ.
- Toàn bộ file mã nguồn tuân thủ SYSTEM LOCK (≤ 250 dòng).
