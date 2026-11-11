---
id: prd_f013-remove-volume-fix-render-flicker_20261111
title: "Remove Volume UI & Fix Panel Render Flicker (F-013)"
status: draft
version: 1.0
author: Antigravity / Claude
created: 2026-11-11
updated: 2026-11-11
tags: [shortcut-panel, render-flicker, volume-cleanup, performance, ui-smoothness]
summary: "Loại bỏ hoàn toàn toàn bộ tính năng và mã nguồn quản lý Volume khỏi UI và codebase. Khắc phục triệt để hiện tượng chớp nháy (render flicker) và độ trễ khi cuộn/navigate trong Shortcut Panel bằng cách tách biệt full re-render khỏi in-place highlight update."
---

# PRD: Remove Volume UI & Fix Panel Render Flicker (F-013)

## 1. Overview
**Problem**:
1. **Shortcut Panel render flicker & lag**: Mỗi khi người dùng cuộn chuột hoặc bấm phím mũi tên/phím số để navigate, `panel_window.py` gọi `_render()` phá hủy toàn bộ widget con (`winfo_children().destroy()`) rồi tạo lại từ đầu. Quá trình này bao gồm cả việc tạo mới `PanelVolumeWidget` (thực hiện 2 cuộc gọi đồng bộ COM Core Audio qua `volume_service.py` mỗi lần vẽ), dẫn đến panel bị chớp giật liên tục và giật lag nghiêm trọng khi cuộn.
2. **Loại bỏ tính năng Volume**: Người dùng không còn nhu cầu quản lý hay hiển thị Volume qua RightWheel (thường dùng phím cứng bàn phím hoặc Quick Settings Windows), và muốn loại bỏ triệt để toàn bộ UI, logic, dịch vụ và cấu hình Volume để giao diện tinh gọn, mã nguồn sạch sẽ, không phụ thuộc vào Core Audio ctypes COM.

**Solution**:
1. **Tách biệt cơ chế render giao diện trong `panel_window.py` & `panel_item_renderer.py`**:
   - **Full re-render**: Chỉ thực hiện khi mở panel lần đầu (`_do_show`) hoặc khi cấu trúc danh sách thực sự thay đổi (chuyển profile, vào/ra thư mục qua breadcrumb, toggle trạng thái pause).
   - **In-place highlight update**: Khi di chuyển vị trí chọn (`navigate`, `select_at`, cuộn chuột) trong cùng một danh sách, chỉ cập nhật trạng thái hiển thị (màu nền, accent bar, badge phím số, font style) của hàng cũ và hàng mới trên các widget có sẵn. Tuyệt đối không xóa/tạo lại widget.
2. **Gỡ bỏ sạch sẽ toàn bộ tính năng và mã nguồn Volume**:
   - Xóa bỏ 3 file module: `volume_service.py`, `volume_overlay.py`, `panel_volume_widget.py`.
   - Dọn dẹp `panel_window.py`: Bỏ import và các thuộc tính overlay/widget, bỏ callback `on_show_volume_slider`, method `open_volume_slider`, message `"volume"`, handler `_do_volume`, và thẻ Volume Widget ở root panel.
   - Dọn dẹp `panel_item_renderer.py`: Bỏ nhánh đọc `volume_service` cho action `show_volume_slider`.
   - Refactor `general_volume_tab.py`: Loại bỏ Card Volume Control (âm lượng hiện tại, mô tả HUD, radio buttons chọn bước nhảy); chỉ giữ lại Card System Startup và Card Language; đổi tên tab thành `GeneralTab` / `general_tab.py`.
   - Cập nhật `settings_window.py`: Đổi nhãn tab "General & Volume" thành "General" và trỏ sang `GeneralTab`.
   - Dọn dẹp `config_service.py`: Xóa `volume_step`, `show_panel_volume` khỏi `_DEFAULT`, xóa item `show_volume_slider` khỏi danh sách `default`, xóa các hàm getter `get_volume_step()`, `get_show_panel_volume()`.
   - Dọn dẹp `panel_logic.py`, `panel_types.py`, `action_picker_dialog.py`: Xóa callback `on_show_volume_slider`, action handling `show_volume_slider`, docstring, và lựa chọn trong dialog picker.
   - Dọn dẹp dead code `shortcut_executor.py`: Xóa hàm `send_volume_step()` và các hằng số `VK_VOLUME_*`.
   - Dọn dẹp `reference_shortcuts_data.py`: Xóa dòng RightWheel Volume item.
   - Dọn dẹp 9 file i18n (`src/features/i18n/*.py`): Xóa key `"action.show_volume_slider"`.
   - Dọn dẹp `main.py`: Bỏ dòng gán callback `panel.on_show_volume_slider = panel_window.open_volume_slider`.
   - Dọn dẹp file cấu hình thật của user (`%APPDATA%\RightWheel\shortcuts.json`): Xóa key `volume_step`, `show_panel_volume` và mọi item có `action == "show_volume_slider"`.

