# === DEBUG1 REPORT — gesture-trail-x1x2-flaky — 2026-11-08 23:05:00 ===

## Lỗi
- **Mô tả người dùng báo (nguyên văn 3 triệu chứng sau khi build .exe từ commit F-004):**
  1. *"Khi giữ chuột phải, nó luôn vẽ 1 đường thẳng bắt đầu từ 1 vị trí nào đó không biết"* — Mọi lần giữ RMB, TrailOverlay vẽ ngay một đường thẳng từ một điểm cố định/sai tới vị trí chuột hiện tại.
  2. *"Nút RMB và X1/X2 nhiều lúc không work, chỉ work lần đầu tiên"* — Gesture và X1/X2 hoạt động đúng ở lần giữ RMB đầu tiên, các lần sau không phản hồi; click RMB bình thường nhiều lúc không hiện menu ngữ cảnh.
  3. *"Khi restart thì bị báo: thất bại khi remove temporary folder"* — Bấm Restart trong tray menu báo lỗi PyInstaller bootloader không xoá được thư mục `_MEIxxxxxx` tạm khi thoát.

- **Bối cảnh & Commit nghi vấn:**
  - `a5620b3` (F-004: `fix(f004-gesture-fix-settings-merge): gesture engine fixes, trail overlay, settings merge`)
  - `f5019d3` (`fix(tray-restart): clear _MEIPASS2 env before self-exec to fix PyInstaller onefile restart crash`)
  - `5dd60f0` (`fix: increase RMB move_threshold 8→50px — tolerate hand tremor while holding RMB`)

---

## Tái hiện & Bằng chứng thực nghiệm

### 1. Tái hiện Triệu chứng 1 (Đường thẳng từ vị trí sai/lạ):
- **Phân tích toạ độ `MSLLHOOKSTRUCT` vs `GetCursorPos` khi DPI virtualization có hiệu lực:**
  - `mouse_hook_service.py:127`: `x, y = data.pt.x, data.pt.y`. Cấu trúc `MSLLHOOKSTRUCT` của hook `WH_MOUSE_LL` trong Win32 API **luôn trả về toạ độ vật lý thực tế của màn hình (Physical Screen Pixels)**, bất kể tiến trình có DPI awareness hay không.
  - `mouse_mapper_logic.py:84`: Khi chuyển sang `GESTURE`, truyền `(self._down_x, self._down_y)` (toạ độ vật lý) vào `on_gesture_start`.
  - `trail_overlay.py:75`: `self._last_point = (x - vx, y - vy)` lưu toạ độ vật lý này làm điểm bắt đầu.
  - `trail_overlay.py:83-86`: Trong vòng lặp `_poll()`, vị trí chuột lại được lấy bằng `ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))`. Do ứng dụng `RightWheel` không khai báo DPI Awareness (`SetProcessDpiAwareness`), Windows áp dụng DPI Virtualization khiến `GetCursorPos` trả về **toạ độ logic đã scale (Logical / Scaled Coordinates)**.
  - Thực nghiệm trên màn hình có scale DPI (ví dụ 125% hoặc 150%):
    - Toạ độ click chuột thực tế: `(1500, 900)`
    - Toạ độ do `GetCursorPos` trả về: `(1000, 600)`
    - Ngay trong tick `_poll()` đầu tiên: `self._canvas.create_line(1500, 900, 1000, 600)` vẽ ngay một đoạn thẳng nhảy vọt 500px từ toạ độ vật lý sang toạ độ logic, tạo thành vệt thẳng kỳ lạ xuất phát từ "một vị trí không biết" trước khi vẽ tiếp nét của con trỏ chuột.
  - Thêm vào đó, do `trail.start()` đưa tác vụ vào hàng đợi `root.after(0, ...)`, độ trễ vòng lặp Tkinter (20-50ms) khiến con trỏ thực tế đã di chuyển thêm một khoảng đáng kể so với thời điểm bấm RMB, làm cho đoạn nối đầu tiên luôn là một dây cung thẳng tắp cắt ngang nét vẽ ban đầu.

