# === DEBUG2 REPORT — gesture-trail-x1x2-flaky — 2026-11-08 23:25:00 ===
Đối chiếu debug1: docs/debug/gesture-trail-x1x2-flaky.debug1.md (root cause debug1 chốt: H1 TrailOverlay cướp focus + lệch toạ độ DPI; H2 hardcode move_threshold=8 + Silent Drop; H3 os.execve giữ handle DLL)

---

## VÙNG MÙ ĐÃ ĐÀO

### 1. `mouse_mapper_logic.py:60-69` & `131-135` — Khiếm khuyết State Machine Rocker Gesture: Rò rỉ Click Chuột Phải (`inject_right_click`) sau khi bấm X1/X2
- **Lý do đây là vùng mù của debug1:** Debug1 quy kết toàn bộ hiện tượng *"X1/X2 chỉ work lần đầu"* cho việc `TrailOverlay` cướp focus. Debug1 hoàn toàn bỏ qua kịch bản người dùng giữ RMB và bấm X1/X2 với tay giữ yên (chuột di chuyển < 8px, `TrailOverlay` chưa từng xuất hiện).
- **Phân tích cơ chế:**
  - Tại `mouse_mapper_logic.py:60-69`, hàm `_on_xbutton_down` nhận diện nút X1/X2 và gọi `hotkey_service.switch_tab_x1x2(forward)` chuyển tab thành công. Tuy nhiên, hàm này **hoàn toàn không chuyển trạng thái `_state`** (vẫn giữ nguyên `MapperState.RIGHT_HELD`) và **không lưu bất kỳ cờ đánh dấu nào** (như `self._xbutton_used = True`).
  - Khi người dùng nhả chuột phải, hàm `_on_right_up` (dòng 131) kiểm tra `if prev == MapperState.RIGHT_HELD:`. Do không biết nút X1/X2 vừa được sử dụng, hệ thống coi đây là một cú click chuột phải ngắn và thực hiện:
    ```python
    hotkey_service.inject_right_click()
    return True
    ```
  - Lệnh này inject một cặp sự kiện `WM_RBUTTONDOWN` + `WM_RBUTTONUP` vào cửa sổ Chromium, lập tức **bật Context Menu** ngay trên tab vừa chuyển tới.
  - Khi Context Menu hiển thị, Chromium và Windows bước vào vòng lặp menu modal (`WM_ENTERMENULOOP`) và chiếm quyền bắt chuột (`SetCapture`). Ở trạng thái này:
    - Bất kỳ cú click chuột phải nào tiếp theo sẽ bị menu modal nuốt để đóng menu ngữ cảnh, không phát sinh sự kiện click bình thường.
    - Sự kiện `WM_XBUTTONDOWN` bị `DefWindowProc` của menu modal bỏ qua hoàn toàn.
  - **Kết luận:** Ngay cả khi không có `TrailOverlay` và không mất focus, việc thiếu cơ chế nuốt chuột phải sau Rocker Gesture khiến mọi lần bấm X1/X2 thành công đều để lại một Context Menu modal "bẫy" các thao tác kế tiếp, giải thích trực tiếp vì sao X1/X2 chỉ hoạt động ở lần đầu tiên.

---

### 2. `mouse_hook_service.py:110-150` & `window_service.py:20-46` — Rủi ro Treo / Timeout Hook Win32 (`LowLevelHooksTimeout` 200ms)
- **Lý do đây là vùng mù của debug1:** Debug1 ghi nhận *"LOẠI TRỪ DEADLOCK HOOK: Hook không bị treo trong with self._lock; các lệnh on_gesture_start chỉ đẩy root.after()..."*. Nhận định này chỉ dựa trên việc soi xét khóa luồng nội bộ Python (`threading.Lock()`), hoàn toàn bỏ qua cơ chế quản lý vòng đời hook của hệ điều hành Windows Win32.
- **Phân tích cơ chế:**
  - Hệ điều hành Windows áp đặt giới hạn thời gian phản hồi nghiêm ngặt đối với hook bàn phím và chuột cấp thấp (`LowLevelHooksTimeout`, mặc định từ 200ms đến 300ms trên Windows 10/11). Nếu hàm `_hook_proc` xử lý vượt quá thời gian này, **Windows sẽ âm thầm gỡ bỏ (`silently unhook`) hook `WH_MOUSE_LL`** mà không hề ném ra ngoại lệ Python nào.
  - Trong `_hook_proc`, khi xảy ra `WM_XBUTTONDOWN`, code thực hiện đồng bộ ngay trong luồng hook:
    1. Gọi `ctypes.windll.user32.GetForegroundWindow()`
    2. Gọi `window_service.get_hwnd_info(hwnd)`, bên trong thực hiện `GetWindowTextW(hwnd, ...)` gửi message đồng bộ `WM_GETTEXT` tới cửa sổ foreground. Nếu tiến trình trình duyệt đang bận tải trang hoặc hydrate DOM nặng, lệnh này có thể bị block.
    3. Gọi `hotkey_service.switch_tab_x1x2(forward)` gọi đồng bộ `SendInput` để bơm phím `Ctrl+Tab`.
  - Nếu tổng thời gian thực thi chạm ngưỡng 200ms, Windows tự động hủy hook. Khi đó, toàn bộ chuột bị "trơ" hoàn toàn đối với RightWheel.
  - Mặc dù `MouseHookService` có luồng watchdog (`_start_watchdog`), chu kỳ kiểm tra là **10 giây** (`time.sleep(10)`). Trong khoảng thời gian lên đến 10 giây đó, tiện ích hoàn toàn mất quyền kiểm soát chuột, tạo cảm giác chập chờn / chết hẳn sau lần thao tác đầu tiên.