**Success Metrics**:
- 0 lần destroy/recreate widget khi điều hướng lên/xuống/nhảy số trong cùng menu -> 0 hiện tượng chớp nháy (flicker) bằng mắt thường.
- Tốc độ phản hồi navigate tức thì (< 1ms CPU time trên luồng Tkinter, không còn nghẽn bởi COM Core Audio calls).
- 0 file, 0 dòng mã nguồn, 0 key cấu hình và 0 key i18n liên quan đến Volume còn tồn tại trong codebase.
- Các tính năng còn lại của Shortcut Panel (app, shortcut, url, folder navigation, settings, pause, active profile) hoạt động trơn tru, không hồi quy.

## 2. User Stories & Acceptance Criteria

### US-034: Fix Panel Render Flicker & In-Place Selection Highlight
**As a** người dùng Shortcut Panel,  
**I want to** cuộn chuột hoặc bấm phím mũi tên điều hướng giữa các mục phím tắt mượt mà,  
**So that** giao diện không bị giật, chớp nháy màn hình và có độ phản hồi tức thì.
**Acceptance Criteria:**
- [ ] `panel_item_renderer.py` lưu trữ danh sách các widget hàng (`_rows`), cung cấp cơ chế cập nhật highlight tại chỗ (`update_highlight(old_idx, new_idx)` hoặc `set_selected_index(idx)`).
- [ ] `panel_window.py` phân biệt rõ ràng giữa full re-render (khi `items`, `breadcrumb`, `profile`, `paused` đổi) và highlight update (khi chỉ đổi `index`).
- [ ] Khi cuộn chuột hoặc bấm Up/Down/0-9 trong cùng một folder/danh sách: 0 widget con của `_win` bị destroy hoặc tạo lại.
- [ ] Hiệu ứng visual (accent bar xanh, background highlight, kbd badge nổi bật) chuyển đổi chính xác, mượt mà giữa hàng cũ và hàng mới.

### US-035: Gỡ bỏ Volume UI khỏi Shortcut Panel & Item Renderer
**As a** người dùng Shortcut Panel,  
**I want to** giao diện panel không còn chứa bất kỳ widget hay nhãn âm lượng nào,  
**So that** panel hiển thị gọn gàng và không tốn tài nguyên gọi API âm lượng hệ thống.
**Acceptance Criteria:**
- [ ] `panel_window.py` gỡ bỏ import `PanelVolumeWidget` và `VolumeOverlay`.
- [ ] Xóa bỏ `self._volume_overlay`, `self._volume_widget`, `open_volume_slider()`, `_do_volume()`, và xử lý lệnh `"volume"` trong message queue `_q`.
- [ ] Gỡ bỏ khối mã khởi tạo `PanelVolumeWidget` ở root level trong `_render()`.
- [ ] `panel_item_renderer.py` gỡ bỏ nhánh override nhãn động `Master Volume (XX%)` và import `volume_service`.
- [ ] `panel_logic.py` gỡ bỏ `self.on_show_volume_slider` và nhánh `elif action == "show_volume_slider"`.
- [ ] `main.py` gỡ bỏ dòng gán callback `panel.on_show_volume_slider = panel_window.open_volume_slider`.

### US-036: Xóa bỏ các Module Volume độc lập và dọn dẹp Shortcut Executor
**As a** lập trình viên dự án RightWheel,  
**I want to** loại bỏ hoàn toàn các file mã nguồn và hàm dead code liên quan đến Volume,  
**So that** codebase không còn mã nguồn thừa, không phụ thuộc vào Core Audio ctypes COM.
**Acceptance Criteria:**
- [ ] Xóa hoàn toàn 3 file:
  - `src/features/shortcut_panel/services/volume_service.py`
  - `src/features/shortcut_panel/ui/panel_volume_widget.py`
  - `src/features/shortcut_panel/ui/volume_overlay.py`
