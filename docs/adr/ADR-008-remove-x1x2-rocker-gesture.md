# ADR-008: Loại bỏ Hoàn toàn Cử chỉ Nút phụ X1/X2 (Rocker Gesture) Khắc phục Lỗi Kẹt Nút Chuột

## Trạng thái
Accepted

## Ngữ cảnh
F-003 và F-005 đã triển khai cử chỉ Rocker Gesture: Giữ chuột phải (RMB) + bấm nút phụ X1/X2 (XBUTTON1/XBUTTON2) để chuyển tab trước/sau trong trình duyệt Chromium.
Tuy nhiên, tính năng này gây ra nhiều lỗi vặt nghiêm trọng trong quá trình sử dụng thực tế:
1. **Kẹt nút chuột trái (Left click bị vô hiệu)**: Đôi khi sau khi thao tác chuột, nút chuột trái bấm không còn tác dụng trên desktop hay các ứng dụng.
2. **Nút chuột phải (RMB) không kích hoạt**: Context menu không hiện ra khi nhấp chuột phải, hoặc rơi vào trạng thái bị nuốt sự kiện.
3. **Mất cân bằng sự kiện trong driver**: Trong `mouse_hook_service.py`, hook cấp thấp `WH_MOUSE_LL` chỉ chặn `WM_XBUTTONDOWN` (0x020B) mà không chặn `WM_XBUTTONUP` (0x020C). Khi người dùng bấm X1/X2, Windows chỉ nhận được sự kiện UP mà không có DOWN tương ứng, khiến driver chuột của hệ thống rơi vào trạng thái bất đối xứng (asymmetric state).
4. **Xung đột SendInput**: Việc gửi tổ hợp phím `Ctrl+Tab` / `Ctrl+Shift+Tab` qua `SendInput` trong khi các nút chuột vật lý đang được giữ đè làm Windows xử lý sai lệch cờ trạng thái phím/chuột.

## Quyết định kiến trúc

### 1. Loại bỏ việc chặn X1/X2 trong Low-Level Mouse Hook (`mouse_hook_service.py`)
- Xóa bỏ việc kiểm tra và chặn `w_param == WM_XBUTTONDOWN`.
- Xóa các định nghĩa hằng số không dùng đến: `WM_XBUTTONDOWN`, `XBUTTON1`, `XBUTTON2`.
- Luồng hook `WH_MOUSE_LL` sẽ bỏ qua hoàn toàn các sự kiện nút phụ X1/X2, để Windows và driver chuột phần cứng tự xử lý tự nhiên (chức năng Back/Forward mặc định).

### 2. Dọn dẹp State Machine trong `mouse_mapper_logic.py`
- Xóa cờ `self._xbutton_used`.
- Xóa nhánh xử lý `event.kind == "xbutton_down"` trong hàm `handle()`.
- Xóa phương thức `_on_xbutton_down(self, button: int) -> bool`.
- Trong `_on_right_up()`: Loại bỏ điều kiện kiểm tra `self._xbutton_used`, trả lại luồng nhả chuột phải nguyên bản, minh bạch và an toàn.
- Trong `_on_right_down()`: Bỏ việc gán `self._xbutton_used = False`.

### 3. Dọn dẹp Services và UI
- Trong `hotkey_service.py`: Xóa bỏ hàm `switch_tab_x1x2(forward: bool)`.
- Trong `mouse_mapper_types.py`: Loại bỏ kiểu sự kiện `"xbutton_down"`.
- Trong `reference_tab.py`: Xóa dòng tra cứu `"RMB + X1/X2"` để không gây hiểu nhầm cho người dùng.

## Hậu quả & Đánh giá tác động
- **Tích cực**:
  - Triệt tiêu 100% nguyên nhân gây kẹt nút chuột trái (left click) và tê liệt nút chuột phải (RMB).
  - Trạng thái driver chuột của hệ điều hành luôn cân bằng tuyệt đối.
  - Mã nguồn trong `mouse_mapper_logic.py` và `mouse_hook_service.py` trở nên gọn gàng, giảm độ phức tạp và nguy cơ race condition.
- **Tính năng được giữ nguyên**:
  - Cử chỉ Shift + Cuộn chuột chuyển tab trình duyệt (F-001) hoạt động độc lập và ổn định.
  - Cử chỉ vẽ chuột 8 hướng (F-003, F-004) hoạt động hoàn hảo.
  - Shortcut Panel và Alt+Tab dual-mode hoạt động mượt mà.
