---
id: proj_ui_architecture_design_system_v2_11
type: project
title: "UI Architecture & Design System v2.11 — Zinc Tokens, Modern Settings, Gestures Playground & Web Landing"
tags: [ui, design-system, zinc, tkinter, settings, gestures, welcome, website]
keywords: [theme_tokens, settings_window, gestures_tab, playground, default_tab, welcome_window, preview_ui]
status: active
created: 2026-11-14
updated: 2026-11-14
summary: "Toàn bộ kiến trúc giao diện người dùng RightWheel v2.11: Hệ thống Design Tokens Zinc, tái thiết kế Settings 2 cột, bảng cử chỉ kèm canvas tương tác, Command Palette và Landing Page"
---

## 1. Tầm nhìn & Triết lý Thiết kế (Design Philosophy)

RightWheel v2.11 chuyển đổi toàn bộ giao diện từ phong cách Tkinter truyền thống sang **Linear / Raycast / shadcn Productivity Standard**:
- **Bảng màu trung tính Zinc**: Nền tối sâu (`#09090b` / `#121214` / `#18181b`), viền tinh tế (`#27272a`), chữ độ tương phản cao (`#f4f4f5` / `#a1a1aa`).
- **Nói KHÔNG với AI Generic**: Tuyệt đối không dùng gradient tím/xanh, neon glow, glassmorphism, bóng đổ xanh rực rỡ, hoặc lưới card đều nhau vô nghĩa.
- **Thực dụng & Rõ ràng**: Thay thế toàn bộ emoji bằng **Text Badges** chuyên nghiệp (`[App]`, `[Web]`, `[Folder]`, `[Cmd]`, `[Seq]`, `[Action]`, `[Keys]`, vector arrows `[ ↓ → ]`).
- **Tương tác trực quan**: Cung cấp **Gesture Playground** để người dùng vẽ thử chuột phải và nhận diện trực tiếp ngay trong giao diện cài đặt.
- **Bảo toàn Nhận diện Thương hiệu**: Giữ nguyên icon gốc (`assets/icon.png` 72x72) trên màn hình Chào mừng (Welcome), không thay thế bằng icon trừu tượng hay generic placeholder.

---

## 2. Hệ thống Design Tokens (`src/features/shortcut_panel/ui/theme.py`)

File tập trung quản lý toàn bộ màu sắc, typography và styling components:

### 2.1 Bảng màu Zinc (Dark Palette làm mặc định)
```python
BG_BASE        = "#09090b"   # Nền cửa sổ ngoài cùng
BG_SURFACE     = "#121214"   # Sidebar, container cấp 1
BG_CARD        = "#18181b"   # Card, item container, listbox background
BG_HOVER       = "#27272a"   # Trạng thái di chuột
BG_ACTIVE      = "#3f3f46"   # Trạng thái đang chọn / nhấn
BORDER_DEFAULT = "#27272a"   # Đường viền phân cách tiêu chuẩn
BORDER_MUTED   = "#1f1f23"   # Viền phân cách phụ
TEXT_PRIMARY   = "#f4f4f5"   # Văn bản chính (độ sáng cao)
TEXT_SECONDARY = "#a1a1aa"   # Nhãn phụ, mô tả ngắn (WCAG AA pass)
TEXT_MUTED     = "#71717a"   # Chú thích mờ, placeholder
ACCENT_PRIMARY = "#0078d4"   # Brand Blue Windows Native
ACCENT_MUTED   = "#1d4ed8"   # Điểm nhấn cấp 2
SUCCESS        = "#22c55e"   # Chỉ báo trạng thái kích hoạt (● BẬT)
DANGER         = "#ef4444"   # Nút Xóa, cảnh báo
```

