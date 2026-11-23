# PRD: f020-gesture-order-and-tkinter-popup-redesign

## 1. Overview
Khắc phục triệt để lỗi không lưu phím khi gán từ Reference/Intent, bổ sung nút 1-click import trên WebView2 ReferenceTab, chuẩn hóa 16 cử chỉ vẽ theo nét đầu tiên (tối đa 2 đoạn, không hình khối) và thiết kế lại Popup Tkinter với góc bo tròn mềm mại và highlight hàng được chọn màu xanh dương nổi bật.

## 2. Requirements & User Stories
- **US-059 (Sửa lỗi gán phím Reference & Intent)**:
  - Khi người dùng nhấp đúp hoặc bấm "+ Thêm vào Phím tắt của tôi" trong tab Reference, hoặc chọn phím tắt từ modal Trợ lý Intent, phím tắt phải được lưu vĩnh viễn vào `profiles.json` và `shortcuts.json`, lập tức hiển thị trên Bảng lệnh phím tắt.
  - Trên tab Reference của WebView2 V3, người dùng có nút 1-click để thêm phím tham chiếu thẳng vào hồ sơ lệnh đang mở.
- **US-060 (Chuẩn hoá thứ tự cử chỉ theo nét đầu)**:
  - Danh sách cử chỉ được sắp xếp rõ ràng theo nét xuất phát đầu tiên: Lên (`U`), Xuống (`D`), Trái (`L`), Phải (`R`) với các hướng con: đơn, ngược chiều, rẽ phải, rẽ trái.
  - Giới hạn tối đa 2 đoạn, loại bỏ hoàn toàn các hình tam giác, hình vuông, vòng tròn, chữ Z, chữ N.
- **US-061 (Popup Tkinter bo góc & highlight xanh)**:
  - Cửa sổ popup ngoài Desktop có góc bo tròn mịn màng (bán kính 14px) bằng Win32 SetWindowRgn và DWM corner preference.
  - Hàng được chọn được phủ màu xanh dương `#0078d4`, thanh nhấn `#38bdf8`, chữ trắng rõ nét.

## 3. Acceptance Criteria
1. Thêm phím từ `ReferenceTab` hoặc `IntentPickerDialog` trong Tkinter được lưu thành công vào cả `profiles.json` và `shortcuts.json` (xác thực bằng test tự động).
2. `ReferenceTab.tsx` trong WebView2 có nút 1-click thêm phím vào hồ sơ lệnh.
3. `GestureEditorModal.tsx` và `sort_gestures()` chỉ còn 16 cử chỉ chuẩn 1-2 đoạn, nhóm theo U, D, L, R.
4. `panel_window.py` cắt góc cửa sổ popup bo tròn 14px.
5. `panel_item_renderer.py` hiển thị hàng đang chọn màu xanh dương `#0078d4`.
6. Toàn bộ test suite `pytest` pass 100%.
7. Bản build `dist/RightWheel.exe` chạy độc lập ổn định.
