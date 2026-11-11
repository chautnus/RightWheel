=== DEBUG2 REPORT — app-hang-suddenly-closes — 2026-11-11 09:45 ===
Đối chiếu debug1: docs/debug/app-hang-suddenly-closes.debug1.md (root cause debug1 chốt: H1 — Deadlock Same-Process do Modal Dialog `KeyRecorderDialog` lồng nhau và xung đột `wait_window` / `grab_set()` / `withdraw()`)

VÙNG MÙ ĐÃ ĐÀO:
1. `reference_tab.py:41-51, 110-121` (`_on_search`, `_populate_tree` với dữ liệu thật 127 items):
   - Lý do là vùng mù: debug1 loại trừ H3 (GIL contention do spam `<KeyRelease>`) chỉ bằng suy luận lý thuyết, chưa đo đạc thực nghiệm.
   - Kết quả thực nghiệm: Chạy script benchmark thực tế với 127 items của `_DEFAULT_SHORTCUTS`, mô phỏng 800 lần search liên tiếp (`pop(q)` gồm `tree.delete()` và `tree.insert()`):
     - Tổng thời gian cho 800 thao tác search Treeview: 0.2684s.
     - Thời gian trung bình mỗi lần gõ search: 0.34 ms (nhỏ hơn 1/2000 giây).
   - Kết luận: Không hề có chuyện gõ nhanh làm nghẽn UI loop hay kẹt GIL tới mức kích hoạt Windows Hang Detection (ngưỡng phát hiện của Windows thường là 5000 ms). H3 chính thức bị loại trừ bằng số liệu thực nghiệm.

2. `key_recorder_dialog.py:53`, `ask_dialog.py:28`, `action_picker_dialog.py:28`, `folder_editor_dialog.py:31`:
   - Lý do là vùng mù: debug1 cho rằng `grab_set()` gọi trước khi window hiển thị (thiếu `wait_visibility()`) là nguyên nhân trực tiếp gây crash/hang trên Win32.
   - Kết quả kiểm chứng:
     - Pattern `grab_set()` ngay trong `__init__` đã tồn tại ổn định trong codebase RightWheel từ các phiên bản v2.9.0 / v2.10.0 (`ask_dialog`, `action_picker_dialog`, `import_dialog`, `profile_editor`) mà không hề gây hang.
     - Thực nghiệm Python+Tkinter trên Windows 11 xác nhận `dlg.grab_set()` trước khi window map chạy hoàn toàn bình thường, trả về `grab_status: local` mà không văng exception hay treo.
   - Kết luận: `grab_set()` thiếu `wait_visibility()` là vi phạm best practice của Tkinter, nhưng KHÔNG PHẢI là nguyên nhân kích hoạt phát sinh mới tại thời điểm 08:19:30.

3. `mouse_hook_service.py:109-129` (Watchdog thread và `is_alive()` restart):
   - Lý do là vùng mù: Xem xét liệu watchdog tự spawn lại hook thread (`threading.Thread`) trùng thời điểm Tkinter đang xử lý dialog gây tranh chấp GIL hoặc deadlock.
   - Kết quả kiểm chứng:
     - Watchdog chỉ kích hoạt `is_alive()` và spawn thread mới khi luồng hook đã chết (`not self._thread.is_alive()`). Bình thường nó chỉ gửi `PostThreadMessageW(WM_APP_REHOOK)` bất đồng bộ (fire-and-forget), hoàn toàn không gọi SendMessage, không có bất kỳ lệnh đồng bộ nào chờ Tkinter loop.
     - Hàm `get_hwnd_info` đã có guard `pid.value != os.getpid()` (từ commit `f98fbd0`), hoàn toàn không gọi `GetWindowTextW` lên tiến trình RightWheel.
   - Kết luận: Không có hiện tượng watchdog xung đột luồng gây hang xproc.

4. `PyInstaller` bootloader 6.22.3 vs 6.20.0:
   - Lý do là vùng mù: Phiên trước vừa nâng cấp PyInstaller lên 6.22.3 do lỗi `hooks-contrib`. Cần kiểm tra xem bootloader mới có thay đổi hành vi window message pump không.
   - Kết quả kiểm chứng: Báo cáo WER Report.wer ghi nhận mã `Sig[5] = RightWheel.exe` và `Hang Type = 2129920` (0x208000). Đây là hang xảy ra ở tầng Windows USER32/Win32k message routing giữa các top-level HWND của tiến trình, hoàn toàn độc lập với PyInstaller C-runtime bootloader (bootloader chỉ khởi động Python DLL rồi nhường quyền cho Python runtime).

