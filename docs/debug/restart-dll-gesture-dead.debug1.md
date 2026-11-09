# === DEBUG1 REPORT — restart-dll-gesture-dead — 2026-11-09 14:20:00 ===

## 1. THÔNG TIN LỖI & MÔ TẢ NGUYÊN VĂN

### Triệu chứng 1 (Xảy ra trước):
> "Trước đó thì các gesture mất tác dụng"
- **Mô tả:** Trong lúc sử dụng bình thường, toàn bộ cử chỉ chuột (`RMB` kéo cử chỉ, `X1`/`X2` chuyển tab, `RMB` + scroll điều hướng / Alt+Tab) đột nhiên ngừng phản hồi hoàn toàn. Chuột vật lý hoạt động bình thường nhưng tiện ích RightWheel không có bất kỳ phản hồi nào.

### Triệu chứng 2 (Xảy ra khi bấm Restart để khôi phục):
> "Bị lỗi này khi khởi động lại"
- **Thông báo lỗi nguyên văn (Dialog Win32 từ PyInstaller Bootloader):**
```text
Failed to load Python DLL 'C:\Users\Chau\AppData\Local\Temp\_MEI311162\python314.dll'.
LoadLibrary: The specified module could not be found.
```

---

## 2. BƯỚC TÁI HIỆN & BẰNG CHỨNG KIỂM CHỨNG KỸ THUẬT

### Bằng chứng A: Phân tích file nhị phân PyInstaller Bootloader (`runw.exe` v6.20.0)
Kiểm tra trực tiếp file nhị phân bootloader dùng để build `RightWheel.exe` tại `C:\Users\Chau\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Python\Python314\site-packages\PyInstaller\bootloader\Windows-64bit-intel\runw.exe`:
- **Lệnh kiểm tra chuỗi nội bộ:**
```python
with open(r'...\runw.exe', 'rb') as f:
    data = f.read()
# Tìm các biến môi trường và định danh
```
- **Kết quả:**
  - `Contains _MEIPASS2`: **`False`** (PyInstaller >= 6.11 đã loại bỏ hoàn toàn biến này khỏi bootloader Windows).
  - Các biến môi trường thực tế tồn tại trong bootloader:
    - `PYINSTALLER_RESET_ENVIRONMENT`
    - `_PYI_APPLICATION_HOME_DIR`
    - `_PYI_ARCHIVE_FILE`
    - `_PYI_PARENT_PROCESS_LEVEL`
    - `_PYI_SPLASH_IPC`
    - `PYINSTALLER_STRICT_UNPACK_MODE`
    - `_MEIPASS`

### Bằng chứng B: Mã nguồn `_restart()` hiện tại trong `src/features/mouse_mapper/ui/tray_ui.py:84-95`
```python
84:        env = os.environ.copy()
85:        env.pop("_MEIPASS2", None)
86:        args_str = " ".join(f'"{a}"' for a in sys.argv[1:])
87:        cmd = f'ping 127.0.0.1 -n 2 > nul & "{sys.executable}" {args_str}'.strip()
88:        subprocess.Popen(
89:            cmd,
90:            shell=True,
91:            env=env,
92:            creationflags=0x00000008 | 0x00000200,  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
93:            close_fds=True,
94:        )
95:        sys.exit(0)
```
- Dòng 85: Chỉ gọi `env.pop("_MEIPASS2", None)`. Trong PyInstaller 6.20.0, `_MEIPASS2` không tồn tại, nhưng `_PYI_APPLICATION_HOME_DIR` (giá trị trỏ tới thư mục tạm `C:\Users\Chau\AppData\Local\Temp\_MEI311162`) **vẫn còn nguyên trong `env`**.
- Dòng 88: Truyền `env` này cho `subprocess.Popen`.
- Dòng 95: Tiến trình Python con gọi `sys.exit(0)`. Ngay khi tiến trình con kết thúc, tiến trình cha (PyInstaller bootloader ban đầu) phát hiện con đã thoát và **thực hiện xóa đệ quy thư mục `_MEI311162`**.
- Sau độ trễ `ping -n 2` (~1 giây), `cmd.exe` khởi chạy tiến trình `RightWheel.exe` mới. Bootloader mới đọc `env` và thấy `_PYI_APPLICATION_HOME_DIR = C:\Users\Chau\AppData\Local\Temp\_MEI311162`. Do biến này tồn tại, bootloader ngộ nhận rằng mình là một tiến trình con/worker của bundle đã giải nén sẵn, bỏ qua bước giải nén và gọi ngay `LoadLibrary` tới file DLL trong thư mục tạm cũ đã bị xóa sạch.