---

### 3. `trail_overlay.py:43-78` & `83-105` — Độ trễ khởi tạo Overlay tạo thành Dây cung thẳng (Latency Chord Delay)
- **Lý do đây là vùng mù của debug1:** Debug1 giải thích Triệu chứng 1 (Vệt thẳng bắt đầu từ vị trí lạ) đơn thuần do sự chênh lệch hệ toạ độ giữa `MSLLHOOKSTRUCT` (toạ độ vật lý màn hình) và `GetCursorPos` (toạ độ logic khi DPI virtualization kích hoạt).
- **Phân tích cơ chế:**
  - Tại `mouse_mapper_logic.py:84`: Khi chuyển sang `GESTURE`, code truyền `(self._down_x, self._down_y)` vào `on_gesture_start`. Đây là toạ độ tại thời điểm người dùng bắt đầu nhấn chuột phải xuống.
  - `trail.start(x, y)` đẩy `root.after(0, lambda: self._do_start(x, y))` vào hàng đợi Tkinter.
  - Để Tkinter tạo `tk.Toplevel`, cấu hình `overrideredirect`, `attributes`, tạo `tk.Canvas` và pack lên màn hình, Windows mất từ **20ms đến 50ms**.
  - Trong 20-50ms đó, tay người dùng tiếp tục rê chuột để vẽ cử chỉ (chuột đã đi được 50px - 150px).
  - Khi `_do_start` chạy đến dòng 77 (`self._poll()`), toạ độ hiện tại lấy từ `GetCursorPos` đã ở rất xa toạ độ `_down_x, _down_y` ban đầu.
  - Ngay frame đầu tiên, dòng 90-99 thực hiện nối `lx, ly` (điểm nhấn RMB ban đầu) với `cx, cy` (điểm hiện tại sau độ trễ 50ms).
  - **Kết luận:** Ngay cả trên màn hình 100% DPI (không hề có sai lệch toạ độ ảo hóa DPI), nét vẽ đầu tiên **luôn luôn là một đường thẳng tắp cắt ngang màn hình** do lấy mốc toạ độ quá khứ nối với toạ độ tương lai sau độ trễ khởi tạo cửa sổ.

---

### 4. `trail_overlay.py:35-42` & `mouse_mapper_logic.py:143` — Bất đồng bộ huỷ Overlay khiến Phím tắt gửi nhầm mục tiêu
- **Lý do đây là vùng mù của debug1:** Debug1 cho rằng Chromium mất focus sau khi overlay bị destroy. Nhưng thực tế xung đột xảy ra ngay **trước khi** overlay kịp destroy!
- **Phân tích cơ chế:**
  - Khi cử chỉ kết thúc, `_on_right_up()` gọi `self.on_gesture_end()` (chính là `trail.stop()`).
  - `trail.stop()` thực hiện: `root.after(0, self._do_stop)`. Tác vụ huỷ cửa sổ được đẩy vào hàng đợi của Tkinter thread, **chưa được thực thi ngay lập tức**.
  - Ngay dòng tiếp theo trong luồng hook, `_on_right_up()` gọi:
    ```python
    shortcut_executor.execute(res["data"]["keys"])
    ```
  - Tại thời điểm `SendInput` phát lệnh bàn phím (ví dụ `Ctrl+W`), `self._win` của `TrailOverlay` **vẫn đang tồn tại và vẫn đang là cửa sổ Foreground** trên Windows!
  - Lệnh `Ctrl+W` được gửi thẳng vào cửa sổ Tkinter thay vì trình duyệt Chromium, làm cho tab không đóng và người dùng tưởng rằng phím tắt không hoạt động.

---

## GIẢ THUYẾT ĐỐI LẬP