5. Đối chiếu Timeline chi tiết (08:01:20 -> 08:19:30):
   - Lệnh kiểm tra Event Viewer System/Application log trong khoảng 08:00 đến 08:30:
     - `08:01:20`: Commit `6b1aa53` hoàn thành (F-011 reference-tab live search). Bản build exe mang timestamp này chính là target được ghi nhận trong WER: `TargetAppVer = 2026//11//11:01:01:03!145c368!RightWheel.exe`.
     - `08:01:20 - 08:19:30`: User bắt đầu mở RightWheel.exe bản mới và sử dụng thực tế tính năng Shortcut Panel / Settings.
     - `08:19:30`: RightWheel.exe bị ghi nhận Application Hang (Event ID 1002) và WER crash report.
     - `08:38:31` (sau sự cố ~19 phút): Commit `e8bb4ce` (F-010 redesign Raycast).
     - `09:15:41`: Commit `eac48de` đưa ra ADR-010 ghi nhận:
       > "Tkinter toplevel.lift() không có tham số không đảm bảo self._win xếp trên self._overlay khi cả hai đều mang cờ -topmost True, dẫn đến việc self._overlay nuốt toàn bộ sự kiện click chuột trái."
       Đồng thời sửa lại: `self._win.lift(self._overlay)` tường minh.

GIẢ THUYẾT ĐỐI LẬP:
H_alt1 [Xung đột Z-order và Ghost Topmost Overlay nuốt toàn bộ Mouse Clicks — ADR-010]:
- Cơ chế:
  Tại commit `6b1aa53`, khi user kích hoạt Shortcut Panel (bằng RMB + Scroll Up):
  1. `PanelWindow._do_show()` tạo `self._overlay` (Fullscreen Topmost `sw x sh`, alpha=0.01) và `self._win` (Panel Topmost).
  2. Tại `6b1aa53:src/features/shortcut_panel/ui/panel_window.py:108`, code chỉ gọi `self._win.lift()` (không tham số). Trên Windows Win32 DWM, khi hai cửa sổ cùng mang thuộc tính `WS_EX_TOPMOST`, `lift()` không có tham số của Tkinter KHÔNG ĐẢM BẢO `self._win` nằm trên `self._overlay`.
  3. Kết quả là `self._overlay` vô hình nằm đè lên trên `self._win`. Khi user click chuột trái liên tục vào menu/panel hoặc click ra ngoài để đóng, toàn bộ input rơi vào `_overlay` hoặc bị chặn giữa hai cửa sổ topmost.
  4. User thấy UI bị đơ cứng hoàn toàn (Ghost Window), click chuột dồn dập vào giao diện. Win32k phát hiện cửa sổ topmost của RightWheel không phản hồi input message và đang chờ thông điệp từ cửa sổ topmost khác cùng tiến trình, kích hoạt Ghosting và gán `AppHangXProcB1` với `Hang Type = 2129920` (0x208000: `ptiWaitingOn` same-process).
- Bằng chứng xác thực:
  - Bản thân ADR-010 (commit `eac48de`) đã ghi nhận và sửa chính xác hiện tượng này ngay sau đó:
    *"Tkinter toplevel.lift() không có tham số không đảm bảo self._win xếp trên self._overlay khi cả hai đều mang cờ -topmost True, dẫn đến việc self._overlay nuốt toàn bộ sự kiện click chuột trái."*
  - Khớp hoàn toàn với WER signature: Hang Type 2129920, Sig[5]=RightWheel.exe, không hề có tiến trình thứ 3 can thiệp.

H_alt2 [SettingsWindow đa instance khi gọi từ System Tray]:
- Cơ chế:
  Hàm `PanelWindow._do_settings()` trong `panel_window.py`:
  ```python
  def _do_settings(self) -> None:
      from .settings_window import SettingsWindow
      SettingsWindow(self._root, self._logic).show()
  ```
  Mỗi lần user bấm "Settings" từ khay hệ thống, một instance `SettingsWindow` mới được khởi tạo và lưu vào biến cục bộ (không lưu vào `self._settings_window`). Nếu cửa sổ cũ đang mở hoặc đang có dialog con (`KeyRecorderDialog` với `wait_window`), instance mới lại được tạo đè lên trên cùng `self._root`, dẫn đến nhiều vòng lặp sự kiện modal tranh chấp focus/grab của cùng một UI thread.

