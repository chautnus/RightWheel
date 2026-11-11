# ADR-011: In-Place Selection Highlight and Volume Subsystem Removal

## Status
Accepted

## Context
1. **Hiện tượng giật hình (Render Flicker) khi điều hướng Panel**: Trong `panel_window.py`, mỗi khi người dùng cuộn chuột (`navigate()`) hoặc bấm phím số/mũi tên, `panel_logic.py` kích hoạt callback `on_update`. Hàm xử lý `_do_update()` hiện tại gọi `self._render()` vô điều kiện cho mọi lần cập nhật. Trong `_render()`, toàn bộ widget con của `self._win` bị hủy (`for w in self._win.winfo_children(): w.destroy()`) rồi xây lại từ đầu: banner paused, profile banner, breadcrumb, inline volume widget, toàn bộ danh sách shortcut items qua `PanelItemRenderer`, và footer status bar. Quá trình destroy và rebuild liên tục này theo tần số cuộn chuột gây hiện tượng chớp nháy (flicker) nghiêm trọng, tốn CPU và giảm chất lượng trải nghiệm người dùng.
2. **Thiếu cơ chế cập nhật trạng thái tại chỗ (In-Place Update)**: `PanelItemRenderer` hiện tại không lưu trữ tham chiếu (reference) tới các widget hàng (`tk.Frame`, `tk.Label`) sau khi tạo, buộc phải xóa sạch container và render lại toàn bộ danh sách dù chỉ có chỉ số lựa chọn `index` thay đổi.
3. **Dư thừa phân hệ Volume**: Thành phần Inline Volume Slider Card trên đỉnh Shortcut Panel và toàn bộ hệ thống Volume Overlay / Service gây phức tạp hóa layout, không còn phù hợp với định hướng công cụ tập trung thuần túy vào shortcut launcher theo PRD đã chốt (US-034..038).

## Decision

1. **Bộ nhớ tạm Widget Reference và Cập nhật Highlight Tại Chỗ trong `PanelItemRenderer`**:
   - `PanelItemRenderer` lưu danh sách tham chiếu cấu trúc của từng hàng vào `self._row_views: list[dict[str, tk.Widget]]` (lưu trữ `row`, `acc_bar`, `badge`, `title`, `sub`).
   - Tách biệt logic áp dụng giao diện: bổ sung hàm nội bộ `_apply_row_style(index: int, sel: bool)` để cấu hình màu sắc (`bg`, `fg`, `highlightbackground`), font chữ (`Segoe UI 10 bold` vs regular) và thanh chỉ thị `acc_bar` (`_ACCENT_BAR` vs `bg`) cho từng hàng mà không thay đổi cấu trúc widget.
   - Bổ sung phương thức `update_selection(old_index: int, new_index: int)`: chỉ cập nhật style của đúng 2 hàng (hàng cũ bỏ chọn, hàng mới được chọn). Khi `old_index` và `new_index` nằm trong giới hạn danh sách, thao tác diễn ra trong sub-millisecond, triệt tiêu 100% hiện tượng chớp nháy.

2. **Cơ chế phân biệt Re-render cấu trúc và Cập nhật Highlight trong `PanelWindow` (State Snapshot Diffing)**:
   - **So sánh 2 phương án**:
     - *Option A (State Snapshot Diffing trong `PanelWindow`)*: `PanelLogic` giữ nguyên giao diện callback `on_update`. `PanelWindow` lưu các snapshot trạng thái cuối cùng (`_last_items`, `_last_breadcrumb`, `_last_profile`, `_last_paused`, `_last_index`). Trong `_do_update()`, so sánh snapshot để quyết định gọi full `_render()` hay chỉ gọi `update_selection()`.
     - *Option B (Phân tách 2 sự kiện trong `PanelLogic`)*: `PanelLogic` bổ sung callback riêng `on_selection_change` (cho `navigate`, `select_at`) và `on_structure_change` (cho folder navigation, reload, pause).
   - **Lựa chọn**: Chọn **Option A (State Snapshot Diffing trong `PanelWindow`)**.
     - *Lý do & Trade-off*:
       - Giữ nguyên tính độc lập của Domain/Logic Layer: `PanelLogic` chỉ quản lý trạng thái máy điều hướng (`NavState`), không phụ thuộc vào chi tiết kỹ thuật hiển thị của GUI toolkit. Giao diện callback `on_update` được bảo toàn nguyên vẹn, không làm vỡ các unit test hiện có.
       - Tầng UI tự chủ: `PanelWindow` nhận diện chính xác khi nào cấu trúc thực sự đổi (`st.items is not self._last_items` hoặc `st.breadcrumb != self._last_breadcrumb` hoặc `profile != self._last_profile` hoặc `paused != self._last_paused` hoặc `self._item_renderer is None`) để kích hoạt full `_render()`.
       - Khi cấu trúc không đổi và chỉ `st.index != self._last_index`: gọi thẳng `self._item_renderer.update_selection(self._last_index, st.index)` và cập nhật `self._last_index = st.index`.

3. **Loại bỏ Phân hệ Volume và Tái cấu trúc Layout Phẳng**:
   - Gỡ bỏ hoàn toàn `PanelVolumeWidget` trên đỉnh danh sách items trong `panel_window.py._render()`.
   - Thứ tự đóng gói giao diện (pack layout) được chuẩn hóa thẳng hàng từ trên xuống:
     1. Banner Paused (nếu đang pause) -> `pack(fill="x")`
     2. Banner Active Profile (nếu khác "Default" và không ở subfolder) -> `pack(fill="x")`
     3. Breadcrumb navigation (nếu ở subfolder) -> `pack(fill="x")`
     4. Danh sách Shortcut Items (`PanelItemRenderer`) -> `pack(fill="both", expand=True)`
     5. Divider đường kẻ ngang và Footer Status Bar -> `pack(fill="x")`
   - Xóa bỏ hoàn toàn 3 file phân hệ Volume: `volume_service.py`, `panel_volume_widget.py`, `volume_overlay.py`.
   - Đổi tên và tinh giản `general_volume_tab.py` thành `general_tab.py` (`GeneralVolumeTab` -> `GeneralTab`), loại bỏ toàn bộ cài đặt âm lượng, chỉ giữ lại Khởi động cùng Windows (Startup) và Ngôn ngữ (Language).
   - Dọn sạch action `show_volume_slider` khỏi `PanelLogic`, `panel_item_renderer.py`, `action_picker_dialog.py`, `shortcut_executor.py`, `config_service.py`, các file i18n và file cấu hình thực tế của người dùng.

## Consequences
- Triệt tiêu hoàn toàn hiện tượng render flicker khi cuộn chuột và duyệt phím trên Shortcut Panel.
- Tốc độ phản hồi giao diện tức thời, giảm tải CPU về mức xấp xỉ 0% khi điều hướng.
- Kiến trúc phân lớp rành mạch: `PanelLogic` duy trì tính trừu tượng cao, `PanelWindow` điều phối hiển thị thông minh, `PanelItemRenderer` quản lý widget vòng đời tại chỗ.
- Codebase được tinh gọn sâu sắc: giảm ~400 dòng code liên quan đến phân hệ Volume, các file đều duy trì nghiêm ngặt dưới ngưỡng giới hạn 250 dòng (SYSTEM LOCK).