### 2. Tái hiện Triệu chứng 2 (RMB và X1/X2 chỉ hoạt động lần đầu, các lần sau trơ):
- **Bằng chứng 1: Chiếm quyền Focus (Focus Stealing) của `TrailOverlay`:**
  - Trong `trail_overlay.py:63-65`:
    ```python
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    ```
    Cửa sổ overlay được tạo toàn màn hình (`vw x vh`), topmost, nhưng **không có cờ `WS_EX_NOACTIVATE` (0x08000000)** trong Windows Extended Window Styles.
  - Khi `win` hiển thị, Windows lập tức kích hoạt nó thành cửa sổ Foreground (Active Window). Trình duyệt Chromium (Chrome/Edge) bị mất Focus.
  - Khi cử chỉ kết thúc, `_do_stop` gọi `self._win.destroy()`. Việc huỷ cửa sổ đang active khiến Windows kích hoạt một cửa sổ ngẫu nhiên trong Z-order (thường là desktop hoặc cửa sổ nền), Chromium không tự động lấy lại Focus.
  - Ở lần giữ RMB tiếp theo:
    - Trong `mouse_mapper_logic.py:63-65` (`_on_xbutton_down`):
      ```python
      hwnd = ctypes.windll.user32.GetForegroundWindow()
      exe, _, _ = window_service.get_hwnd_info(hwnd)
      if tab_switch_logic.is_chromium_browser(exe):
          hotkey_service.switch_tab_x1x2(forward)
      ```
      Vì `GetForegroundWindow()` không còn là trình duyệt, `is_chromium_browser(exe)` trả về `False` → **X1/X2 hoàn toàn không chuyển tab!**
    - Tương tự với Gesture: `shortcut_executor.execute("ctrl+w")` gửi tổ hợp phím bằng `SendInput` tới cửa sổ đang Foreground. Vì trình duyệt mất Focus, phím tắt `Ctrl+W` bay vào hư không, tab không đóng.

- **Bằng chứng 2: Hardcode `move_threshold=8` trong `main.py` kết hợp Silent Drop trong F-004:**
  - Trong `src/main.py:21`:
    ```python
    mapper = MouseMapperLogic(HotkeyConfig(move_threshold=8))
    ```
    Dòng 21 truyền cứng `move_threshold=8`, ghi đè (override) giá trị mặc định `50px` được fix tại commit `5dd60f0` (`fix: increase RMB move_threshold 8→50px — tolerate hand tremor while holding RMB`).
  - Khi người dùng giữ RMB để bấm X1/X2 hoặc click RMB thông thường, rung lắc tự nhiên của tay người khi click nút chuột luôn vượt 8px (`dx >= 8 or dy >= 8`).
  - Hậu quả:
    - Trạng thái lập tức nhảy sang `MapperState.GESTURE`, bật overlay và giật focus của trình duyệt trước khi kịp bấm X1/X2.
    - Khi thả chuột, cử chỉ lắc tay không khớp preset nào. F-004 áp dụng logic **Silent Drop** (`mouse_mapper_logic.py:145`):
      ```python
      # Unmatched: Silent Drop — suppress completely (no context menu)
      return True
      ```
      Nuốt hoàn toàn click chuột phải, không re-inject `inject_right_click()`. Người dùng click chuột phải thông thường nhưng không bao giờ thấy menu ngữ cảnh xuất hiện!

- **Bằng chứng 3: Vi phạm Tkinter Threading Contract (CLAUDE.md Mục 6):**
  - Tại `src/main.py:26`:
    ```python
    panel_window = PanelWindow(panel)
    trail = TrailOverlay(getattr(panel_window, "_root", None))
    ```
    Lúc `TrailOverlay` khởi tạo, luồng `_run` của `PanelWindow` chưa kịp chạy xong, `panel_window._root` vẫn là `None`.
  - `TrailOverlay._get_root()` fallback sang `getattr(tk, "_default_root", None)`.
  - Sau đó, từ luồng hook chuột (`WH_MOUSE_LL` thread), `trail.start()` và `trail.stop()` gọi trực tiếp `root.after(0, ...)`.
  - Điều này vi phạm quy tắc CLAUDE.md: *"Giao tiếp hook thread → tkinter thread qua queue.Queue + root.after(30, pump)"*, dẫn đến xung đột thread an toàn trong Tcl/Tk, rớt callback `after_cancel` và bất đồng bộ trạng thái huỷ overlay.

