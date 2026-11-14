"""Default intent action catalog data for RightWheel."""
from __future__ import annotations

from .intent_service import IntentItem

INTENT_CATALOG: list[IntentItem] = [
    # ── Windows System Actions ────────────────────────────────────────────────
    IntentItem(
        "task_manager", "Mở Trình quản lý tác vụ (Task Manager)", "Open Task Manager",
        "ctrl+shift+esc", "Hệ thống",
        ["task manager", "taskmgr", "tác vụ", "tiến trình", "cpu", "ram", "kill", "đơ máy", "quản lý ứng dụng"],
        "Mở nhanh Task Manager để kiểm tra hiệu năng hoặc tắt ứng dụng bị treo."
    ),
    IntentItem(
        "snip_screenshot", "Chụp ảnh màn hình (Snip Tool)", "Take Screenshot (Snip & Sketch)",
        "win+shift+s", "Hệ thống",
        ["chụp màn hình", "screenshot", "snip", "cắt ảnh", "chụp ảnh", "capture", "vùng chọn", "screen"],
        "Cắt và chụp ảnh một vùng hoặc toàn bộ màn hình Windows."
    ),
    IntentItem(
        "clipboard_history", "Lịch sử bộ nhớ tạm (Clipboard History)", "Clipboard History",
        "win+v", "Hệ thống",
        ["clipboard", "lịch sử copy", "paste history", "dán", "sao chép nhiều lần", "nhớ tạm"],
        "Mở bảng lịch sử các nội dung đã sao chép gần đây."
    ),
    IntentItem(
        "show_desktop", "Hiện / Ẩn màn hình chính (Desktop)", "Show / Hide Desktop",
        "win+d", "Hệ thống",
        ["desktop", "màn hình chính", "ẩn hết", "thu nhỏ tất cả", "ra desktop"],
        "Thu nhỏ lập tức toàn bộ cửa sổ để nhìn thấy màn hình Desktop."
    ),
    IntentItem(
        "run_dialog", "Mở hộp thoại Chạy lệnh (Run)", "Open Run Dialog",
        "win+r", "Hệ thống",
        ["run", "hộp thoại run", "chạy lệnh", "cmd", "mở run"],
        "Mở cửa sổ Run để chạy nhanh các lệnh Windows hoặc mở ứng dụng."
    ),
    IntentItem(
        "windows_settings", "Mở Cài đặt Windows (Settings)", "Open Windows Settings",
        "win+i", "Hệ thống",
        ["settings", "cài đặt windows", "tùy chọn hệ thống", "cấu hình", "options"],
        "Mở trang cài đặt chính của hệ điều hành Windows."
    ),
    IntentItem(
        "lock_pc", "Khóa máy tính (Lock Workstation)", "Lock Computer",
        "win+l", "Hệ thống",
        ["lock", "khóa máy", "khóa màn hình", "rời máy", "bảo mật"],
        "Khóa màn hình máy tính ngay lập tức khi bạn rời khỏi bàn làm việc."
    ),
    IntentItem(
        "file_explorer", "Mở trình duyệt tệp (File Explorer)", "Open File Explorer",
        "win+e", "Hệ thống",
        ["explorer", "file explorer", "thư mục", "tệp tin", "my computer", "this pc", "ổ đĩa"],
        "Mở cửa sổ quản lý tệp và thư mục của Windows."
    ),
    IntentItem(
        "emoji_picker", "Bảng biểu tượng cảm xúc (Emoji Picker)", "Open Emoji Picker",
        "win+.", "Hệ thống",
        ["emoji", "biểu tượng", "icon", "mặt cười", "ký tự đặc biệt"],
        "Chèn nhanh biểu tượng cảm xúc emoji hoặc ký hiệu đặc biệt."
    ),
    IntentItem(
        "quick_settings", "Bảng điều khiển nhanh Wifi/Bluetooth", "Open Quick Settings",
        "win+a", "Hệ thống",
        ["quick settings", "wifi", "bluetooth", "âm lượng", "độ sáng", "action center"],
        "Mở thanh điều khiển nhanh âm lượng, độ sáng, kết nối mạng."
    ),

    # ── Window Management Actions ─────────────────────────────────────────────
    IntentItem(
        "close_window", "Đóng cửa sổ hiện tại (Close Window)", "Close Current Window",
        "alt+f4", "Cửa sổ",
        ["close window", "đóng cửa sổ", "tắt ứng dụng", "thoát app", "exit", "quit"],
        "Đóng ngay lập tức cửa sổ ứng dụng đang hoạt động."
    ),
    IntentItem(
        "maximize_window", "Phóng to cửa sổ tối đa (Maximize)", "Maximize Window",
        "win+up", "Cửa sổ",
        ["maximize", "phóng to", "toàn màn hình", "mở rộng cửa sổ"],
        "Phóng to cửa sổ hiện tại chiếm toàn bộ màn hình."
    ),
    IntentItem(
        "minimize_window", "Thu nhỏ cửa sổ xuống Taskbar (Minimize)", "Minimize Window",
        "win+down", "Cửa sổ",
        ["minimize", "thu nhỏ", "hạ cửa sổ", "ẩn xuống taskbar"],
        "Thu nhỏ cửa sổ hiện tại xuống thanh tác vụ."
    ),
    IntentItem(
        "snap_left", "Căn cửa sổ sang nửa màn hình bên Trái", "Snap Window Left",
        "win+left", "Cửa sổ",
        ["snap left", "chia nửa trái", "căn trái", "bên trái", "chia đôi màn hình"],
        "Căn gọn cửa sổ hiện tại vào nửa bên trái của màn hình."
    ),
    IntentItem(
        "snap_right", "Căn cửa sổ sang nửa màn hình bên Phải", "Snap Window Right",
        "win+right", "Cửa sổ",
        ["snap right", "chia nửa phải", "căn phải", "bên phải", "chia đôi màn hình"],
        "Căn gọn cửa sổ hiện tại vào nửa bên phải của màn hình."
    ),
    IntentItem(
        "task_view", "Xem các ứng dụng đang mở (Task View)", "Task View / Recent Windows",
        "win+tab", "Cửa sổ",
        ["task view", "recent tab", "chuyển cửa sổ", "xem tất cả cửa sổ", "virtual desktop"],
        "Xem toàn bộ các cửa sổ và desktop ảo đang mở."
    ),
    IntentItem(
        "alt_tab_switch", "Chuyển đổi nhanh giữa các ứng dụng", "Switch Windows (Alt+Tab)",
        "alt+tab", "Cửa sổ",
        ["alt tab", "đổi ứng dụng", "chuyển app", "qua lại cửa sổ"],
        "Chuyển đổi nhanh sang cửa sổ ứng dụng vừa sử dụng trước đó."
    ),

    # ── Web Browser Actions ───────────────────────────────────────────────────
    IntentItem(
        "new_tab", "Mở Tab trình duyệt mới (New Tab)", "Open New Tab",
        "ctrl+t", "Trình duyệt",
        ["new tab", "tab mới", "thêm tab", "mở tab", "trang mới"],
        "Mở một tab mới trên trình duyệt web (Chrome, Edge, Firefox...)."
    ),
    IntentItem(
        "close_tab", "Đóng Tab hiện tại (Close Tab)", "Close Tab",
        "ctrl+w", "Trình duyệt",
        ["close tab", "đóng tab", "tắt tab", "bỏ tab", "xóa tab"],
        "Đóng tab đang xem trên trình duyệt web."
    ),
    IntentItem(
        "next_tab", "Chuyển sang Tab kế tiếp (Next Tab)", "Next Tab",
        "ctrl+tab", "Trình duyệt",
        ["next tab", "tab tiếp theo", "đổi tab", "tab sau", "chuyển tab"],
        "Duyệt sang tab kế tiếp trong cùng một cửa sổ trình duyệt."
    ),
    IntentItem(
        "prev_tab", "Quay lại Tab trước đó (Previous Tab)", "Previous Tab",
        "ctrl+shift+tab", "Trình duyệt",
        ["prev tab", "previous tab", "tab trước", "lùi tab"],
        "Quay trở lại tab liền kề phía trước."
    ),
    IntentItem(
        "reopen_closed_tab", "Khôi phục Tab vừa đóng (Reopen Tab)", "Reopen Closed Tab",
        "ctrl+shift+t", "Trình duyệt",
        ["reopen tab", "mở lại tab", "khôi phục tab", "vừa tắt", "tab đóng nhầm"],
        "Khôi phục lại tab bạn vừa vô tình đóng trên trình duyệt."
    ),
    IntentItem(
        "reload_page", "Tải lại trang web (Reload / Refresh)", "Reload Page",
        "ctrl+r", "Trình duyệt",
        ["reload", "refresh", "f5", "tải lại", "làm mới", "cập nhật trang"],
        "Tải lại nội dung trang web hiện tại."
    ),
    IntentItem(
        "hard_reload_page", "Tải lại xóa bộ nhớ đệm (Hard Reload)", "Hard Reload Page",
        "ctrl+shift+r", "Trình duyệt",
        ["hard reload", "xóa cache", "tải lại sạch", "ctrl f5"],
        "Tải lại trang web và làm mới toàn bộ tài nguyên không dùng cache."
    ),
    IntentItem(
        "focus_address_bar", "Đặt con trỏ vào thanh địa chỉ URL", "Focus Address Bar",
        "ctrl+l", "Trình duyệt",
        ["url", "thanh địa chỉ", "nhập web", "gõ link", "address bar"],
        "Bôi đen thanh địa chỉ để sẵn sàng gõ đường link hoặc tìm kiếm."
    ),
    IntentItem(
        "bookmark_page", "Lưu trang vào Dấu trang (Bookmark)", "Bookmark Current Page",
        "ctrl+d", "Trình duyệt",
        ["bookmark", "dấu trang", "lưu trang", "yêu thích", "favorite"],
        "Thêm trang web đang xem vào danh sách yêu thích."
    ),
    IntentItem(
        "browser_history", "Mở Lịch sử duyệt web (History)", "Open Browsing History",
        "ctrl+h", "Trình duyệt",
        ["history", "lịch sử", "lịch sử web", "các trang đã xem"],
        "Mở bảng tra cứu lịch sử các trang web đã truy cập."
    ),
    IntentItem(
        "incognito_window", "Mở cửa sổ Ẩn danh mới (Incognito)", "Open Incognito Window",
        "ctrl+shift+n", "Trình duyệt",
        ["incognito", "ẩn danh", "riêng tư", "private window"],
        "Mở cửa sổ duyệt web riêng tư không lưu lại lịch sử."
    ),

    # ── File Explorer Actions ─────────────────────────────────────────────────
    IntentItem(
        "new_folder", "Tạo thư mục mới (New Folder)", "Create New Folder",
        "ctrl+shift+n", "File Explorer",
        ["new folder", "tạo thư mục", "folder mới", "tạo folder"],
        "Tạo nhanh một thư mục mới trong thư mục hiện tại."
    ),
    IntentItem(
        "rename_file", "Đổi tên tệp hoặc thư mục (Rename)", "Rename File / Folder",
        "f2", "File Explorer",
        ["rename", "đổi tên", "sửa tên", "f2"],
        "Bắt đầu đổi tên tệp hoặc thư mục đang được chọn."
    ),
    IntentItem(
        "find_in_page", "Tìm kiếm nội dung trên trang (Find)", "Find on Page",
        "ctrl+f", "File Explorer",
        ["find", "tìm kiếm", "tìm từ", "search page", "tra cứu"],
        "Mở thanh tìm kiếm từ khóa trên văn bản hoặc trang web."
    ),
]
