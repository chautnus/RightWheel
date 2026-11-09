---
id: prd_f007-modern-ui-volume-front_20261109
title: "Modern Minimalist UI & Volume Fronting (F-007)"
status: draft
version: 1.0
author: Antigravity / Claude
created: 2026-11-09
updated: 2026-11-09
tags: [ui-redesign, minimalist, volume-control, shortcut-panel, settings-window, volume-hud, modern-dark]
summary: "Tái thiết kế toàn diện giao diện RightWheel (Shortcut Panel, Volume Overlay HUD, Settings Window) theo phong cách Modern Dark Minimalist (Fluent/Raycast), tích hợp Volume Bar trực tiếp trên Shortcut Panel và nâng cấp Capsule HUD với icon loa động và nhãn %."
---

# PRD: Modern Minimalist UI & Volume Fronting (F-007)

## 1. Overview
**Problem**:
- Giao diện hiện tại mang phong cách Tkinter cổ điển, màu sắc tối giản nhưng thô cứng, thiếu sự tinh tế của các app tiện ích hiện đại (Raycast, Windows 11 Fluent).
- Điều khiển âm lượng (F-006) vừa ra mắt nhưng bị giấu trong folder `📁 App`, người dùng phải mở menu 2 cấp mới tiếp cận được.
- Cửa sổ Settings Window dùng thanh tab `ttk.Notebook` cũ, bảng Listbox phẳng thô và thiếu khu vực cấu hình tiện ích Volume chuyên biệt.

**Solution**:
1. **Shortcut Panel**: Tích hợp thanh trượt Volume Quick-Widget trực tiếp trên đỉnh Panel, hỗ trợ cuộn chuột hoặc click kéo; thiết kế lại các item shortcut dạng thẻ bo góc mềm, badge số tắt [0-9] tinh tế, highlight hover hiện đại.
2. **Volume Overlay HUD**: Nâng cấp thành dạng Capsule/Pill HUD nổi phong cách Windows 11 Flyout / macOS, icon loa biến đổi theo mức âm lượng (🔇/🔈/🔉/🔊), hiển thị thanh tiến trình bo cong và nhãn phần trăm rõ ràng.
3. **Settings Window**: Chuyển đổi từ `ttk.Notebook` ngang sang Modern Sidebar Navigation (Navigation Rail) bên trái với icons hiện đại, bên phải là Content Cards bo góc phong cách Slate/Zinc tối giản, bổ sung khu vực cấu hình Volume & Appearance chuyên biệt.
4. **Config & Defaults**: Đưa action Volume Control ra ngoài root shortcuts mặc định và lưu tùy chọn volume step size.

**Success Metrics**:
- Giao diện trực quan, đồng bộ phong cách Modern Dark Minimalist trên cả 3 bề mặt UI.
- Thao tác chỉnh volume ngay trên Shortcut Panel nhanh hơn 2x (không cần vào folder con).
- 100% file mã nguồn tuân thủ giới hạn SYSTEM LOCK (≤ 250 dòng).

## 2. Background & Context
RightWheel đã hoàn thiện State Machine (F-001/F-002), Gesture Engine (F-003..F-005) và Volume Control cơ bản (F-006). F-007 tập trung vào trải nghiệm người dùng (UX) và thẩm mỹ thị giác (UI), biến RightWheel thành một công cụ làm việc vừa mạnh mẽ vừa cao cấp.

## 3. Jobs To Be Done (JTBD)
> **When** tôi gọi Shortcut Panel hoặc dùng phím tắt/chuột điều khiển âm lượng, **I want to** trải nghiệm một giao diện hiện đại, tối giản, thanh thoát với Volume Control ngay phía trước, **so I can** thao tác mượt mà, nhanh gọn và có cảm giác thẩm mỹ chuyên nghiệp.

## 4. Stakeholders
| Role | Name | Responsibility |
|---|---|---|
| Product Owner | User | Phê duyệt yêu cầu và kế hoạch |
| Architect & Developer | Antigravity | Thiết kế kiến trúc và thực thi |
| Verification | User & Antigravity | Kiểm thử tĩnh và kiểm thử tay |

## 5. User Stories & Acceptance Criteria

### US-020: Quick Volume Bar trên Shortcut Panel
**As a** user thường xuyên dùng Shortcut Panel,  
**I want to** thấy thanh âm lượng tích hợp ngay trên đầu Panel khi mở,  
**So that** tôi có thể cuộn chuột hoặc xem âm lượng ngay lập tức mà không cần click vào folder con.
**Acceptance Criteria:**
- [ ] Khi Shortcut Panel hiển thị, trên cùng panel có Volume Widget nhỏ gọn gồm: icon loa, thanh trượt mini, % âm lượng.
- [ ] Cuộn chuột khi con trỏ đang nằm trên Volume Widget (hoặc Panel khi đang ở widget mode) sẽ tăng/giảm âm lượng hệ thống và cập nhật thanh slider tức thì.
- [ ] Vẫn giữ nguyên phím số 0-9 để jump trực tiếp tới các shortcut bên dưới.
- [ ] Mục `🔊 Volume Control` được đưa ra root menu mặc định trong `shortcuts.json`.