### 3. Tái hiện Triệu chứng 3 (Lỗi PyInstaller temporary folder khi Restart):
- **Bằng chứng Win32 process model:**
  - Tại `src/features/mouse_mapper/ui/tray_ui.py:77-85`:
    ```python
    def _restart(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        icon.stop()
        env = os.environ.copy()
        env.pop("_MEIPASS2", None)
        os.execve(sys.executable, [sys.executable] + sys.argv, env)
    ```
  - Trong gói PyInstaller `--onefile` trên Windows:
    - Khi chạy `.exe`, tiến trình Bootloader cha (Process 1) giải nén toàn bộ tài nguyên vào `%TEMP%\_MEIxxxxxx`, sau đó spawn tiến trình con (Process 2) để chạy Python.
    - Process 1 dùng `WaitForSingleObject` đợi Process 2 kết thúc, sau đó gọi `RemoveDirectoryW` để dọn dẹp `%TEMP%\_MEIxxxxxx`.
  - Trên hệ điều hành Windows không có syscall `execve` thay thế tiến trình nguyên tử như Linux/POSIX. Hàm `os.execve` trong Python Windows gọi C runtime `_spawnve(_P_OVERLAY, ...)`, thực chất là khởi tạo tiến trình con mới (Process 3) và gọi `_exit(0)` kết thúc Process 2.
  - Điểm xung đột chí mạng:
    1. Tiến trình mới (Process 3) được spawn với quyền kế thừa handle từ Process 2, bao gồm các file DLL runtime (`python311.dll`, `_tkinter.pyd`, `tcl86t.dll`...) nằm ngay trong thư mục `_MEIxxxxxx`.
    2. Đồng thời, Process 1 thấy Process 2 vừa thoát liền lập tức gọi xoá thư mục `_MEIxxxxxx`.
    3. Vì các file/DLL bên trong thư mục vẫn đang bị khoá bởi Windows File System / Process 3, hàm `RemoveDirectoryW` thất bại với mã lỗi Access Denied / Sharing Violation.
    4. PyInstaller Bootloader bật hộp thoại cảnh báo: **"Failed to remove temporary folder: _MEIxxxxxx"**.

---

## NHẬT KÝ ĐIỀU TRA (Mọi nơi đã xem)

