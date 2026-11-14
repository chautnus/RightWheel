# Memory: Architecture & Implementation Notes for F-016 (Intent-Based Action Assistant & Reference Tab Integration)

## Core Architecture Decisions
- **Porting Intent Catalog từ dự án Touchpad gesture (commit 31b968c)**:
  - Chuyển đổi dữ liệu tham chiếu tĩnh (Reference) thành hệ thống Intent Catalog sống, hỗ trợ tìm kiếm theo mục đích tự nhiên bằng cả tiếng Việt và tiếng Anh.
  - Tách đôi file để tuân thủ triệt để quy tắc SYSTEM LOCK $\le 250$ dòng:
    1. `src/features/shortcut_panel/services/intent_service.py` (102 dòng): Chứa `IntentItem`, `IntentService`, cơ chế `_normalize_str` khử dấu tiếng Việt (`đ/d`, diacritics).
    2. `src/features/shortcut_panel/services/intent_catalog_data.py` (200 dòng): Lưu trữ danh mục hơn 30 tác vụ phổ biến thuộc các nhóm Hệ thống, Cửa sổ, Trình duyệt, File Explorer.
  - Hộp thoại trợ lý `src/features/shortcut_panel/ui/intent_picker_dialog.py` (194 dòng): Modal UI kế thừa bảng màu Zinc Dark (`theme.*`), hỗ trợ gõ tìm kiếm tức thì, lọc theo Category Pills, xem trước mô tả và nút "Chọn phím này" / "Nhập thủ công...".
- **Tích hợp vào DefaultTab (Thêm Phím tắt)**:
  - Trong `src/features/shortcut_panel/ui/default_tab_crud.py` (246 dòng, $\le 250$): Hàm `_add_shortcut()` khi được kích hoạt sẽ mở `IntentPickerDialog.ask()`.
  - Nếu người dùng chọn một mục trong catalog, tự động gán tên hiển thị và tổ hợp phím chuẩn.
  - Nếu người dùng chọn "Nhập thủ công...", hệ thống fallback về modal nhập tên + `KeyRecorderDialog` truyền thống mà không bị gián đoạn.
- **Nâng cấp ReferenceTab thành Thư viện Phím tắt Tương tác (1-Click Import)**:
  - Trong `src/features/shortcut_panel/ui/reference_tab.py` (191 dòng, $\le 250$): Bổ sung thanh điều khiển dưới đáy với nút `[ + Thêm vào Phím tắt của tôi ]` và sự kiện double-click `<Double-1>` trên bảng Treeview.
  - Người dùng có thể duyệt bảng tham chiếu phím tắt hệ thống / trình duyệt và nhấp đúp hoặc bấm nút để tự động lưu trực tiếp vào cấu hình `config_service` của RightWheel kèm nhãn thông báo phản hồi trực quan.
- **Kiểm thử**:
  - `tests/test_intent_service.py`: 5 unit tests kiểm tra chuẩn hóa tiếng Việt, tìm kiếm mờ theo intent id/keywords, tìm kiếm theo nhóm và giả lập lưu cấu hình trong môi trường headless. Toàn bộ 10/10 tests trên dự án pass 100%.
  - PyInstaller: Đóng gói lại thành công `dist/RightWheel.exe` (21.3 MB).