- [ ] `shortcut_executor.py` xóa bỏ hàm `send_volume_step(delta: int)` và các hằng số không dùng: `VK_VOLUME_MUTE`, `VK_VOLUME_DOWN`, `VK_VOLUME_UP`.
- [ ] Toàn bộ mã nguồn không còn bất kỳ lệnh import nào trỏ tới 3 file đã xóa.

### US-037: Refactor General Settings Tab & Cập nhật Settings Window
**As a** người dùng trang Cài đặt (Settings),  
**I want to** tab cài đặt chung chỉ tập trung vào cấu hình hệ thống (Khởi động cùng Windows, Ngôn ngữ),  
**So that** giao diện cài đặt rõ ràng, không còn các tùy chọn âm lượng không sử dụng.
**Acceptance Criteria:**
- [ ] `general_volume_tab.py` được refactor (và đổi tên thành `general_tab.py` với class `GeneralTab` theo quyết định ADR):
  - Gỡ bỏ hoàn toàn Card 1: Volume Control (nhãn volume hiện tại, mô tả HUD, radio buttons chọn bước nhảy 2%, 5%, 10%).
  - Gỡ bỏ import `volume_service`, biến trạng thái `_step_var`, và hàm `_on_step_change`.
  - Giữ nguyên toàn vẹn Card 2 (System Startup) và Card 3 (Language selector).
- [ ] `settings_window.py` cập nhật nhãn danh mục từ "General & Volume" thành "General" và trỏ sang import tab mới.

### US-038: Dọn dẹp Schema Config, Types, Dialogs, Data, i18n & User Data Migration
**As a** người dùng và hệ thống RightWheel,  
**I want to** cấu hình mặc định, kiểu dữ liệu, bảng tra cứu phím tắt và dữ liệu cấu hình cá nhân được làm sạch hoàn toàn khỏi Volume,  
**So that** không phát sinh lỗi tương thích ngược và cấu hình đồng nhất trên toàn hệ thống.
**Acceptance Criteria:**
- [ ] `config_service.py`:
  - Xóa `"volume_step"` và `"show_panel_volume"` khỏi `_DEFAULT`.
  - Xóa item `{"type": "action", "label": "Volume Control", "action": "show_volume_slider"}` khỏi `_DEFAULT["default"]`.
  - Xóa 2 hàm `get_volume_step()` và `get_show_panel_volume()`.
- [ ] `panel_types.py`: Xóa `"show_volume_slider"` khỏi docstring `ActionItem.action`.
- [ ] `action_picker_dialog.py`: Xóa entry `("show_volume_slider", "action.show_volume_slider")` khỏi danh sách `ACTIONS`.
- [ ] `reference_shortcuts_data.py`: Xóa dòng `("RightWheel", "Panel item: Volume", "Open volume slider HUD, scroll to adjust")`. Giữ nguyên các phím tắt Windows chung (`Volume Up/Down/Mute keys`).
- [ ] `src/features/i18n/*.py` (cả 9 ngôn ngữ: en, es, fr, id, it, pt, th, vi, zh): Xóa key `"action.show_volume_slider"`.
- [ ] Migration cấu hình thật của người dùng: Quét và làm sạch `%APPDATA%\RightWheel\shortcuts.json`:
  - Xóa thuộc tính cấp root `"volume_step"`, `"show_panel_volume"` nếu có.
  - Xóa bất kỳ item nào có trường `"action": "show_volume_slider"` trong danh sách `default` hoặc các `profiles`.

## 3. Constraints & Dependencies
- Không làm ảnh hưởng đến mouse hook và gesture engine (`mouse_mapper_logic.py`, `mouse_hook_service.py` - LOCKED).
- Không ảnh hưởng đến các hành vi cốt lõi của panel: điều hướng bàn phím (Enter để chọn, Esc để thoát, BackSpace để lùi folder, phím số 0-9 để nhảy mục).
- Toàn bộ file mã nguồn tuân thủ SYSTEM LOCK (≤ 250 dòng).
- Không thêm bất kỳ third-party dependency mới nào (chỉ dùng Python standard library & Tkinter).