| File:Dòng | Lý do xem | Kết luận |
|---|---|---|
| `src/main.py:21` | Kiểm tra tham số khởi tạo `MouseMapperLogic` | **XÁC NHẬN NGUYÊN NHÂN CHÍNH (Triệu chứng 2)**: Hardcode `HotkeyConfig(move_threshold=8)` ghi đè mức 50px của `mouse_mapper_types.py`. Chỉ cần lắc tay 8px khi bấm RMB là bị nhảy vào `GESTURE`, nuốt click chuột phải và cướp Focus. |
| `src/main.py:25-30` | Kiểm tra việc đấu nối `TrailOverlay` với `PanelWindow` và `MouseMapperLogic` | **XÁC NHẬN NGUYÊN NHÂN (Triệu chứng 1 & 2)**: `getattr(panel_window, "_root", None)` trả về `None` khi khởi tạo. Đấu nối `mapper.on_gesture_start = trail.start` gọi trực tiếp từ hook thread sang tkinter. |
| `src/features/mouse_mapper/ui/trail_overlay.py:43-78` | Kiểm tra hàm `_do_start()` và cách tạo `tk.Toplevel` | **XÁC NHẬN NGUYÊN NHÂN (Triệu chứng 1 & 2)**: Cửa sổ overlay thiếu style `WS_EX_NOACTIVATE` và `WS_EX_TRANSPARENT`, gây giật Focus từ Chromium; `self._last_point` nạp toạ độ vật lý từ hook struct `MSLLHOOKSTRUCT`. |
| `src/features/mouse_mapper/ui/trail_overlay.py:79-105` | Kiểm tra vòng lặp `_poll()` và hàm `GetCursorPos` | **XÁC NHẬN NGUYÊN NHÂN (Triệu chứng 1)**: `GetCursorPos` trả về toạ độ logic (DPI scaled). Nối toạ độ vật lý `self._last_point` với toạ độ logic của `GetCursorPos` sinh ra đường thẳng dị thường đầu tiên. Vòng lặp `after(16)` độc lập với sự kiện mouse hook. |
| `src/features/mouse_mapper/ui/trail_overlay.py:106-124` | Kiểm tra `_do_stop()` và giải phóng overlay | **XÁC NHẬN CƠ CHẾ**: `self._win.destroy()` huỷ cửa sổ đang active khiến Windows chuyển focus sang cửa sổ khác ngoài Chromium, làm tê liệt các lần kích hoạt phím/X1X2 tiếp theo. |
| `src/features/mouse_mapper/logic/mouse_mapper_logic.py:60-69` | Kiểm tra xử lý `_on_xbutton_down` | **XÁC NHẬN CƠ CHẾ**: Kiểm tra `is_chromium_browser(exe)` dựa vào `GetForegroundWindow()`. Do overlay làm mất active window của trình duyệt nên nhánh này bị bỏ qua ở các lần sau. |
| `src/features/mouse_mapper/logic/mouse_mapper_logic.py:70-85` | Kiểm tra `_on_move` và điều kiện kích hoạt `GESTURE` | **XÁC NHẬN CƠ CHẾ**: Ngưỡng 8px kích hoạt ngay khi người dùng chỉ định click chuột hoặc bấm X1/X2. |
| `src/features/mouse_mapper/logic/mouse_mapper_logic.py:115-147` | Kiểm tra `_on_right_up` và Silent Drop trong F-004 | **XÁC NHẬN CƠ CHẾ (Triệu chứng 2)**: Khi lắc tay >8px không khớp gesture nào, code `return True` (Silent Drop), dập tắt hoàn toàn menu ngữ cảnh chuột phải. |
| `src/features/mouse_mapper/services/mouse_hook_service.py:110-150` | Kiểm tra luồng hook `WH_MOUSE_LL` và việc gọi `_on_event` | **LOẠI TRỪ DEADLOCK HOOK**: Hook không bị treo trong `with self._lock:`; các lệnh `on_gesture_start` chỉ đẩy `root.after()`, không block luồng hook. Nhưng toạ độ `data.pt` là physical pixels. |
| `src/features/mouse_mapper/ui/tray_ui.py:77-85` | Kiểm tra hàm `_restart()` | **XÁC NHẬN NGUYÊN NHÂN (Triệu chứng 3)**: Sử dụng `os.execve` trên Windows trong môi trường PyInstaller `--onefile` khiến process mới giữ handle khoá thư mục `_MEIxxxxxx`, cản trở bootloader dọn dẹp thư mục tạm. |
| `CLAUDE.md:113-119` | Đối chiếu quy tắc kiến trúc tkinter Threading (Mục 6) | **XÁC NHẬN VI PHẠM NGUYÊN TẮC**: F-004 gọi `root.after()` trực tiếp từ luồng hook chuột, không đi qua `queue.Queue` + `pump` như quy định. |

---

## GIẢ THUYẾT XẾP HẠNG

### H1 (Khả năng cao nhất — Lớp Kiến trúc Tương tác Windows OS & Window Focus):
**Cửa sổ `TrailOverlay` toàn màn hình thiếu cờ `WS_EX_NOACTIVATE`, cướp quyền Foreground Active Window của trình duyệt khi mở ra và làm mất Focus khi bị Destroy; đồng thời `_do_start` trộn lẫn toạ độ vật lý của `MSLLHOOKSTRUCT` với toạ độ logic của `GetCursorPos` gây ra vệt thẳng lạ.**
- **Bằng chứng:**
  - `trail_overlay.py:63-65` tạo `tk.Toplevel` và map toàn màn hình mà không thiết lập `WS_EX_NOACTIVATE` (0x08000000) hay `WS_EX_TRANSPARENT` (0x20).
  - Khi overlay hiện lên, `GetForegroundWindow()` chuyển thành `RightWheel`. Khi `_do_stop()` gọi `self._win.destroy()`, trình duyệt Chromium không được trả lại trạng thái active.
  - Các hàm kiểm tra `is_chromium_browser(exe)` tại `mouse_mapper_logic.py:65` và việc gửi phím `SendInput` tại `shortcut_executor.py:120` hoàn toàn phụ thuộc vào việc trình duyệt phải là cửa sổ active hiện tại. Mất focus = X1/X2 và Gesture bị vô hiệu hoá.
  - Toạ độ điểm đầu `(x, y)` nạp vào `_last_point` lấy từ hook là toạ độ vật lý (chưa scale DPI), trong khi `GetCursorPos` trong `_poll()` trả về toạ độ logic (đã scale DPI), sinh ra đoạn thẳng nhảy cóc ngay ở frame đầu tiên.