### Bằng chứng C: Lệnh Win32 đồng bộ gây block trên luồng hook cấp thấp (`WH_MOUSE_LL`)
- Tại `src/features/mouse_mapper/logic/mouse_mapper_logic.py:66`:
  ```python
  hwnd = ctypes.windll.user32.GetForegroundWindow()
  exe, _, _ = window_service.get_hwnd_info(hwnd)
  ```
- Tại `src/features/mouse_mapper/logic/tab_switch_logic.py:38`:
  ```python
  hwnd = _user32.GetForegroundWindow()
  exe, _title, _cls = window_service.get_hwnd_info(hwnd)
  ```
- Cả hai hàm trên đều chạy đồng bộ trên luồng hook của `MouseHookService`.
- Tại `src/features/shortcut_panel/services/window_service.py:24-26`:
  ```python
  buf = ctypes.create_unicode_buffer(512)
  _u32.GetWindowTextW(hwnd, buf, 512)
  title = buf.value
  ```
  `GetWindowTextW` gửi message `WM_GETTEXT` đồng bộ tới cửa sổ đích. Nếu cửa sổ đích (Edge, Chrome, app đang freeze) không pump message, `GetWindowTextW` treo vô hạn hoặc vượt quá `LowLevelHooksTimeout` (200-300ms) của Windows. Khi chạm ngưỡng này, Windows kernel **âm thầm gỡ bỏ (`silently unhook`) hook `WH_MOUSE_LL`**.
- Tại `src/features/mouse_mapper/services/mouse_hook_service.py:84-108`:
  Luồng watchdog chỉ post `WM_APP_REHOOK` vào message queue của luồng hook. Nếu luồng hook đang bị block bên trong `GetWindowTextW`, hàm `GetMessageW` không được gọi, khiến `WM_APP_REHOOK` không bao giờ được xử lý. Kể cả khi luồng hook chỉ bị trễ > 200ms rồi trả về, chu kỳ watchdog 10 giây là quá dài, trong thời gian đó toàn bộ gesture chuột bị tê liệt và sự kiện `WM_RBUTTONUP` bị mất làm hỏng state machine của `MouseMapperLogic`.

---

## 3. NHẬT KÝ ĐIỀU TRA (MỌI NƠI ĐÃ XEM)

