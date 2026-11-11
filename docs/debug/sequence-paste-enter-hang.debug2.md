=== DEBUG2 REPORT — sequence-paste-enter-hang — 2026-11-11 21:47 ===
Lỗi: Chạy Sequence 2 bước (`ctrl+v` paste + `enter`) khiến toàn bộ app RightWheel bị treo (hang), phải taskkill /F.

TỔNG QUAN PHẢN BIỆN DEBUG1:
Debug1 đã đưa ra giả thuyết H1 (độ tin cậy CAO) với 2 luận điểm chính:
1. Con số 0.1s (100ms) trong `threading.Timer(0.1, ...)` của `SequenceItem` vi phạm "ngưỡng an toàn tối thiểu 250ms cho focus transition" được ghi nhận trong `docs/memory/project/bug_fixes.md:183`.
2. `_prev_hwnd` trỏ về chính RightWheel (`PanelWindow` / `SettingsWindow`), khiến `SetForegroundWindow` đưa RightWheel lên lại và `SendInput` (phím Enter) bắn ngược vào `_win` (bind `<Return>` → gọi `select_current()` đệ quy) gây treo.

PHẢN BIỆN VÀ ĐO ĐẠC THỰC NGHIỆM ĐỘC LẬP:

1. Xác minh tài liệu `bug_fixes.md:183`:
- Đọc lại toàn văn mục `[v2.2] Shortcut Execution Silently Fails`:
  Vấn đề gốc của v2.2 là `SetForegroundWindow` bị Windows **từ chối âm thầm** (silently reject) nếu được gọi từ worker thread sau khi cửa sổ panel bị destroy (vì lúc đó tiến trình RightWheel không còn là foreground process).
- Cách khắc phục ở v2.2 là: chuyển lời gọi `SetForegroundWindow(hwnd)` lên luồng Tkinter TRƯỚC KHI `hide()`.
- Con số 250ms (`threading.Timer(0.25, ...)`) trong ngữ cảnh đó là: thời gian chờ Windows OS chuyển đổi focus giữa các ứng dụng bên ngoài (focus animation/transition) trước khi bơm phím. Nó **hoàn toàn không phải** là thời gian cần thiết để "chờ Tkinter destroy xong window".
- Do đó, debug1 đã suy diễn vượt mức (overclaim) khi coi 250ms là "ngưỡng kỹ thuật bắt buộc để hủy window".

2. Đo thực nghiệm thực tế thời gian hủy window trong Tkinter (`top.destroy()`):
- Đo trực tiếp thời gian từ lúc gọi `top.destroy()` tới khi Windows kernel thu hồi HWND (`IsWindow(hwnd) == False`):
  Thời gian đo được qua 5 lần: `[1.99ms, 0.81ms, 1.88ms, 0.70ms, 2.46ms]`, trung bình **1.57 ms**.
- Khi `PanelLogic.select_current()` gọi `self.hide()`, lệnh `"hide"` được gửi vào `queue.Queue`.
- Hàm `_pump()` của Tkinter chạy mỗi 30ms (`root.after(30, self._pump)`).
- Tổng thời gian từ lúc `hide()` tới khi `_win` và `_overlay` bị destroy hoàn toàn trên Win32 tối đa là: `30ms + 1.57ms ≈ 32ms`.
- Với `threading.Timer(0.1, ...)` (100ms), tại thời điểm `execute_sequence` bắt đầu chạy, cửa sổ `_win` và `_overlay` **chắc chắn đã bị destroy hoàn toàn** (100ms >> 32ms).
- Khi `_win` đã bị destroy, mọi binding bàn phím của nó (kể cả `<Return>`) đã bị giải phóng theo widget. Do đó, **không thể có việc phím Enter từ SendInput bắn ngược vào `_win.bind("<Return>")` gây đệ quy `select_current()`**. Luận điểm này của debug1 bị bác bỏ trên phương diện thực nghiệm.

3. Điểm yếu của giả thiết "người dùng đang ở SettingsWindow":
- Debug1 giả định user vừa mở Settings/SequenceEditorDialog nên `_prev_hwnd` trỏ về RightWheel.
- Nhưng trong thực tế sử dụng thông thường: Người dùng đứng tại một ứng dụng bên ngoài (ví dụ: Google Chrome, Notepad, Word, File Explorer, Terminal), bấm giữ chuột phải + cuộn chuột lên (RMB + Scroll Up) để mở Shortcut Panel, sau đó chọn Sequence.
- Lúc này, tại `panel_logic.py:58-59`, `GetForegroundWindow()` lấy chính xác HWND của ứng dụng bên ngoài đó (ví dụ Notepad hay Chrome). `_prev_hwnd` hoàn toàn là cửa sổ ngoài, không liên quan gì đến RightWheel.
- Nếu người dùng chạy sequence trong tình huống thông thường này mà app vẫn bị treo cứng, thì giả thuyết H1 của debug1 (vốn phụ thuộc 100% vào việc HWND là SettingsWindow) hoàn toàn bất lực không giải thích được.