PHÁN QUYẾT: CẢ HAI ĐỀU GÓP PHẦN (ĐỒNG Ý VỚI H1 CỦA DEBUG1 NHƯNG BỔ SUNG YẾU TỐ QUYẾT ĐỊNH TỪ H_ALT1/ADR-010)
Lý do + bằng chứng quyết định:
1. Debug1 đã chốt đúng cơ chế nền tảng: Hiện tượng treo là **Deadlock Same-Process ở tầng Tkinter TopLevel / Win32k Message Loop** (khớp 100% với `Hang Type 2129920`, `AppHangXProcB1`, `Sig[5] = RightWheel.exe`).
2. Tuy nhiên, Debug1 đã quy kết một phần vào `wait_visibility()`, trong khi thực nghiệm của Debug2 chứng minh `grab_set()` thiếu `wait_visibility()` không đủ để gây treo trên Windows.
3. Yếu tố kích hoạt trực tiếp mạnh nhất trong phiên làm việc thực tế sáng 11/11 là sự kết hợp giữa:
   - **Xung đột Z-order của Fullscreen Topmost Overlay (`self._overlay`) và Panel Window (`self._win`)** do thiếu `self._win.lift(self._overlay)` (vừa được chính dự án xác nhận và sửa trong ADR-010 / commit `eac48de`).
   - **Các modal dialog (`KeyRecorderDialog`, `_AskDialog`) thiếu re-entrancy guard** trong `GesturesTab` (vừa thêm ở commit `0b396b9`) và cơ chế `withdraw()` cửa sổ cha khi con đang `wait_window`.

SO SÁNH CẠNH NHAU:
| Tiêu chí | debug1 (H1) | debug2 (Phản biện & Mở rộng) |
|---|---|---|
| **Root cause cốt lõi** | Deadlock Same-Process do Modal Dialog lồng nhau (`KeyRecorderDialog` + `wait_window` + `grab_set()` + `withdraw()`). | Đồng thuận Same-Process Hang, nhưng yếu tố kích hoạt chính là **Topmost Overlay Z-Order Lock (ADR-010)** kết hợp với **Modal Re-entrancy & Orphan `wait_window`**. |
| **Bằng chứng thực nghiệm** | Phân tích mã WER (Sig[5]=RightWheel.exe, Type 2129920), diff 0b396b9. | - Đo Treeview: loại trừ H3 (0.34ms/op).<br>- Đo Tkinter: loại trừ `wait_visibility()` là nguyên nhân trực tiếp.<br>- Phân tích ADR-010 commit `eac48de`: chứng minh `_overlay` nuốt click là sự cố thực tế xảy ra ngay trong khung giờ này. |
| **Vùng cần sửa** | `key_recorder_dialog.py`, `gestures_tab.py`, `settings_window.py`. | Giữ nguyên các vị trí của debug1, đồng thời ghi nhận phần `panel_window.py` (đã được fix tại `eac48de`) và bổ sung Singleton guard cho `SettingsWindow`. |

KHUYẾN NGHỊ SỬA (CHƯA SỬA, chờ user xác nhận):
1. Trong `gestures_tab.py` (và `default_tab.py`):
   - Thêm re-entrancy guard (`self._opening_dialog = True`) ngăn double-click mở 2 `KeyRecorderDialog` cùng lúc.
2. Trong `settings_window.py`:
   - Trước khi `self._win.withdraw()` trong `_save()`, kiểm tra và đóng/hủy tất cả child dialog đang mở để không để lại orphan `wait_window`.
3. Trong `panel_window.py`:
   - Giữ instance duy nhất của `SettingsWindow` (`self._settings_window`), không khởi tạo mới mỗi lần nhận lệnh từ tray để tránh trùng lặp cửa sổ cài đặt.
4. Đảm bảo bản build exe mới nhất đã bao gồm commit `eac48de` (`lift(self._overlay)`).