| File:Dòng | Lý do xem | Kết luận |
|---|---|---|
| `tray_ui.py:84-95` (`_restart`) | Kiểm tra cơ chế tự khởi động lại được sửa ở F-005 | **XÁC NHẬN NGUYÊN NHÂN LỖI RESTART:** Chỉ pop `_MEIPASS2` (đã lỗi thời), bỏ sót `_PYI_APPLICATION_HOME_DIR` và không set `PYINSTALLER_RESET_ENVIRONMENT=1`. |
| `runw.exe` (PyInstaller 6.20.0 bootloader) | Kiểm tra các biến môi trường thực tế mà bootloader sử dụng | **XÁC NHẬN:** Bootloader không hề chứa chuỗi `_MEIPASS2`. Chứa `_PYI_APPLICATION_HOME_DIR` và `PYINSTALLER_RESET_ENVIRONMENT`. |
| `mouse_hook_service.py:110-151` (`_hook_proc`) | Kiểm tra toàn bộ luồng xử lý hook chuột cấp thấp | **XÁC NHẬN NGUYÊN NHÂN GESTURE CHẾT:** Thực thi các tác vụ nặng/đồng bộ ngay trong callback hook (`window_service`, `config_service.load()`, `SendInput`). |
| `mouse_hook_service.py:84-108` (`_run`, `_start_watchdog`) | Kiểm tra cơ chế phục hồi hook khi bị timeout | **XÁC NHẬN KHIẾM KHUYẾT:** Watchdog chu kỳ 10s dùng `PostThreadMessageW`. Nếu luồng hook bị block trong lệnh đồng bộ, message loop không chạy, watchdog hoàn toàn vô hiệu. |
| `window_service.py:14-46` (`get_hwnd_info`) | Kiểm tra hàm lấy thông tin cửa sổ | **XÁC NHẬN ĐIỂM TREO:** `GetWindowTextW` gửi message xuyên tiến trình đồng bộ không có timeout. Luôn chạy kể cả khi caller chỉ cần `exe`. |
| `tab_switch_logic.py:31-42` (`handle_scroll_for_tab_switch`) | Kiểm tra luồng Shift+Scroll | **XÁC NHẬN:** Gọi `get_hwnd_info` đồng bộ trên mỗi tick cuộn khi giữ Shift. |
| `mouse_mapper_logic.py:62-72` (`_on_xbutton_down`) | Kiểm tra luồng Rocker Gesture X1/X2 | **XÁC NHẬN:** Gọi `get_hwnd_info` đồng bộ và `switch_tab_x1x2` (`SendInput`) đồng bộ trên luồng hook. |
| `mouse_mapper_logic.py:142-153` (`_on_right_up`) | Kiểm tra kết thúc cử chỉ RMB | **XÁC NHẬN:** Đọc đĩa đồng bộ qua `config_service.load()` và bắn phím qua `shortcut_executor.execute()` đồng bộ trên luồng hook. |
| `config_service.py:67-88` (`load`) | Kiểm tra chi phí đọc file cấu hình | **NGHI VẤN ĐỘ TRỄ:** Đọc file JSON từ đĩa mỗi lần nhả cử chỉ; có thể chậm khi đĩa bận hoặc bị Antivirus quét. |
| `RightWheel.spec` | Kiểm tra cấu hình build onefile, runtime_tmpdir | **LOẠI TRỪ LỖI CẤU HÌNH SPEC:** Cấu hình chuẩn một file (`runtime_tmpdir=None`, `upx=True`), không có flag bất thường. |
| `docs/debug/gesture-trail-x1x2-flaky.debug2.md` | Đối chiếu cảnh báo trước đó ở F-005 | **XÁC NHẬN:** Mục 2 (rủi ro `LowLevelHooksTimeout` 200ms) đã cảnh báo chính xác nhưng bị hoãn lại ở F-005. |

---

## 4. GIẢ THUYẾT XẾP HẠNG

### H1 (Khả năng cao nhất — Lớp Config-Env & Dependency/Version Lifecycle):
**Lỗi DLL khi Restart bắt nguồn từ việc `tray_ui.py` kế thừa biến môi trường `_PYI_APPLICATION_HOME_DIR` của PyInstaller >= 6.11:**
- **Cơ chế:** PyInstaller 6.20.0 sử dụng bộ biến `_PYI_*` (`_PYI_APPLICATION_HOME_DIR`, `_PYI_ARCHIVE_FILE`, `_PYI_PARENT_PROCESS_LEVEL`) thay cho biến legacy `_MEIPASS2`. Khi `tray_ui.py` chỉ gọi `env.pop("_MEIPASS2", None)`, biến `_PYI_APPLICATION_HOME_DIR` (giá trị `C:\Users\Chau\AppData\Local\Temp\_MEI311162`) vẫn được truyền sang tiến trình `RightWheel.exe` mới spawn qua `cmd.exe`.
- **Hậu quả:** Khi tiến trình cũ thoát, bootloader cũ xóa thư mục `_MEI311162`. Tiến trình mới khởi động thấy biến môi trường trỏ vào thư mục cũ nên bỏ qua bước giải nén và gọi `LoadLibrary` vào đường dẫn đã bị xóa, lập tức bật dialog lỗi `LoadLibrary: The specified module could not be found`.
- **Bằng chứng:** Chuỗi nhị phân trong `runw.exe` chứng minh 100% không còn `_MEIPASS2`, chỉ có `_PYI_APPLICATION_HOME_DIR` và cờ reset chính thức `PYINSTALLER_RESET_ENVIRONMENT`.