### 2.2 Typography (Native Segoe UI & Consolas)
- `FONT_TITLE`: `("Segoe UI", 13, "bold")` — Tiêu đề màn hình, section lớn
- `FONT_SECTION`: `("Segoe UI", 11, "bold")` — Tiêu đề nhóm cài đặt
- `FONT_BODY`: `("Segoe UI", 10)` — Nội dung văn bản, danh sách phím tắt
- `FONT_BOLD`: `("Segoe UI", 10, "bold")` — Nhãn nút bấm, tab được chọn
- `FONT_CAPTION`: `("Segoe UI", 9)` — Chú thích phụ, thông số
- `FONT_CODE`: `("Consolas", 10)` — Phím tắt, sequence command

### 2.3 Component Badges
Hàm `create_badge(parent, text, bg, fg)` tạo nhãn phẳng dạng pill với padding tối thiểu để phân loại loại shortcut hoặc vector cử chỉ trực quan.

---

## 3. Kiến trúc các Màn hình (Screen Implementations)

### 3.1 Settings Window (`settings_window.py`)
- **Bố cục 2 cột**:
  - **Sidebar trái** (`BG_SURFACE` `#121214`, rộng 190px): Danh mục tab với icon ký tự tối giản, chỉ báo viền trái `ACCENT_PRIMARY` dày 3px khi active, nút Đóng/Lưu ở đáy.
  - **Khu vực nội dung phải** (`BG_CARD` `#18181b`): Hiển thị tab tương ứng mà không tạo thêm root window.
- **Thứ tự Tab**: `Chung (general)` | `Phím tắt (shortcuts)` | `Cử chỉ chuột (gestures)` | `Tra cứu (reference)`.

### 3.2 Tab Phím tắt (`default_tab.py` - Master-Detail Modernization)
- **Top Action Toolbar**: Thay thế 11 nút dọc chiếm diện tích bằng thanh công cụ ngang:
  `[ + Phím tắt ]` | `[ + App ]` | `[ + URL ]` | `[ + Folder ]` | `[ + Khác ▾ ]` (chuỗi lệnh Sequence & hành động hệ thống) | `[ ⬇ Nhập ]`.
- **Full-Width Listbox**: Danh sách phím tắt chiếm trọn bề ngang với định dạng Badge chuẩn hóa:
  - `[App] Visual Studio Code`
  - `[Web] GitHub Dashboard`
  - `[Folder] Projects`
  - `[Seq] Chat & Send`
- **Bottom Action Bar**: Các nút thao tác vị trí và bản ghi `[ ↑ ]`, `[ ↓ ]`, `[ Sửa ]`, `[ Xóa ]` phân tách rõ ràng.

### 3.3 Tab Cử chỉ Chuột (`gestures_tab.py` - Interactive Gestures & Playground)
- **Danh sách Cử chỉ**: Hiển thị bảng vector cử chỉ với badge mũi tên trực quan `[ ↓ → ]` (L-shape đóng tab), `[ ↑ ]` (mở panel), v.v.
- **Chỉ báo Trạng thái**: Badge màu xanh `● BẬT` (`#22c55e`) hoặc `○ TẮT` (`#71717a`).
- **Interactive Gesture Playground**:
  - Khung Canvas tương tác cao 130px với nền `#121214` và viền nét đứt.
  - Người dùng giữ chuột phải và vẽ trực tiếp trên canvas.
  - Canvas vẽ đường trail mượt mà theo thời gian thực và tự động đưa toạ độ vào `GestureRecognizer`.
  - Hiển thị phản hồi tức thì: `Nhận diện: [ ↓ → ] Đóng tab hiện tại` kèm hiệu ứng viền xanh lá, giúp người dùng làm quen cử chỉ mà không ảnh hưởng đến ứng dụng đang chạy.
- **Cấu hình Đường vẽ & Độ nhạy**: Tùy chỉnh màu vệt chuột (Color picker), độ dày nét vẽ (Slider), số điểm tối thiểu và ngưỡng nhận diện (Threshold).

