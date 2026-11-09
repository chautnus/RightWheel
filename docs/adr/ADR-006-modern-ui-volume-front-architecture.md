# ADR-006: Kiến trúc Tái thiết kế Giao diện Modern Minimalist & Tích hợp Quản lý Volume Phía trước

## Trạng thái
Accepted

## Ngữ cảnh
F-006 đã giới thiệu tính năng điều khiển âm lượng hệ thống và tab tra cứu phím tắt. Tuy nhiên:
1. Giao diện Shortcut Panel và Settings Window vẫn sử dụng các thành phần Tkinter cổ điển (`ttk.Notebook` thanh tab ngang, danh sách Listbox thô, màu tối cơ bản).
2. Chức năng Volume bị giấu sâu trong thư mục `📁 App`, đòi hỏi 2 bước cuộn/chọn mới kích hoạt được.
3. Người dùng yêu cầu hiện đại hóa toàn diện giao diện theo phong cách Modern Dark Minimalist (Fluent / Raycast) và đưa điều khiển volume ra phía trước.

## Các quyết định kiến trúc

### 1. Tích hợp Quick Volume Bar trên đỉnh Shortcut Panel (`panel_window.py`)
- **Vị trí**: Nằm ngay dưới Profile badge (nếu có) và trên danh sách shortcut items.
- **Thành phần**: Canvas mini hiển thị icon loa động, thanh trượt phần trăm âm lượng bo góc, và nhãn mức âm lượng hiện tại.
- **Tương tác**:
  - Khi con trỏ chuột hover vào khu vực Volume Bar, sự kiện `<MouseWheel>` được bind trực tiếp để thay đổi volume ngay tại chỗ qua `send_volume_step()`.
  - Giữ nguyên toàn bộ State Machine của `mouse_mapper_logic.py` (LOCKED) và UX Flow của Shortcut Panel (Rule 3). Phím số 0-9 vẫn kích hoạt item tương ứng mà không bị tranh chấp.
  - Tùy chọn ẩn/hiện Volume Bar được điều khiển qua cấu hình `show_panel_volume`.

### 2. Capsule Volume Overlay HUD (`volume_overlay.py`)
- **Tạo hình**: Thay thế khung chữ nhật vuông vức bằng Canvas vẽ dạng viên thuốc Capsule (bo góc tròn 2 đầu hoặc bo góc mềm 12px), nền `#18181b`, viền mỏng `#27272a`.
- **Icon động**: Tính toán icon dựa trên `_level`:
  - `_level == 0.0`: 🔇
  - `0.0 < _level <= 0.33`: 🔈
  - `0.33 < _level <= 0.66`: 🔉
  - `0.66 < _level <= 1.0`: 🔊
- **Nhãn số**: Bổ sung hiển thị phần trăm rõ ràng (ví dụ: `50%`) với font Segoe UI Variable / Segoe UI 10pt bold màu trắng.
- **Thời gian tự ẩn**: Giữ nguyên cơ chế tự ẩn 3000ms an toàn trên Tkinter thread và hủy backdrop khi click ra ngoài.

### 3. Tái cấu trúc Settings Window theo phong cách Sidebar Navigation (`settings_window.py`)
- **Bố cục**: Thay thế `ttk.Notebook` ngang bằng bố cục 2 cột hiện đại:
  - Cột trái (Sidebar 170px): Nền `#121214`, danh sách danh mục có icon (⚙ General & Volume, ⌨ Shortcuts, 🖱 Gestures, 📖 Reference, 🔑 License), có vạch chỉ báo active (accent pill).
  - Cột phải: Content area nền `#18181b` hiển thị card tương ứng.
- **Phân rã module (Chống vi phạm SYSTEM LOCK 250 dòng)**:
  - Tạo mới `general_volume_tab.py` (quản lý Startup, Language, Volume Step Size, và Toggle Volume Bar trên Panel).
  - Giữ `settings_window.py` đóng vai trò Controller/Shell thuần túy, đảm bảo kích thước file luôn dưới 180 dòng.

### 4. Cấu hình & Dữ liệu (`config_service.py`)
- Bổ sung các trường cấu hình mới với giá trị mặc định an toàn:
  - `volume_step`: `0.05` (5%)
  - `show_panel_volume`: `True`
- Cập nhật `_DEFAULT`: Đưa mục `🔊 Volume Control` ra root của danh sách `default` để người dùng thấy ngay khi cài mới.

## Hậu quả & Đánh giá tác động
- **Tích cực**:
  - Giao diện thẩm mỹ vượt trội, phong cách Modern Dark Minimalist chuyên nghiệp.
  - Tiếp cận tính năng Volume tức thì ngay trên Shortcut Panel.
  - Tuân thủ 100% các quy tắc an toàn (SYSTEM LOCK, Tkinter single-root, Rule 4b).
- **Rủi ro & Giảm thiểu**:
  - Canvas custom widgets cần tính toán tọa độ chính xác để không bị lệch pixel trên các màn hình DPI khác nhau. Đã sử dụng kích thước cố định và tỷ lệ phần trăm chuẩn hóa.