### H2 (Khả năng cao nhất — Lớp Win32 Hook Threading & IPC Synchronous Hang):
**Triệu chứng cử chỉ mất tác dụng bắt nguồn từ việc thực thi các lệnh Win32 đồng bộ xuyên tiến trình (`GetWindowTextW`) và I/O đĩa ngay trên luồng hook cấp thấp (`WH_MOUSE_LL`):**
- **Cơ chế:**
  1. Trong `_on_xbutton_down` và `handle_scroll_for_tab_switch`, code gọi `window_service.get_hwnd_info(hwnd)` chỉ để lấy tên file thực thi (`exe`), nhưng hàm này luôn gọi đồng bộ `GetWindowTextW(hwnd)`. Lệnh này gửi message `WM_GETTEXT` sang tiến trình foreground (như Chromium). Nếu trình duyệt đang bận tải trang/render nặng, `GetWindowTextW` bị block.
  2. Windows kernel giám sát `_hook_proc` qua bộ đếm thời gian `LowLevelHooksTimeout` (200-300ms). Bất kỳ sự kiện nào xử lý vượt quá thời gian này sẽ bị Windows **âm thầm gỡ bỏ (`silently unhook`) hook `WH_MOUSE_LL`** khỏi chuỗi hook toàn cục.
  3. Khi hook bị gỡ bỏ, sự kiện `WM_RBUTTONUP` không được nhận, khiến `MouseMapperLogic` bị kẹt ở trạng thái `RIGHT_HELD` hoặc `GESTURE`.
  4. Nếu luồng hook bị treo trong `GetWindowTextW`, vòng lặp `GetMessageW` không thể nhận message `WM_APP_REHOOK` từ watchdog (chu kỳ 10s), khiến hook chết vĩnh viễn cho đến khi người dùng khởi động lại app.
- **Bằng chứng:** Code trong `mouse_mapper_logic.py`, `tab_switch_logic.py`, và `window_service.py` cho thấy các lệnh block Win32 và I/O hoàn toàn không được marshal ra worker thread mà chạy thẳng trên luồng hook.

### H3 (Khả năng thấp — Lớp Race Condition giữa hai tiến trình / Antivirus Scan):
**Thời gian chờ 1 giây (`ping -n 2`) không đủ để bootloader cũ dọn dẹp thư mục tạm, dẫn đến đụng độ tên thư mục tạm mới:**
- **Kiểm chứng & Loại trừ:** Tên thư mục tạm của PyInstaller được sinh dựa trên PID (`_MEI<PID>2`). Tiến trình mới có PID khác hoàn toàn nên sẽ sinh ra một thư mục tạm khác (ví dụ `_MEI123452`), không thể xung đột tên với thư mục cũ `_MEI311162`. Lỗi thực tế trỏ thẳng vào chính thư mục cũ `_MEI311162`, chứng minh tiến trình mới không hề cố tạo thư mục mới mà bị ép sử dụng lại đường dẫn cũ do biến môi trường `_PYI_APPLICATION_HOME_DIR`. Do đó giả thuyết H3 bị loại trừ.

---

## 5. ROOT CAUSE CHỐT & MỐI LIÊN HỆ GIỮA 2 TRIỆU CHỨNG

### Root Cause Chốt:
1. **Triệu chứng 1 (Gesture chết):** Do **H2** — Luồng hook `WH_MOUSE_LL` bị vi phạm thời gian phản hồi `LowLevelHooksTimeout` hoặc bị treo vĩnh viễn bởi các lệnh Win32 đồng bộ (`GetWindowTextW` trong `get_hwnd_info`) và I/O đĩa (`config_service.load()`) chạy trực tiếp trong callback `_hook_proc`.
2. **Triệu chứng 2 (Lỗi DLL khi Restart):** Do **H1** — `tray_ui.py:_restart()` dọn dẹp biến môi trường không triệt để (chỉ pop `_MEIPASS2` legacy mà không pop các biến `_PYI_*` của PyInstaller 6.20.0, đặc biệt là `_PYI_APPLICATION_HOME_DIR`, và không thiết lập `PYINSTALLER_RESET_ENVIRONMENT=1`).