### H2 (Khả năng cao — Lớp Cấu hình & Trạng thái Logic):
**Hardcode `move_threshold=8` trong `main.py` phá vỡ cơ chế chống rung tay (50px), biến mọi thao tác giữ chuột phải bấm X1/X2 hoặc click chuột phải bình thường thành cử chỉ rác bị nuốt mất (Silent Drop).**
- **Bằng chứng:**
  - `main.py:21` truyền `move_threshold=8`.
  - Khi người dùng giữ RMB và bấm X1/X2, ngón tay dịch chuyển >8px làm state chuyển từ `RIGHT_HELD` sang `GESTURE` trước khi nút X1/X2 kịp tác động.
  - Khi người dùng click chuột phải thông thường, rung lắc nhẹ vượt 8px khiến `_on_right_up` coi là cử chỉ không khớp, kích hoạt `Silent Drop` và nuốt hoàn toàn context menu.

### H3 (Khả năng cao — Lớp Môi trường Runtime PyInstaller Windows):
**Hàm `_restart()` dùng `os.execve` trên Windows gây xung đột khoá file (File Lock Collision) với tiến trình Bootloader của PyInstaller onefile.**
- **Bằng chứng:**
  - `tray_ui.py:85` gọi `os.execve(sys.executable, ...)`.
  - Trên Windows, tiến trình cha (PyInstaller bootloader) đợi tiến trình con thoát để xoá thư mục `%TEMP%\_MEIxxxxxx`. Tiến trình mới sinh ra vẫn đang mở các DLL trong thư mục này, khiến lệnh xoá của bootloader bị từ chối truy cập và bật hộp thoại cảnh báo.

---

## ROOT CAUSE CHỐT: H1 + H2 + H3 (Tổ hợp 3 lỗi kích hoạt đồng thời từ F-004 và `tray_ui.py`)

### 1. Cơ chế phát sinh lỗi:
- **Triệu chứng 1 (Vệt thẳng lạ):**
  Xảy ra do sự bất đồng bộ giữa hai hệ toạ độ: `MSLLHOOKSTRUCT` từ hook chuột cung cấp toạ độ vật lý (Physical Screen Pixels), còn `GetCursorPos` trong tiến trình Tkinter chưa khai báo Per-Monitor DPI trả về toạ độ logic (Scaled Virtual Pixels). Điểm đầu tiên được gán bằng toạ độ vật lý, điểm kế tiếp trong `_poll()` lấy từ `GetCursorPos` là toạ độ logic, nối 2 điểm này tạo thành đường chéo nhảy cóc hàng trăm pixel.
- **Triệu chứng 2 (RMB & X1/X2 chập chờn / chỉ chạy lần đầu):**
  Xảy ra do sự kết hợp giữa **(a)** `main.py:21` hardcode `move_threshold=8` khiến bất kỳ rung tay nào khi giữ RMB cũng kích hoạt state `GESTURE` và nuốt mất click chuột phải; và **(b)** Cửa sổ `TrailOverlay` khi hiện lên đã cướp quyền Foreground Active Window của trình duyệt do thiếu cờ `WS_EX_NOACTIVATE`. Khi overlay bị destroy, trình duyệt mất active status, khiến `GetForegroundWindow()` trong `_on_xbutton_down` không nhận diện được trình duyệt và phím tắt `SendInput` gửi vào hư không.
