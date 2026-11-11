# PRD: F-011 Fix Cursor Position, Left Click Z-Order & Remove Emoticons

## 1. Problem Statement
- Khi mở Shortcut Panel, cửa sổ xuất hiện xa vị trí chuột (bị đẩy lên đỉnh màn hình do căn giữa dọc khi chiều cao panel tăng).
- Chuột trái (Left Click) bị vô hiệu hóa hoàn toàn trên panel do `self._overlay` chiếm quyền z-order cao hơn `self._win`.
- Các emoticon / emoji xuất hiện ở nhiều nơi (menu items, volume icon, settings sidebar, default presets) không đúng yêu cầu tối giản.

## 2. Requirements & Acceptance Criteria

### AC 1: Vị trí xuất hiện chính xác tại con trỏ chuột
- Menu nổi xuất hiện với góc trên-trái bám sát con trỏ chuột `(px, py)` (có margin bù 10px để con trỏ chuột nằm ngay bên trong vùng menu).
- Tự động giới hạn (clamp) trong màn hình nếu con trỏ ở sát mép phải hoặc mép dưới.

### AC 2: Khôi phục hoạt động của chuột trái (Left Click)
- `self._win` phải luôn nằm trên `self._overlay` trong thứ tự z-order của Windows.
- Click chuột trái vào bất kỳ item nào lập tức chọn và kích hoạt shortcut đó.
- Click chuột trái và kéo trên thanh Volume cập nhật âm lượng Windows mượt mà.

### AC 3: Loại bỏ toàn bộ Emoticon
- Không còn bất kỳ emoji nào trong `panel_item_renderer.py` (loại bỏ `📁`, `🚀`, `🌐`, `⚡`, `⌨`, `💻`).
- Không còn emoji loa trong `panel_volume_widget.py` (`🔊`, `🔇`,...).
- Không còn emoji trong navigation của `settings_window.py` (`⚙`, `⌨`, `◈`, `🖱`, `📖`, `🔑`, `✓`).
- Nhãn shortcut tự động làm sạch emoji nếu chuỗi có chứa ký tự emoji từ trước.