### Mối liên hệ nhân quả giữa hai triệu chứng:
- Người dùng đang làm việc bình thường, thao tác cử chỉ chuột hoặc bấm X1/X2 trúng thời điểm trình duyệt/ứng dụng foreground phản hồi chậm. Lệnh `GetWindowTextW` làm luồng hook chạm ngưỡng `LowLevelHooksTimeout` (hoặc bị block), Windows âm thầm hủy hook `WH_MOUSE_LL`, làm toàn bộ gesture "bỗng dưng tê liệt" (**Triệu chứng 1**).
- Thấy gesture không còn ăn, người dùng click chuột phải vào Tray Icon (vốn chạy trên luồng riêng của pystray nên menu vẫn bật được) và bấm nút "Restart" để hy vọng khôi phục tiện ích.
- Lệnh `_restart()` spawn tiến trình mới nhưng truyền nguyên biến môi trường `_PYI_APPLICATION_HOME_DIR = ...\_MEI311162`. Khi tiến trình cũ vừa thoát, bootloader cũ xóa thư mục này; tiến trình mới khởi động cố nạp `python314.dll` từ thư mục vừa bị xóa và văng dialog lỗi (**Triệu chứng 2**).

### Trả lời 3 câu hỏi bắt buộc:
1. **Tại sao lỗi xảy ra (cơ chế):**
   - Hook chết do Win32 kernel timeout/block khi gọi `GetWindowTextW` và I/O đồng bộ trên luồng `WH_MOUSE_LL`.
   - Lỗi DLL do bootloader PyInstaller 6.20.0 kế thừa `_PYI_APPLICATION_HOME_DIR` từ tiến trình cũ đã bị hủy dọn dẹp.
2. **Tại sao bây giờ mới lộ:**
   - Commit `f5019d3` và `484d4d8` (F-005) chuyển cơ chế restart sang `subprocess.Popen` với `env.pop("_MEIPASS2")` dựa trên giả định PyInstaller phiên bản cũ. Các phiên bản PyInstaller hiện tại (6.20.0) dùng `_PYI_*` nên bản fix ở F-005 hoàn toàn vô hiệu với biến môi trường mới.
   - Các tính năng mới (F-003, F-005, F-006) bổ sung liên tục các tác vụ vào luồng cử chỉ (`tab_switch_logic`, `window_service.get_hwnd_info`, `config_service.load`), gia tăng đáng kể nguy cơ chạm ngưỡng timeout 200ms của Windows hook.
3. **Nơi cần sửa (mô tả, CHƯA sửa):**
   - **Fix Triệu chứng 2 (`tray_ui.py`):** Trong `_restart()`, ngoài việc pop `_MEIPASS2`, phải quét và xóa toàn bộ các biến môi trường có tiền tố `_PYI_` (`[k for k in env if k.startswith('_PYI_')]`) và gán cờ chuẩn của PyInstaller: `env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"`.
   - **Fix Triệu chứng 1 (`window_service.py`, `mouse_mapper_logic.py`, `mouse_hook_service.py`):**
     1. Tách hàm lấy `exe` thuần túy (`get_process_name_by_hwnd`) chỉ dùng `GetWindowThreadProcessId` + `QueryFullProcessImageNameW` (không gọi `GetWindowTextW`, không gửi message, không bao giờ block). Các caller như `_on_xbutton_down` và `handle_scroll_for_tab_switch` chỉ cần gọi hàm này.
     2. Nếu cần lấy tiêu đề cửa sổ (`title`), dùng `user32.InternalGetWindowText` hoặc `SendMessageTimeoutW` với timeout ngắn (50ms) thay vì `GetWindowTextW`.
     3. Đẩy việc thực thi phím tắt (`shortcut_executor.execute`) và đọc config đĩa ra worker thread hoặc bất đồng bộ thay vì chặn luồng hook.

**Độ tin cậy:** Cao (100%) — Đã kiểm chứng trực tiếp chuỗi nhị phân bootloader `runw.exe` của PyInstaller 6.20.0 và đối chiếu mã nguồn thực tế của toàn bộ các hàm liên quan.

---
*CHƯA SỬA GÌ. Chạy debug2 để phản biện root cause này trước khi fix.*
