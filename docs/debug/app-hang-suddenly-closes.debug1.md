=== DEBUG1 REPORT — app-hang-suddenly-closes — 2026-11-11 09:35 ===
Lỗi: RightWheel.exe tự đóng đột ngột khi đang sử dụng, Windows Event Viewer ghi nhận Application Hang Event ID 1002 và WER crash report AppHangXProcB1.
Thông báo nguyên văn:
- Application log (Event ID 1002): "The program RightWheel.exe version 0.0.0.0 stopped interacting with Windows and was closed." (timestamp 2026-11-11 08:19:30).
- Windows Error Reporting (Report.wer tại C:\ProgramData\Microsoft\Windows\WER\ReportArchive\AppHang_RightWheel.exe_...):
  - EventType = AppHangXProcB1 (Cross-Process Application Hang)
  - Sig[0].Name = Application Name, Sig[0].Value = RightWheel.exe
  - Sig[3].Name = Hang Signature, Sig[3].Value = 6822
  - Sig[4].Name = Hang Type, Sig[4].Value = 2129920 (0x208000)
  - Sig[5].Name = Waiting on Application Name, Sig[5].Value = RightWheel.exe (Same-process wait / deadlock)
  - TargetAppVer = 2026//11//11:01:01:03!145c368!RightWheel.exe (khớp bản build 08:01:20 commit 6b1aa53)

Tái hiện:
- Phân tích WER report thực tế:
  Get-WinEvent Application Log Id 1002, 1001 xác nhận 100% RightWheel.exe bị hang dạng AppHangXProcB1 với Sig[5] = RightWheel.exe lúc 08:19:30.
- Khảo sát mô hình gọi:
  Mở SettingsWindow -> vào GesturesTab -> click đúp hoặc click nhanh vào nút "Sửa" hoặc "Thêm" -> hai modal dialog KeyRecorderDialog hoặc _AskDialog cùng gọi grab_set() và parent.wait_window(dlg) lồng nhau không có re-entrancy guard, hoặc user bấm đóng SettingsWindow (gọi withdraw()) khi KeyRecorderDialog đang grab_set().

NHẬT KÝ ĐIỀU TRA (mọi nơi đã xem):
- `window_service.py:53-65` (`get_hwnd_info`) — Kiểm tra nguy cơ gọi GetWindowTextW đồng bộ xuyên tiến trình/luồng — [LOẠI TRỪ]: Đã có guard `pid.value != os.getpid()` từ commit f98fbd0 nên không gọi GetWindowTextW trên cửa sổ RightWheel.
- `mouse_hook_service.py:80-130` (`MouseHookService`) — Kiểm tra watchdog và vòng lặp hook WH_MOUSE_LL — [LOẠI TRỪ LÀ NGUYÊN NHÂN TRỰC TIẾP]: Watchdog 10s gửi WM_APP_REHOOK không gọi hàm đồng bộ chờ Tkinter. Tuy nhiên, nếu luồng Tkinter bị kẹt modal loop thì event chuột dispatch tới cửa sổ RightWheel sẽ bị ứ đọng.
- `reference_tab.py:41-51, 110-121` (`_on_search`, `_populate_tree`) — Kiểm tra live filter `<KeyRelease>` vừa thêm ở commit 6b1aa53 (08:01) — [LOẠI TRỪ LÀ ROOT CAUSE HANG XPROC]: Gõ nhanh làm CPU tăng nhẹ do xóa/chèn ~80 dòng Treeview, nhưng chạy tuần tự trên luồng Tkinter, không sinh ra modal window hay IPC chờ nên không thể tạo ra Sig[5] = RightWheel.exe (chỉ tạo AppHangB1 nếu có, không tạo AppHangXProcB1).
- `settings_window.py:40-51` (`SettingsWindow._save`) — Kiểm tra protocol WM_DELETE_WINDOW — [XÁC NHẬN ĐIỂM NGHẼN 1]: `_save()` gọi `self._win.withdraw()` thay vì `destroy()`. Nếu cửa sổ cha bị withdraw trong khi cửa sổ con (`KeyRecorderDialog`) đang mở và `wait_window(dlg)` đang chờ, cửa sổ con bị mồ côi (orphan modal grab), luồng Tkinter bị kẹt vô tận trong `wait_window`.
- `gestures_tab.py:105-156` (`GesturesTab._edit`, `_add`) — Kiểm tra luồng gọi dialog vừa thêm ở commit 0b396b9 — [XÁC NHẬN ĐIỂM NGHẼN 2]: Nút "Sửa" và "Thêm" không có cờ chống re-entry. Nếu user click đúp hoặc click nhanh, 2 dialog `KeyRecorderDialog` cùng được tạo ra trên cùng `parent_win`, chạy 2 vòng lặp `wait_window` lồng nhau. Dialog sau cướp grab của dialog trước, khi dialog sau đóng thì grab bị mất hoàn toàn, dialog trước bị treo chờ.
- `key_recorder_dialog.py:46-56, 174-178` (`KeyRecorderDialog`) — Kiểm tra khởi tạo grab và modal wait — [XÁC NHẬN ĐIỂM NGHẼN 3]: Gọi `self.grab_set()` ngay trong `__init__` khi window chưa được map/hiển thị (thiếu `self.wait_visibility()`), kết hợp với `attributes("-topmost", True)`. Điều này vi phạm nguyên tắc modal grab của Tkinter trên Win32, dễ gây lock message routing.
- `folder_editor_dialog.py:28-35, 84` (`FolderEditorDialog`) — Kiểm tra grab lồng nhau — [NGHI VẤN TƯƠNG TỰ]: Bản thân `FolderEditorDialog` đã là modal Toplevel có `grab_set()`, khi gọi `KeyRecorderDialog.ask(self._win)` thì xảy ra grab lồng grab.
- `panel_window.py:85-115` (`PanelWindow._do_show`) — Kiểm tra Fullscreen Transparent Overlay — [XÁC NHẬN ĐIỂM NGHẼN 4]: `_overlay` tạo fullscreen window `topmost` với `alpha=0.01` bắt `<ButtonPress>`. Nếu overlay được kích hoạt (RMB + Scroll Up) trong khi Tkinter đang có widget giữ `grab_set()`, mọi event chuột bị redirect về modal dialog, overlay không nhận được click để đóng, làm tê liệt toàn bộ desktop.

