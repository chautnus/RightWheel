# Context: f020-gesture-order-and-tkinter-popup-redesign

## 1. Problem Description & Root Causes
- **Bug: Gán phím từ Reference / Intent không hoạt động**:
  - Khi người dùng tìm phím tắt trong tab Reference (`reference_tab.py:175`) hoặc qua Trợ lý Intent (`intent_picker_dialog.py` / `default_tab_crud.py:31`) rồi bấm "+ Thêm vào Phím tắt", hệ thống báo thành công nhưng phím tắt không hề xuất hiện trên panel hoặc bị mất ngay sau đó.
  - **Bằng chứng điều tra thực nghiệm (Root Cause)**:
    1. Khi tải cấu hình bằng `config_service.load()`, dữ liệu Schema v4 `profiles.json` được nạp và `data["default"]` là một danh sách sao chép độc lập với `data["profiles"][0]["commands"]`.
    2. Hàm thêm phím tắt chỉ `append()` vào `data["default"]`.
    3. Khi gọi `config_service.save(data)`, vì `data.get("version") == 4`, hệ thống chuyển tiếp toàn bộ sang `save_unified_profiles(data)`.
    4. `save_unified_profiles` lưu `doc["profiles"]` vào `profiles.json` và sau đó lấy `global_prof.get("commands", [])` để ghi đè ngược lại `shortcuts.json`.
    5. Do `global_prof["commands"]` không hề được cập nhật, phần tử mới thêm vào `data["default"]` bị xoá sạch hoàn toàn!
    6. Ngoài ra, giao diện WebView2 V3 (`ReferenceTab.tsx`) hiện chỉ là danh sách tĩnh, chưa trang bị nút 1-click "+ Thêm vào Lệnh" để người dùng gán trực tiếp.
- **Sắp xếp cử chỉ theo nét đầu & giới hạn 2 đoạn**:
  - `GestureEditorModal.tsx` và danh sách cử chỉ hiện có cả nét 3 đoạn và hình vẽ khối (`CIRCLE`, `SQUARE`, `TRIANGLE`...).
  - Cần sắp xếp theo 4 nhóm nét đầu (U, D, L, R) với phân cấp: đơn -> ngược chiều -> rẽ phải -> rẽ trái.
  - Giới hạn tối đa 2 đoạn, loại bỏ hoàn toàn các hình phức tạp.
- **Thiết kế lại Popup Tkinter**:
  - Popup Raycast ngoài Desktop hiện có góc vuông sắc cạnh và hàng đang chọn có màu xám đậm (`#27272a`).
  - Cần bo tròn góc cửa sổ bằng Win32 `CreateRoundRectRgn` / `SetWindowRgn` và highlight hàng đang chọn bằng màu xanh dương nổi bật (`#0078d4`), thanh nhấn cyan (`#38bdf8`) và chữ trắng (`#ffffff`).

## 2. Solution Architecture
1. **Fix đồng bộ `save()` trong `config_service.py`**:
   - Trong `src/features/shortcut_panel/services/config_service.py:save(data)`:
     Tự động đồng bộ `data["default"]` (hoặc `data["shortcuts"]`) vào `global_prof["commands"]` và `global_prof["shortcuts"]` trước khi lưu vào `profiles.json` và `shortcuts.json`.
2. **Thêm nút 1-click "+ Thêm vào Lệnh" trong WebView2 `ReferenceTab.tsx`**:
   - Thêm nút hành động nhanh trên mỗi mục tham chiếu, gọi `onAddCommand` để nối phím vào hồ sơ lệnh đang hoạt động kèm thông báo toast phản hồi.
3. **Chuẩn hoá danh sách 16 cử chỉ vẽ**:
   - Trong `GestureEditorModal.tsx` và `src/core/config_service.py:sort_gestures`:
     Áp dụng bảng xếp hạng `_DRAW_GESTURE_ORDER` phân nhóm theo nét đầu:
     - U: `U`, `U_D`, `U_R`, `U_L`
     - D: `D`, `D_U`, `D_R`, `D_L`
     - L: `L`, `L_R`, `L_U`, `L_D`
     - R: `R`, `R_L`, `R_U`, `R_D`
4. **Bo tròn góc & Highlight xanh cho Popup Tkinter**:
   - `panel_window.py`: Gọi `_apply_rounded_corners()` (GDI Round Rect Region + DWM Rounded Corner).
   - `panel_item_renderer.py`: Cập nhật `_BG_SEL = "#0078d4"`, `_ACCENT_BAR = "#38bdf8"`, `_FG_SEL = "#ffffff"`, padding `padx=6, pady=2`.