### 3.4 Command Palette / Shortcut Panel (`panel_window.py` & `panel_item_renderer.py`)
- **Raycast / Linear Palette**: Cửa sổ nổi hiển thị danh sách lệnh nhanh ngay dưới con trỏ chuột (`px - 10, py - 10`).
- **State Snapshot Diffing**: Thuật toán so khớp trạng thái và cập nhật in-place row highlight (`_row_views`), loại bỏ 100% hiện tượng giật/nháy (render flicker).
- **Z-Order Overlay Guard**: Overlay trong suốt bắt click-outside (`alpha=0.01`, topmost) và gọi `self._win.lift()` để không nuốt click chuột trái của người dùng.

### 3.5 Màn hình Chào mừng Onboarding (`welcome_window.py`)
- Cửa sổ Toplevel 480x560px với phong cách Zinc Dark sâu (`BG_BASE` / `BG_SURFACE`).
- **Giữ nguyên Brand Icon chuẩn**: Hiển thị ảnh `assets/icon.png` kích thước 72x72px ở vị trí trung tâm, sắc nét, không dùng placeholder.
- **3 Thẻ hướng dẫn nhanh**:
  1. *Giữ chuột phải + Cuộn lên*: Mở bảng lệnh phím tắt.
  2. *Giữ chuột phải + Vẽ cử chỉ*: Thao tác nhanh chuyển/đóng tab.
  3. *Khay hệ thống (System Tray)*: Nhấp chuột phải vào icon khay để vào Cài đặt.
- Tùy chọn checkbox *"Không hiển thị lại màn hình này"* và nút hành động chính *"Bắt đầu sử dụng"*.

### 3.6 Trang Landing Page (`website/index.html`)
- Chuyển toàn bộ CSS Custom Properties sang thang màu Zinc (`--bg: #09090b`, `--surface: #121214`, `--border: #27272a`, `--text: #f4f4f5`, `--muted: #a1a1aa`).
- Đạt độ tương phản màu chuẩn **WCAG AA 5.8:1**.
- Chuẩn hóa nút CTA chính sang Brand Blue (`#0078d4`), loại bỏ hoàn toàn viền rực neon.
- Hỗ trợ trợ năng với media query `@media (prefers-reduced-motion: reduce)`.

---

## 4. Công cụ Xem trước Giao diện (Preview Tooling)

Để kiểm tra giao diện mà không phải khởi chạy toàn bộ mouse hook nền hay phụ thuộc vào cử chỉ chuột:
- **Batch script**: [preview_ui.bat](file:///c:/dev/Mousehotkey/preview_ui.bat)
- **Python script**: [src/preview_ui.py](file:///c:/dev/Mousehotkey/src/preview_ui.py)
- **Menu chọn trực tiếp**:
  1. Mở Cửa sổ Cài đặt (Settings Window - Tab Cử chỉ & Playground).
  2. Mở Bảng lệnh (Command Palette giả lập).
  3. Mở Màn hình Chào mừng (Welcome Onboarding Window).
  4. Mở Tất cả để kiểm tra đồng bộ.

---

## 5. Quy tắc & Bất biến Khi Mở rộng UI (UI Developer Guidelines)

1. **Tuân thủ Giới hạn Kích thước File**:
   - Mọi file UI mới hoặc cập nhật bắt buộc $\le 250$ dòng code (ngưỡng cứng theo CLAUDE.md & PRD).
   - Tách riêng dialog (`folder_editor_dialog.py`, `sequence_step_dialogs.py`) và renderer (`panel_item_renderer.py`).
2. **Quy tắc Single Root**:
   - Toàn bộ ứng dụng duy nhất một thể hiện `tk.Tk()` trong `panel_window.py`. Mọi cửa sổ khác bắt buộc dùng `tk.Toplevel(root)`.
3. **Quy tắc Focus & Destroy**:
   - Luôn gọi `SetForegroundWindow(hwnd)` TRƯỚC khi `hide()` hoặc `destroy()` cửa sổ panel để bảo đảm phím tắt SendInput gửi đúng cửa sổ đích.
4. **Không Thử Nghiệm Bằng Browser**:
   - Tuyệt đối tuân thủ quy tắc toàn cục không dùng browser automation để kiểm thử UI. Sử dụng render test tĩnh hoặc headless mockups.