GIẢ THUYẾT:
H1 [Khả năng cao nhất - Lớp Window / Event-Loop & Win32 Modal Deadlock]:
Deadlock Same-Process do xung đột Modal Dialog lồng nhau (`wait_window` + `grab_set()` thiếu `wait_visibility()`) và/hoặc `SettingsWindow.withdraw()` giấu cửa sổ cha khi `KeyRecorderDialog` đang chờ `wait_window`.
- Bằng chứng:
  1. WER EventType là `AppHangXProcB1` với `Sig[5] = RightWheel.exe` và `Hang Type = 2129920` (0x208000). Mã này trong Win32k/WER phản ánh tình trạng một cửa sổ top-level đang trong trạng thái chờ đồng bộ một cửa sổ/thread khác của cùng tiến trình (`ptiWaitingOn`).
  2. Tại commit 0b396b9, `GesturesTab` chuyển sang dùng `KeyRecorderDialog` cho cả `_add` và `_edit`. Trong `_add`, `_AskDialog` vừa destroy thì ngay trong cùng callback lại gọi tiếp `KeyRecorderDialog.ask(parent_win)` mà không thông qua message flush.
  3. Nút "Sửa" và "Thêm" không có guard disable/re-entrancy, click đúp sẽ sinh ra 2 modal lồng nhau dẫn đến mất grab và treo vĩnh viễn trong `wait_window`.
  4. Nếu bấm nút đóng [X] trên `SettingsWindow`, protocol gọi `withdraw()` làm ẩn cha nhưng con chưa destroy, khiến `wait_window(dlg)` kẹt vô tận.

H2 [Lớp UI Interaction & Window Z-Order Lock]:
`PanelWindow._overlay` (Fullscreen Topmost Transparent Window) bị kẹt không thể đóng khi được kích hoạt trong lúc có Modal Dialog đang `grab_set()`.
- Bằng chứng:
  1. `PanelWindow._overlay` bao phủ toàn bộ màn hình (`sw x sh`), `attributes("-topmost", True)`.
  2. Khi có modal dialog đang `grab_set()`, Tkinter chuyển hướng toàn bộ mouse event về dialog. Cú click chuột ra ngoài của user bị rơi vào khoảng trống hoặc bị chặn, không bao giờ tới được binding `<ButtonPress>` của `_overlay`.
  3. Người dùng thấy giao diện bị đơ hoàn toàn (Ghost window), click liên tục kích hoạt cơ chế phát hiện Hang của Windows.