### US-021: Capsule Volume Overlay HUD
**As a** user kích hoạt chỉnh âm lượng riêng biệt,  
**I want to** thấy một HUD dạng viên thuốc (Capsule) nổi bo tròn hiện đại,  
**So that** trải nghiệm thị giác tương đồng với Windows 11 Flyout / macOS.
**Acceptance Criteria:**
- [ ] HUD có kích thước nhỏ gọn dạng Capsule bo góc (~220x46px), nền tối mờ `#18181b`, viền tinh tế `#27272a`.
- [ ] Icon loa tự động cập nhật: 🔇 (0%), 🔈 (1-33%), 🔉 (34-66%), 🔊 (67-100%).
- [ ] Thanh tiến trình bo góc mượt mà, kèm nhãn số phần trăm (ví dụ: `65%`).
- [ ] Tự ẩn sau 3 giây không tương tác hoặc khi nhấn ESC/click ra ngoài.

### US-022: Modern Sidebar Navigation cho Settings Window
**As a** user mở cửa sổ Settings,  
**I want to** một giao diện hiện đại với thanh điều hướng Sidebar bên trái và các thẻ cấu hình bo góc bên phải,  
**So that** việc cấu hình trực quan, thoáng đãng và dễ nhìn hơn tab Notebook cũ.
**Acceptance Criteria:**
- [ ] SettingsWindow chuyển sang layout: Cột trái (Sidebar 180px) hiển thị các danh mục (General & Volume, Shortcuts, Gestures, Reference, License) với icon đại diện; Cột phải hiển thị thẻ nội dung (Card Container).
- [ ] Nút chọn tab trên Sidebar có trạng thái Active rõ ràng (nền sáng hơn, vạch chỉ báo accent color).
- [ ] Bảng màu chuẩn Slate/Zinc Dark (`#09090b` nền chính, `#18181b` card nền, `#27272a` viền).

### US-023: Tùy biến Volume & Giao diện trong Settings
**As a** user,  
**I want to** tùy chỉnh bước nhảy volume (step size: 2%, 5%, 10%) và bật/tắt hiển thị Volume Bar trên Panel,  
**So that** ứng dụng hoạt động đúng theo thói quen của tôi.
**Acceptance Criteria:**
- [ ] Thẻ "Volume & General" trong Settings cho phép chọn bước nhảy âm lượng (2%, 5%, 10%).
- [ ] Cho phép bật/tắt "Show Volume Bar on Shortcut Panel".
- [ ] Lưu cấu hình an toàn vào `shortcuts.json` mà không làm hỏng dữ liệu cũ.

## 6. Functional Requirements
| ID | Requirement | Priority | Story |
|---|---|---|---|
| FR-020 | Tích hợp `PanelVolumeWidget` vào `panel_window.py` ở đầu danh sách | Must Have | US-020 |
| FR-021 | Nâng cấp styling các item của `panel_window.py` (bo góc giả lập, padding, badge [0-9]) | Must Have | US-020 |
| FR-022 | Nâng cấp `volume_overlay.py` thành Capsule HUD với icon loa động và nhãn % | Must Have | US-021 |
| FR-023 | Tái cấu trúc `settings_window.py` thành Sidebar Navigation layout | Must Have | US-022 |
| FR-024 | Tạo tab/card `general_volume_tab.py` quản lý cấu hình Volume và Startup | Must Have | US-023 |
| FR-025 | Bổ sung field `volume_step` và `show_panel_volume` vào `config_service.py` | Should Have | US-023 |
| FR-026 | Cập nhật `_DEFAULT` trong `config_service.py` đưa Volume Control ra root level | Should Have | US-020 |

## 7. Non-Functional Requirements
- Không dùng dependency bên ngoài mới (giữ Tkinter/ctypes/pystray).
- Giới hạn dòng: Mọi file mới hoặc sửa đổi đều ≤ 250 dòng (SYSTEM LOCK).
- Thread-safe: Toàn bộ lệnh UI vẫn chạy trên Tkinter daemon thread của `panel_window`.

## 8. Out of Scope
- Không can thiệp `mouse_mapper_logic.py` (LOCKED).
- Không can thiệp `mouse_hook_service.py` (LOCKED).
- Không hỗ trợ chuyển đổi Light Theme (tập trung 100% vào Modern Dark Minimalist).

## 9. Definition of Done
- Tất cả các tiêu chí US-020 đến US-023 đạt Acceptance Criteria.
- Đã chạy kiểm tra cú pháp tĩnh `py_compile` và build check.
- Toàn bộ file liên quan ≤ 250 dòng.