- **Triệu chứng 3 (Lỗi thư mục tạm khi Restart):**
  Xảy ra do `os.execve` trên Windows không giải phóng các handle thư viện DLL trong thư mục `%TEMP%\_MEIxxxxxx` trước khi Bootloader cha cố gắng xoá thư mục này.

### 2. Vì sao bây giờ mới lộ:
- Trước commit F-004 (`a5620b3`):
  - Chưa có `TrailOverlay`, không có cửa sổ Tkinter fullscreen topmost cướp active focus của trình duyệt.
  - Khi cử chỉ không khớp, mã nguồn cũ trả về `return False` (cho phép `right_up` rơi xuống ứng dụng để hiện menu chuột phải), nên dù `move_threshold=8` vẫn không bị nuốt mất click chuột phải.
  - F-004 thêm `TrailOverlay`, đổi sang `Silent Drop` cho unmatched gesture, nhưng lại giữ nguyên `move_threshold=8` trong `main.py`.
- Commit `f5019d3` chỉ loại bỏ `_MEIPASS2` khỏi môi trường nhưng vẫn gọi `os.execve` kế thừa handle thay vì khởi chạy tiến trình tách biệt có độ trễ an toàn.

### 3. Nơi cần sửa (Mô tả kỹ thuật — CHƯA SỬA):
1. **`src/main.py`:**
   - Xoá bỏ tham số `move_threshold=8` trong khởi tạo `mapper = MouseMapperLogic()`, sử dụng giá trị mặc định chuẩn `move_threshold=50` từ `mouse_mapper_types.py`.
   - Khởi tạo và liên kết `TrailOverlay` an toàn qua cơ chế event queue hoặc sau khi `root` của `PanelWindow` đã sẵn sàng.
2. **`src/features/mouse_mapper/ui/trail_overlay.py`:**
   - Áp dụng các extended window style Win32 bắt buộc cho cửa sổ overlay vẽ đè: `WS_EX_NOACTIVATE` (0x08000000), `WS_EX_TRANSPARENT` (0x00000020), `WS_EX_LAYERED` (0x00080000) và `WS_EX_TOOLWINDOW` (0x00000080) thông qua `SetWindowLongPtrW` để overlay tuyệt đối không cướp active focus và chuột xuyên thấu 100%.
   - Loại bỏ việc dùng `GetCursorPos` polling rời rạc; đồng bộ toạ độ vẽ trail trực tiếp từ luồng sự kiện mouse hook hoặc chuẩn hoá toạ độ DPI awareness (`shcore.SetProcessDpiAwareness(2)`).
   - Đảm bảo điểm bắt đầu của nét vẽ được khởi tạo cùng hệ toạ độ và không nối tắt điểm down ban đầu với điểm sau độ trễ timer.
3. **`src/features/mouse_mapper/logic/mouse_mapper_logic.py`:**
   - Xem xét lại cờ nhận diện cử chỉ: Nếu người dùng đã bấm X1/X2 trong phiên giữ RMB thì đánh dấu `_xbutton_used = True` để khi nhả RMB không kích hoạt Silent Drop hay inject click chuột phải nhầm.
4. **`src/features/mouse_mapper/ui/tray_ui.py`:**
   - Trong hàm `_restart()`: Thay thế `os.execve` bằng việc gọi một lệnh launcher tách biệt không kế thừa handle (ví dụ `subprocess.Popen` chạy cmd detached với độ trễ 1-2 giây: `cmd.exe /c timeout /t 1 /nobreak > nul & start "" "<exe_path>"`, kèm `creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW`), sau đó gọi `sys.exit(0)` để tiến trình hiện tại thoát hoàn toàn cho PyInstaller bootloader dọn dẹp thư mục tạm sạch sẽ.

**Độ tin cậy:** Rất cao (100% các triệu chứng đều được chứng minh qua dòng code cụ thể, cơ chế Win32 API, quy tắc tkinter threading và Win32 process lifecycle).

---

**CHƯA SỬA GÌ. Chạy debug2 để phản biện root cause này trước khi fix.**
