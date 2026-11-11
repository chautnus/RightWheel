=== DEBUG1 REPORT — sequence-paste-enter-hang — 2026-11-11 21:42 ===
Lỗi: Chạy Sequence 2 bước (`ctrl+v` paste + `enter`) từ Shortcut Panel khiến toàn bộ app RightWheel treo (hang), không thoát được, phải taskkill /F. Windows Event Viewer chưa kịp ghi Application Hang (không phải crash tức thì, mà là UI/process kẹt cứng).

Tái hiện bằng suy luận logic:
1. User vừa trong SettingsWindow tạo/sửa Sequence (hoặc click vào Settings/dialog).
2. Khi Shortcut Panel được kích hoạt (RMB + Scroll Up), `PanelLogic.show()` lưu `self._prev_hwnd = ctypes.windll.user32.GetForegroundWindow()`.
   - Nếu user mở panel ngay khi SettingsWindow/SequenceEditorDialog vừa active, `_prev_hwnd` chính là HWND của SettingsWindow hoặc SequenceEditorDialog.
3. User chọn item Sequence (bấm Enter hoặc click chuột).
4. `PanelLogic.select_current()` thực thi:
   - `ctypes.windll.user32.SetForegroundWindow(hwnd)` đưa chính cửa sổ của RightWheel lên lại foreground.
   - `self.hide()` gửi lệnh hide vào queue Tkinter.
   - `threading.Timer(0.1, shortcut_executor.execute_sequence, args=[item.steps]).start()` kích hoạt worker thread sau 100ms.
5. Sau 100ms, worker thread gọi:
   - `execute('ctrl+v')`: `SendInput` bơm keypress Ctrl+V vào message queue của cửa sổ đang active.
   - Sleep 100ms (`delay_ms=100`).
   - `execute('enter')`: `SendInput` bơm keypress Enter vào message queue.
6. Hậu quả kép dẫn đến Treo cứng:
   - Nếu `_prev_hwnd` trỏ về Shortcut Panel / Settings:
     - `panel_window.py:105`: `self._win.bind("<Return>", lambda _: self._logic.select_current())`. Phím Enter tổng hợp bị bắt lại bởi chính binding `<Return>` của PanelWindow (nếu chưa kịp đóng) hoặc kích hoạt nút mặc định trên Tkinter focus widget.
     - Trong `SequenceEditorDialog` / `SettingsWindow`, phím `Enter` kích hoạt Save/OK hoặc Listbox selection, mở tiếp child dialog hoặc modal loop khi trạng thái focus chưa ổn định.
   - Nhưng ĐIỂM NGHẼN CỐT LÕI (Root Cause):
     Khác với `ShortcutItem` (`threading.Timer(0.25, ...)` cho 250ms để OS hoàn tất focus transition và nhả các phím chuột RMB/chờ panel ẩn hoàn toàn), `SequenceItem` chỉ delay 100ms (`Timer(0.1, ...)`). Tại thời điểm 100ms, tiến trình Tkinter đang bận xử lý `_do_hide()` (hủy `_overlay` và `_win`), chuột vật lý hoặc cửa sổ đích chưa hoàn tất focus handoff. Khi `SendInput` bơm liên tiếp `ctrl+v` và `enter`, nếu phím Ctrl hoặc Enter bị kẹt trạng thái modifier hoặc rơi vào message pump của luồng Tkinter RightWheel đang grab/topmost, luồng message loop bị block hoặc đệ quy re-entrant event dispatch.

NHẬT KÝ ĐIỀU TRA (mọi nơi đã xem):
- `src/features/shortcut_panel/logic/panel_logic.py:58-60, 112-132` (`show()`, `select_current()`) — Khảo sát cách lưu `_prev_hwnd` và delay timer. Phát hiện `ShortcutItem` dùng delay `0.25s` (đã được ghi nhận trong architecture/bug_fixes là ngưỡng an toàn tối thiểu cho focus transition), trong khi `SequenceItem` dùng `0.1s`.
- `src/features/shortcut_panel/services/shortcut_executor.py:91-124, 206-237` (`execute()`, `execute_sequence()`) — Đã kiểm tra cấu trúc `_INPUT` 64-bit và logic lặp `time.sleep()`. SendInput chạy trên worker thread tách biệt (không block main thread trực tiếp), nhưng nếu gửi phím vào chính tiến trình mẹ khi cửa sổ cha chưa sẵn sàng thì tạo ra re-entrant event storm.
- `src/features/shortcut_panel/ui/panel_window.py:90-120` (`_do_show()`, `_do_hide()`) — Xem xét binding `<Return>` tại dòng 105. `self._win.bind("<Return>", lambda _: self._logic.select_current())`. Nếu phím Enter của sequence bắn ngược vào `_win` trước khi `_win` bị destroy hoàn toàn, `select_current()` bị gọi đệ quy lần 2.
- `src/features/shortcut_panel/ui/default_tab.py:47` & `default_tab_crud.py:91-126` — Kiểm tra binding `<Double-Button-1>` và dialog guards. Đã có `_dialog_open` guard.
- `src/features/shortcut_panel/ui/settings_window.py:48-59` — Kiểm tra `_save()` và child dialog cleanup.
- `src/features/shortcut_panel/ui/key_recorder_dialog.py:46-56, 175-178` & `sequence_editor_dialog.py:28-42` — Kiểm tra modal grab. `SequenceEditorDialog` có `self.grab_set()`.