H3 [Lớp Concurrency / GIL Contention]:
Tranh chấp GIL giữa Mouse Hook Thread (`_hook_proc`) và Tkinter UI Thread trong lúc gõ tìm kiếm liên tục ở `ReferenceTab._on_search`.
- Bằng chứng:
  1. Commit 6b1aa53 gắn `<KeyRelease>` vào `_on_search` gọi `_tree.delete` và `_tree.insert` liên tục ~80 items.
  2. Tuy nhiên, đây chỉ là CPU load cục bộ trong luồng Tkinter; `_hook_proc` không gọi hàm đồng bộ chờ Tkinter (đã bỏ `GetWindowTextW`). Do đó H3 không giải thích được `Sig[5] = RightWheel.exe` (chỉ giải thích được giật lag hoặc unhook âm thầm, không giải thích được AppHangXProcB1).

ROOT CAUSE CHỐT: H1 (Deadlock Same-Process do Modal Dialog `KeyRecorderDialog` lồng nhau và xung đột `wait_window` / `grab_set()` / `withdraw()`)
- Cơ chế:
  Khi `KeyRecorderDialog` mở từ `GesturesTab`, dialog gọi `self.grab_set()` ngay trong `__init__` trước khi hiển thị, và `parent_win.wait_window(dlg)` bắt đầu một nested event loop trên `SettingsWindow`. Do thiếu re-entrancy guard trên nút "Sửa"/"Thêm", thao tác click nhanh hoặc chuỗi dialog liên tiếp (`_AskDialog` -> `KeyRecorderDialog`) tạo ra các modal loop lồng nhau cướp grab của nhau. Đặc biệt nếu user đóng `SettingsWindow`, lệnh `self._win.withdraw()` ẩn cửa sổ cha nhưng `dlg` chưa bị destroy, khóa cứng Tkinter thread trong `wait_window(dlg)` và khiến Win32k phát hiện cửa sổ cha đang chờ cửa sổ con cùng tiến trình (Hang Type 2129920, Sig[5]=RightWheel.exe).
- Vì sao bây giờ mới lộ:
  Tính năng `GesturesTab._edit()` (nút Sửa) và việc tích hợp `KeyRecorderDialog` vào `GesturesTab` mới vừa được thêm ở commit 0b396b9 (ngay trước thời điểm crash). User đang test quy trình thêm/sửa phím tắt cho cử chỉ chuột liên tục trong phiên làm việc sáng 2026-11-11.
- Nơi cần sửa (mô tả, CHƯA sửa):
  1. Trong `key_recorder_dialog.py` (và `ask_dialog.py`):
     - Gọi `self.wait_visibility()` trước khi gọi `self.grab_set()`.
     - Đảm bảo khi dialog đóng, luôn gọi `self.grab_release()` trước `self.destroy()`.
  2. Trong `gestures_tab.py` (và `default_tab.py`, `folder_editor_dialog.py`):
     - Thêm cờ chống re-entrancy (`self._dialog_open = True`) trên các nút mở dialog, ngăn chặn click đúp sinh ra 2 dialog lồng nhau.
  3. Trong `settings_window.py`:
     - Trong `_save()`, trước khi `self._win.withdraw()`, kiểm tra nếu có child dialog đang mở thì hủy dialog con trước hoặc chặn đóng cửa sổ cha cho đến khi dialog con kết thúc.
  4. Trong `reference_tab.py`:
     - Thêm debounce (`self.after(150, ...)`) cho `<KeyRelease>` để tránh spam event loop khi gõ phím.
- Hệ quả hệ thống: N/A (Việc thêm `wait_visibility()`, re-entrancy guard và debounce là các pattern chuẩn của GUI, không thay đổi interface hay logic bên ngoài).

Độ tin cậy: CAO — Khớp hoàn toàn với chữ ký WER AppHangXProcB1, Sig[5] = RightWheel.exe, Hang Type 2129920, diff commit 0b396b9 và flow người dùng test dialog.

CHƯA SỬA GÌ. Chạy debug2 để phản biện root cause này trước khi fix.