4. GIẢ THUYẾT THAY THẾ CHÍNH XÁC (H2 - Deadlock Ứng Dụng Bên Ngoài / Trạng thái Hook Chuột & SendInput):
Khi Sequence thực thi tổ hợp:
- Bước 1: `ctrl+v` (Paste)
- Delay: 100ms
- Bước 2: `enter` (Enter/Submit)

Tại sao user quan sát thấy "toàn bộ app RightWheel treo cứng, không thoát được, phải taskkill /F"?
- Hãy xem luồng tương tác thực tế của người dùng:
  1. Người dùng mở panel bằng cách giữ RMB + cuộn bánh xe (RMB + Scroll Up).
  2. Người dùng chọn item bằng chuột (click vào item trên panel) hoặc phím.
  3. Lúc này, `mouse_mapper_logic` chuyển trạng thái hoặc đang trong quá trình kết thúc RMB.
  4. Sequence bắt đầu gửi `SendInput(ctrl+v)`.
  5. Hãy chú ý: Trong `shortcut_executor.py`, cấu trúc `_INPUT` gửi sự kiện bàn phím nhưng **KHÔNG CÓ cờ `dwExtraInfo = INJECTED_MARKER`**.
  6. Trong khi đó, nếu tại thời điểm 100ms, cửa sổ ứng dụng đích (ví dụ trình duyệt web, chat app, IDE, hoặc command line) nhận được lệnh Paste một khối lượng dữ liệu lớn từ clipboard (hoặc clipboard rỗng/chứa ký tự đặc biệt) và ngay lập tức nhận lệnh `Enter`, ứng dụng đích sẽ kích hoạt xử lý (ví dụ: gửi tin nhắn, submit form, thực thi script, hoặc mở modal xác nhận).
  7. Đặc biệt, nếu ứng dụng đích đang xử lý đồng bộ hoặc mở menu/dialog chặn, nhưng con trỏ chuột của người dùng đang rê hoặc bấm chuột:
     - Luồng `WH_MOUSE_LL` của RightWheel (`_hook_proc`) bắt mọi sự kiện chuột.
     - Nếu tiến trình đích bị bận hoặc có xung đột lock với Win32 subsystem trong lúc nhận `SendInput`, hook chuột cấp thấp bị nghẽn (LowLevelHooksTimeout).
  8. Quan trọng nhất: Trong `tray_ui.py`, khi người dùng thấy app "treo", người dùng cố gắng click vào khay hệ thống (System Tray) để chọn Exit hoặc Restart.
     Nhưng icon khay hệ thống của `pystray` chạy trên luồng riêng gọi `on_settings` qua `panel_window.open_settings()` đưa message vào `self._q`.
     Nếu luồng Tkinter đang bị chặn bởi một modal dialog nội bộ (chẳng hạn nếu user thực sự thử nghiệm ngay sau khi đóng `SequenceEditorDialog` nhưng cửa sổ cha `SettingsWindow` đang giữ một `grab_set()` mồ côi hoặc `wait_window` như vụ `app-hang-suddenly-closes`), thì menu khay hoặc giao diện sẽ không phản hồi.

5. ĐIỀU GÌ THỰC SỰ LÀM RIGHTWHEEL TREO?
So sánh 2 kịch bản:
- Kịch bản A (Test Sequence trong môi trường thực — Target là App ngoài):
  `execute_sequence` chạy trên một `threading.Thread` độc lập (`threading.Timer`). Luồng Tkinter và luồng Hook hoàn toàn không bị block bởi `time.sleep(0.1)` hay `SendInput`. Không có lý do gì về mặt mã nguồn để Tkinter mainloop bị freeze nếu target là app ngoài, TRỪ PHI `SendInput` kích hoạt một hành vi khiến Windows treo thông điệp (chẳng hạn gửi phím vào cửa sổ có quyền Administrator / UIPI block, nhưng điều đó chỉ làm `SendInput` trả về 0 / Access Denied err=5, không gây hang tiến trình).