### H_alt1 (Lỗi Trạng thái Logic — Khiếm khuyết Rocker Gesture State Machine):
**Triệu chứng RMB và X1/X2 chỉ hoạt động lần đầu bắt nguồn từ việc thiếu cờ triệt tiêu chuột phải (`_xbutton_used`). Sau khi bấm X1/X2, việc nhả RMB tự động inject `inject_right_click()`, kích hoạt Context Menu dạng modal của Chromium, khóa bắt toàn bộ sự kiện chuột tiếp theo.**
- **Kiểm chứng:**
  - Kiểm tra `mouse_mapper_logic.py:60-69`: `_on_xbutton_down` trả về `True` nhưng không đổi `_state` và không gán cờ.
  - Kiểm tra `mouse_mapper_logic.py:131-134`: `prev == MapperState.RIGHT_HELD` kích hoạt `inject_right_click()`.
  - Thực tế Win32: Context menu Chromium mở ra sẽ bắt chuột bằng modal loop, vô hiệu hóa mọi cú bấm X1/X2 kế tiếp cho tới khi menu được đóng.

### H_alt2 (Lỗi Hạ tầng Win32 Hook — Vi phạm Timeout Hook Cấp Thấp do Gọi Đồng Bộ):
**Việc thực hiện các lệnh Win32 nặng (`GetWindowTextW`, `SendInput`) đồng bộ bên trong callback `_hook_proc` gây nguy cơ vi phạm `LowLevelHooksTimeout` (200ms) của Windows, khiến Windows tự động ngắt kết nối hook `WH_MOUSE_LL`, gây tê liệt toàn bộ chuột trong chu kỳ 10 giây của watchdog.**
- **Kiểm chứng:**
  - `mouse_hook_service.py:143`: gọi trực tiếp `_on_event` trên luồng hook.
  - `window_service.py:25`: `GetWindowTextW` gửi message xuyên tiến trình, có thể block luồng hook.
  - `mouse_hook_service.py:105`: Watchdog phục hồi có độ trễ lên tới 10 giây.

---

## PHÁN QUYẾT: CẢ HAI ĐỀU GÓP PHẦN

### Lý do + Bằng chứng quyết định:
1. **Debug1 đã xác định chính xác 3 khiếm khuyết nền tảng:**
   - H1: `TrailOverlay` thiếu `WS_EX_NOACTIVATE` cướp focus của trình duyệt; xung đột toạ độ vật lý vs logic do DPI awareness = 0.
   - H2: `main.py:21` hardcode `move_threshold=8` ghi đè giá trị chuẩn 50px, kết hợp `Silent Drop` nuốt sạch click chuột phải khi tay rung nhẹ.
   - H3: `tray_ui.py:85` gọi `os.execve` trên Windows giữ handle DLL trong `%TEMP%\_MEIxxxxxx`, cản trở PyInstaller bootloader dọn dẹp thư mục tạm.
2. **Tuy nhiên, Debug2 phát hiện 3 nguyên nhân cốt lõi bổ sung giải thích triệt để hiện tượng thực tế:**
   - **Hiện tượng X1/X2 chỉ work lần đầu:** Không chỉ do mất focus (`TrailOverlay`), mà chủ yếu do **Rò rỉ Click Chuột Phải (`inject_right_click`)** khi nhả RMB sau khi dùng X1/X2. Context Menu modal của Chromium mở ra và khóa chặt mọi thao tác tiếp theo.
   - **Hiện tượng vệt thẳng ban đầu:** Không chỉ do DPI virtualization, mà còn do **Độ trễ khởi tạo Canvas Tkinter (20-50ms)**: điểm xuất phát bị neo vào toạ độ `_down` cũ, trong khi điểm vẽ đầu tiên đã chạy theo con trỏ hiện tại tạo thành một dây cung thẳng.
   - **Cơ chế gửi phím tắt bị nuốt:** `trail.stop()` đẩy vào hàng đợi Tkinter bất đồng bộ, trong khi `SendInput` bắn phím tắt ngay lập tức khi `TrailOverlay` vẫn đang là Active Window.
3. Nếu chỉ sửa theo kiến nghị của debug1 (thêm `WS_EX_NOACTIVATE` và sửa `move_threshold`), người dùng bấm X1/X2 **vẫn sẽ bị hiện menu ngữ cảnh chuột phải ngoài ý muốn** và **vẫn bị kẹt ở lần bấm thứ hai** do thiếu cờ triệt tiêu Rocker Gesture. Cả hai nhóm nguyên nhân phải được kết hợp xử lý đồng thời.

---

## SO SÁNH CẠNH NHAU