GIẢ THUYẾT:
H1 [Khả năng cao nhất - Race Condition Focus Transition & Self-Inflicted Enter Re-entrancy Loop]:
Delay kích hoạt của Sequence chỉ là 0.1s (thay vì 0.25s như ShortcutItem chuẩn trong kiến trúc RightWheel). Trong 100ms, cửa sổ `PanelWindow` chưa kịp unmap/destroy hoàn toàn khỏi Windows desktop, và `_prev_hwnd` (hoặc con trỏ focus của Windows) vẫn đang nằm ở RightWheel (`_win` hoặc `SettingsWindow`). Khi `execute_sequence` gửi `ctrl+v` rồi `enter` sau 100ms:
1. Phím `Enter` bắn trực tiếp vào `_win`, kích hoạt lại binding `<Return>` (`panel_logic.select_current()`) đệ quy.
2. Hoặc `SetForegroundWindow(_prev_hwnd)` kích hoạt lại `SettingsWindow` / `SequenceEditorDialog`, và phím `Enter` kích hoạt nút Save/Edit liên tục tạo ra xung đột modal/event deadlock giữa worker thread và Tkinter main loop.
- Bằng chứng code:
  - `panel_logic.py:119`: `ShortcutItem` dùng `threading.Timer(0.25, self._fire, args=[item.keys]).start()` — Tài liệu `docs/memory/project/bug_fixes.md:183` ghi rõ: *"Sau đó 250ms delay cho focus transition hoàn tất trước khi SendInput"*.
  - `panel_logic.py:130`: `SequenceItem` dùng `threading.Timer(0.1, shortcut_executor.execute_sequence, ...).start()` — Vi phạm quy tắc 250ms focus transition!
  - `panel_window.py:105`: `self._win.bind("<Return>", lambda _: self._logic.select_current())` — Nếu `_win` chưa bị destroy trong 100ms (do queue Tkinter trễ), `enter` từ SendInput sẽ kích hoạt `select_current()` đệ quy vô tận.

H2 [SendInput Modifier State Jam / Raw Input Deadlock]:
Khi gửi `ctrl+v`, tổ hợp `Ctrl` down -> `V` down -> `V` up -> `Ctrl` up được gửi bằng `SendInput`. Nhưng nếu phím Enter được gửi ngay sau đó 100ms khi người dùng vẫn đang đè chuột phải (RMB) hoặc một phím vật lý khác chưa nhả, cờ modifier `Ctrl` hoặc `RMB` bị kẹt trong OS message queue, làm các hook chuột cấp thấp (`WH_MOUSE_LL`) và message pump của Tkinter bị nghẽn (không pump được message).
- Bằng chứng:
  - Trong `execute_sequence`, mỗi bước có `delay_ms` mặc định là 100ms, nhưng giữa các bước không có cơ chế đồng bộ kiểm tra trạng thái modifier nhả hoàn toàn.

H3 [Self-Targeting vào Settings Listbox]:
Nếu user vừa đóng SettingsWindow hoặc mở panel ngay trên SettingsWindow, `_prev_hwnd` là HWND của Settings. `SetForegroundWindow` đưa Settings lên trước, `ctrl+v` paste text vào widget đang active, sau đó `enter` kích hoạt double click / edit item, dẫn đến mở lại `SequenceEditorDialog` modal trong khi tiến trình đang bận.

ROOT CAUSE CHỐT: H1 (Vi phạm ngưỡng an toàn focus transition: Timer Sequence dùng 0.1s thay vì 0.25s, kết hợp với việc `_prev_hwnd` có thể trỏ về chính cửa sổ RightWheel, khiến SendInput (đặc biệt là phím Enter) bị bắn ngược vào PanelWindow/SettingsWindow trước khi panel đóng hoàn toàn).

Nơi cần sửa (mô tả, CHƯA sửa):
1. Trong `src/features/shortcut_panel/logic/panel_logic.py`:
   - Dòng 130: Đổi `threading.Timer(0.1, ...)` của `SequenceItem` thành `threading.Timer(0.25, ...)` đồng bộ với `ShortcutItem` (đảm bảo đủ 250ms cho focus transition và panel destroy hoàn tất).
   - Dòng 58-60 & 114-116: Thêm kiểm tra PID cho `_prev_hwnd`. Nếu `_prev_hwnd` thuộc về chính tiến trình RightWheel (`os.getpid()`), KHÔNG gọi `SetForegroundWindow` hoặc tìm cửa sổ bên dưới, tránh tự kích hoạt lại giao diện của chính mình và tự nhận keystroke.
2. Trong `src/features/shortcut_panel/ui/panel_window.py`:
   - Hủy bỏ các binding bàn phím ngay khi bắt đầu `_do_hide()` để tránh nhận keystroke tổng hợp trong lúc chờ destroy.

Độ tin cậy: CAO.
CHƯA SỬA GÌ. Đề xuất chạy debug2 để phản biện góc nhìn khác trước khi sửa.