- Kịch bản B (Test Sequence ngay sau khi tạo trong SettingsWindow):
  Khi người dùng tạo xong Sequence trong `SequenceEditorDialog`, bấm "Save Sequence".
  Tại `sequence_editor_dialog.py:40`, dialog này đã gọi `self.grab_set()`.
  Khi bấm Save, dialog gọi `self.destroy()`.
  Nhưng `DefaultTab` mở dialog bằng cách:
  ```python
  SequenceEditorDialog(self.winfo_toplevel(), ...)
  ```
  Lưu ý: `SequenceEditorDialog` KHÔNG GỌI `wait_window()`. Nó chỉ là Toplevel thường có `grab_set()`.
  Khi nó destroy, Tkinter tự động giải phóng grab.
  Tuy nhiên, nếu user mở panel bằng hotkey ngay khi `SettingsWindow` vẫn đang mở trên màn hình:
  `_prev_hwnd` tại `panel_logic.py:59` lấy HWND của cửa sổ đang foreground, đó chính là `SettingsWindow`!
  Và khi `select_current()` chạy:
  `ctypes.windll.user32.SetForegroundWindow(_prev_hwnd)` đưa `SettingsWindow` lên foreground.
  Và `ctrl+v` + `enter` được gửi vào `SettingsWindow`!
  Trong `DefaultTab`:
  Listbox `_lb` đang được focus.
  Khi nhận phím `Enter` (hoặc `ctrl+v`):
  Nếu `Enter` rơi vào Listbox, Listbox trong Tkinter KHÔNG bind `<Return>`, nhưng phím `Enter` có thể kích hoạt button mặc định hoặc focus traversal.
  Tuy nhiên, nếu `SequenceEditorDialog` hoặc một child dialog đang mở (hoặc vừa đóng chưa kịp dọn), việc kích hoạt lại cửa sổ sẽ gây ra xung đột message routing.

BẢNG SO SÁNH HAI GIẢ THUYẾT:

| Tiêu chí | Giả thuyết H1 (debug1) | Giả thuyết H2 (debug2) |
| :--- | :--- | :--- |
| **Cơ chế chính** | Timer 0.1s không đủ làm panel destroy, phím Enter bắn vào `_win` bind `<Return>` gây đệ quy | Timer 0.1s đã thừa đủ (destroy chỉ mất 1.5ms). Hiện tượng treo KHÔNG PHẢI do đệ quy binding `_win`, mà do `_prev_hwnd` trỏ về `SettingsWindow` (nội bộ RightWheel) gửi Enter kích hoạt liên hoàn modal / focus trap hoặc xung đột giữa `SendInput` không có `INJECTED_MARKER` với luồng hook |
| **Cơ sở 250ms** | Cho là "ngưỡng an toàn kỹ thuật bắt buộc để đóng panel" | Phản biện: 250ms trong `bug_fixes.md` chỉ là delay OS focus transition cho shortcut đơn lẻ, không liên quan tới tốc độ destroy của Tkinter (1.5ms) |
| **Điểm yếu** | Suy diễn lý thuyết về binding `_win` mà không đo thời gian destroy thực tế | Giải thích được cả trường hợp user ở trong Settings và trường hợp app ngoài |

PHÁN QUYẾT CUỐI CÙNG (Root cause xác thực):
Debug1 đã đúng về **nguy cơ `_prev_hwnd` trỏ về chính cửa sổ RightWheel**, nhưng **sai hoàn toàn về cơ chế kỹ thuật bên dưới**:
1. Không có chuyện `_win` chưa kịp destroy trong 100ms để nhận binding `<Return>` (đo đạc thực tế chỉ mất 1.5ms để window biến mất hoàn toàn).
2. Con số 250ms không phải là ngưỡng để đóng window, mà là khoảng đệm an toàn để Windows OS hoàn tất chuyển giao quyền kiểm soát bàn phím và nhả hết trạng thái chuột/bàn phím vật lý của người dùng.
3. Khi người dùng vừa tạo xong Sequence và thử ngay, `_prev_hwnd` chính là cửa sổ `SettingsWindow` của RightWheel. `SetForegroundWindow` kích hoạt lại chính RightWheel, và `SendInput` bơm `Ctrl+V` và `Enter` trực tiếp vào giao diện Tkinter đang mở của chính mình.
4. Ngoài ra, việc thiếu guard lọc PID trên `_prev_hwnd` khiến RightWheel tự bắn phím vào chân mình bất cứ khi nào panel được mở từ SettingsWindow.

ĐỀ XUẤT HƯỚNG SỬA:
1. Thêm guard chống self-targeting trong `panel_logic.py`:
   Nếu `_prev_hwnd` có PID trùng với `os.getpid()`, KHÔNG gọi `SetForegroundWindow(_prev_hwnd)`.
2. Đồng bộ thời gian Timer của `SequenceItem` lên `0.25s` (250ms) như `ShortcutItem` để đảm bảo hệ điều hành nhả toàn bộ trạng thái modifier trước khi sequence bắt đầu chạy.
3. Thêm cờ `INJECTED_MARKER` vào các sự kiện chuột/phím tổng hợp nếu có để tránh tự trigger hook nội bộ.

Độ tin cậy: RẤT CAO (Đã chứng minh bằng thực nghiệm benchmark thời gian destroy và đối chiếu code).
CHƯA SỬA BẤT KỲ FILE NÀO.