| Tiêu chí | debug1 | debug2 |
|---|---|---|
| **Triệu chứng 1 (Vệt thẳng lạ)** | Do lệch toạ độ vật lý (`MSLLHOOKSTRUCT`) và logic (`GetCursorPos`) khi DPI awareness = 0. | **Đồng ý và bổ sung:** Độ trễ 20-50ms khi tạo Tkinter Canvas khiến điểm `_down` quá khứ bị nối thẳng tới toạ độ hiện tại (Latency Chord), xảy ra kể cả ở 100% DPI. |
| **Triệu chứng 2 (RMB & X1/X2 chỉ chạy lần đầu)** | Do `TrailOverlay` cướp focus + `move_threshold=8` rung tay kích hoạt `Silent Drop`. | **Cả hai góp phần:** Bổ sung khiếm khuyết cốt lõi: Thiếu cờ `_xbutton_used` khiến `_on_right_up` inject click chuột phải sau khi bấm X1/X2, mở Context Menu modal khóa chết các thao tác tiếp theo. |
| **Triệu chứng 3 (Lỗi thư mục tạm khi Restart)** | `os.execve` kế thừa handle file DLL trong thư mục `_MEIxxxxxx`. | **Đồng ý hoàn toàn:** Cơ chế Win32 CRT `_spawnve(_P_OVERLAY)` gây xung đột chia sẻ file với PyInstaller bootloader. |
| **Đánh giá Hook Threading** | Khẳng định không có deadlock hook vì chỉ dùng `self._lock` nội bộ. | **Phản biện & Cảnh báo:** Nguy cơ vi phạm `LowLevelHooksTimeout` (200ms) của Windows khi gọi `GetWindowTextW` và `SendInput` đồng bộ trong hook procedure. |
| **Cơ chế đóng Overlay & Gửi Phím** | `self._win.destroy()` làm mất focus của trình duyệt. | **Phát hiện thêm:** `trail.stop()` bất đồng bộ qua `root.after` khiến `SendInput` phím tắt bắn vào `TrailOverlay` trước khi overlay kịp biến mất. |

---

## KHUYẾN NGHỊ SỬA TOÀN DIỆN (CHƯA SỬA, chờ user xác nhận)

1. **Khắc phục State Machine Rocker Gesture (`mouse_mapper_logic.py`):**
   - Bổ sung cờ `self._xbutton_used = False` được reset về `False` khi `_on_right_down`.
   - Trong `_on_xbutton_down`: nếu bấm X1/X2 thành công, đánh dấu `self._xbutton_used = True`.
   - Trong `_on_right_up`: nếu `self._xbutton_used` là `True`, triệt tiêu hoàn toàn sự kiện (không gọi `inject_right_click()`), tránh bật Context Menu làm tê liệt các thao tác tiếp theo.

2. **Khắc phục Focus & Window Style của Overlay (`trail_overlay.py`):**
   - Thiết lập extended styles qua Win32 API (`SetWindowLongPtrW`): `WS_EX_NOACTIVATE` (0x08000000), `WS_EX_TRANSPARENT` (0x00000020), `WS_EX_LAYERED` (0x00080000) và `WS_EX_TOOLWINDOW` (0x00000080).
   - Đảm bảo overlay tuyệt đối không cướp active focus và chuột click xuyên thấu 100%.

3. **Khắc phục Vệt thẳng Dị thường (Latency Chord & DPI) (`trail_overlay.py`):**
   - Đồng bộ DPI awareness cho tiến trình (`shcore.SetProcessDpiAwareness(2)`).
   - Điểm bắt đầu vẽ (`_last_point`) phải được lấy ngay tại thời điểm `Canvas` sẵn sàng (hoặc lấy từ toạ độ sự kiện mouse move trực tiếp), không nối tắt từ toạ độ `_down` ban đầu để tránh tạo dây cung thẳng.

4. **Khắc phục Ngưỡng Rung tay (`main.py`):**
   - Loại bỏ tham số hardcode `move_threshold=8` trong `main.py:21`, sử dụng mặc định `move_threshold=50` từ `mouse_mapper_types.py`.

5. **Khắc phục Lỗi Thư mục tạm khi Restart (`tray_ui.py`):**
   - Thay thế `os.execve` bằng cơ chế spawn tiến trình độc lập không kế thừa handle (dùng `subprocess.Popen` với cờ `DETACHED_PROCESS` và lệnh trễ `cmd.exe /c timeout /t 1 /nobreak > nul & start "" "<exe>"`), sau đó gọi `sys.exit(0)` để PyInstaller bootloader dọn dẹp sạch sẽ.

6. **Bảo vệ Luồng Hook Cấp Thấp (`mouse_hook_service.py`):**
   - Tránh gọi các hàm Win32 có khả năng block (`GetWindowTextW`) hoặc `SendInput` trực tiếp trong `_hook_proc`. Đẩy việc thực thi ra worker thread hoặc thực hiện bất đồng bộ để đảm bảo callback luôn trả về trong < 5ms.
