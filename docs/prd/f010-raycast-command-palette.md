# PRD: F-010 Raycast & Linear Command Palette Modern UI

## 1. Executive Summary
Hiện đại hóa toàn diện giao diện Shortcut Panel của RightWheel theo phong cách **Raycast & Linear Command Palette** (tối giản cao cấp, Zinc dark theme, kbd badges dạng phím cơ sắc nét, thanh trượt Volume inline trực tiếp, phân cấp nội dung chuyên nghiệp) trên nền tảng 100% native Tkinter, khởi động dưới 30ms, tuân thủ giới hạn file ≤ 250 dòng.

---

## 2. User Stories & Acceptance Criteria

### US-028: Raycast Visual Aesthetic & Kbd Badges
- **AC 1.1**: Nền chính sử dụng bảng màu Zinc Dark: nền window `#121214`, thẻ item mặc định `#18181b`, hover/selected item `#27272a` với viền trái accent bar xanh dương (`#0078d4`) hoặc viền sáng.
- **AC 1.2**: Các phím số 0-9 được hiển thị dạng kbd badge nổi (`kbd-style`), nền `#27272a`, viền `#3f3f46`, font `Segoe UI` 9 bold chữ trắng.
- **AC 1.3**: Tiêu đề breadcrumb và tên profile hiển thị trang nhã, không thô cứng.

### US-029: Inline Interactive Volume Slider
- **AC 2.1**: Dòng Volume trên Shortcut Panel tích hợp thanh trượt tiến trình (track `#27272a`, filled `#0078d4`, bo tròn) và nhãn âm lượng thực tế (`XX%`).
- **AC 2.2**: Icon loa động (`🔇`, `🔈`, `🔉`, `🔊`) tự động phản ánh mức âm lượng thực tế của Windows.
- **AC 2.3**: Người dùng có thể cuộn chuột trực tiếp trên dòng Volume hoặc click/drag trên thanh trượt để điều chỉnh âm lượng Windows ngay lập tức mà không cần chuyển sang popup riêng.

### US-030: Content Categorization & Navigation Footer
- **AC 3.1**: Có vạch phân cách danh mục nhẹ nhàng giữa các nhóm shortcut ứng dụng và các tác vụ hệ thống (Settings, Pause).
- **AC 3.2**: Footer nhỏ gọn ở đáy panel hiển thị gợi ý phím điều hướng (`◈ Profile • ↑↓ Navigate • Enter Select • Esc Close`).
- **AC 3.3**: Toàn bộ thao tác chuột (click, wheel) và phím (0-9, Up, Down, Enter, Esc, BackSpace) hoạt động trơn tru không có độ trễ.

---

## 3. Non-Functional Requirements
- **Performance**: Thời gian khởi tạo/render giao diện panel < 30ms khi cuộn chuột mở panel.
- **Memory footprint**: Tiêu thụ thêm RAM không đáng kể (< 3MB).
- **System Lock**: Tất cả các file mã nguồn mới/sửa đổi phải ≤ 250 dòng.
- **Stability**: Không gây xung đột với single Tkinter root mainloop và máy trạng thái RMB mouse hook.
