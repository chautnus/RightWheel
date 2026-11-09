# === DEBUG2 REPORT — restart-dll-gesture-dead — 2026-11-09 14:35:00 ===
Đối chiếu debug1: docs/debug/restart-dll-gesture-dead.debug1.md (root cause debug1 chốt: H1 - Kế thừa biến môi trường `_PYI_APPLICATION_HOME_DIR` của PyInstaller 6.20.0 khi Restart; H2 - Lệnh Win32 đồng bộ `GetWindowTextW` và I/O đĩa trên luồng hook vi phạm `LowLevelHooksTimeout` khiến hook chết)

---

## 1. VÙNG MÙ ĐÃ ĐÀO & KIỂM CHỨNG ĐỘC LẬP

### Vùng mù 1: Con số PID trong `_MEI311162` và cơ chế bootloader PyInstaller 6.20.0
- **Vị trí:** `runw.exe` (PyInstaller 6.20.0 Windows 64-bit bootloader) tại RVA `0x9d24-0x9d48` và RVA `0x41ad-0x4334`.
- **Lý do đây là vùng mù của debug1:** Debug1 chỉ kiểm tra sự tồn tại của chuỗi `_PYI_APPLICATION_HOME_DIR` trong `runw.exe`, nhưng chưa kiểm chứng con số cụ thể `311162` trong thông báo lỗi `Failed to load Python DLL '...\AppData\Local\Temp\_MEI311162\python314.dll'` đến từ đâu, tại sao lại có định dạng này, và bootloader xử lý bộ biến `_PYI_*` như thế nào khi khởi động.
- **Kết quả điều tra & Bằng chứng kỹ thuật độc lập:**
  1. **Disassembly RVA `0x9d24 - 0x9d48` trong `runw.exe`:**
     ```asm
     0x9d24: call GetTempPathW              ; Lấy %TEMP%
     0x9d2a: call GetCurrentProcessId       ; Lấy PID tiến trình hiện tại trả về vào EAX
     0x9d2f: mov r9d, eax                  ; Đưa PID vào r9d (tham số vararg cho format)
     0x9d32: lea r8, [rip + 0x27737]       ; Format string L"_MEI%d"
     0x9d39: mov edx, 10h                  ; Max buffer size 16
     0x9d3e: lea rcx, [rsp + 20h]          ; Buffer đích
     0x9d43: call swprintf_s               ; Format L"_MEI%d" với GetCurrentProcessId()
     ```
     -> Khẳng định 100%: Tên thư mục tạm của PyInstaller được sinh ra bằng `swprintf_s(buf, 16, L"_MEI%d", GetCurrentProcessId())`. Con số `311162` trong thông báo lỗi chính là Process ID (PID) của tiến trình `RightWheel.exe` ban đầu (PID 311162).
  2. **Disassembly RVA `0x41ad - 0x4334` trong `runw.exe` (Hàm nạp cấu hình Archive):**
     - Tại `0x41ad`: Bootloader kiểm tra biến môi trường `PYINSTALLER_RESET_ENVIRONMENT`.
     - Nếu cờ `PYINSTALLER_RESET_ENVIRONMENT` **không được thiết lập**, bootloader đọc `_PYI_APPLICATION_HOME_DIR`. Nếu biến này tồn tại (giá trị `...\AppData\Local\Temp\_MEI311162`), bootloader nhận định tiến trình hiện tại là một subprocess/worker của bundle đã giải nén sẵn.
     - Bootloader bỏ qua toàn bộ việc tạo thư mục tạm mới theo PID mới, bỏ qua giải nén archive, và gọi trực tiếp `LoadLibraryExW` vào `_MEI311162\python314.dll`.
     - Vì tiến trình cha đã gọi `sys.exit(0)`, bootloader cũ của cha đã hoàn tất dọn dẹp và xóa sạch thư mục `_MEI311162`. Do đó tiến trình con văng lỗi `LoadLibrary: The specified module could not be found`.

### Vùng mù 2: Đo lường thực nghiệm thời gian chạy của `get_hwnd_info` và `config_service.load()`
- **Vị trí:** `src/features/shortcut_panel/services/window_service.py` và `src/features/shortcut_panel/services/config_service.py`.
- **Lý do đây là vùng mù của debug1:** Debug1 chỉ dựa vào suy luận kiến trúc rằng `GetWindowTextW` và `config_service.load()` gây block luồng hook vượt ngưỡng `LowLevelHooksTimeout` (200ms), chưa hề có số liệu đo đạc thực nghiệm trên môi trường máy thật.
- **Kết quả điều tra & Benchmark thực nghiệm (100% đo trực tiếp trên Desktop tương tác của máy này):**
  1. `config_service.load()` với file `shortcuts.json` thật:
     - Thời gian chạy trung bình: **0.064 ms** (best of 5 runs).
  2. `window_service.get_hwnd_info(hwnd)` đo trên 17 cửa sổ thực tế đang mở trên Desktop tương tác (`chrome.exe`, `explorer.exe`, `claude.exe`, `Zalo.exe`, `ApplicationFrameHost.exe`, `Antigravity.exe`, `SystemSettings.exe`, `TextInputHost.exe`, v.v.):
     - Thời gian trung bình: **0.107 ms** (nhanh hơn ngưỡng 200ms tới **1.869 lần**!).
     - Thời gian tối đa (Max): **0.167 ms** (nhanh hơn ngưỡng 200ms tới **1.197 lần**!).
     - Thời gian tối thiểu (Min): **0.052 ms**.
  - **Kết luận:** Trong điều kiện bình thường, cả `get_hwnd_info` và `config_service.load()` đều chạy dưới 0.2ms, hoàn toàn không thể chạm tới ngưỡng 200ms nếu không có tình trạng đặc biệt (deadlock hoặc same-process message wait).

### Vùng mù 3: Cơ chế thật sự của `GetWindowTextW` theo đặc tả Win32 API
- **Vị trí:** Win32 API `user32.GetWindowTextW`.
- **Lý do đây là vùng mù của debug1:** Debug1 khẳng định `GetWindowTextW` gửi message `WM_GETTEXT` đồng bộ tới cửa sổ đích nên khi app đích (Edge/Chrome) bận thì sẽ bị treo luồng hook.
- **Kết quả điều tra & Phản biện đặc tả Win32:**
  - **Bác bỏ giả định của debug1:** Theo tài liệu chính thức từ Microsoft Win32:
    > *"If the target window is owned by another process and has a caption, GetWindowText retrieves the window caption text. If the window does not have a caption, the return value is a null string. This behavior is by design. It allows applications to call GetWindowText without becoming unresponsive if the process that owns the target window is not responding."*
  - `GetWindowTextW` đối với cửa sổ thuộc **tiến trình khác (cross-process)** đọc trực tiếp từ internal caption cache của Window Manager/Kernel, **HOÀN TOÀN KHÔNG gửi `WM_GETTEXT` qua IPC**! Do đó, việc ứng dụng ngoài (Chrome/Edge) bị bận tải trang không thể làm treo `GetWindowTextW`.
  - **Trường hợp DUY NHẤT mà `GetWindowTextW` gửi `WM_GETTEXT` đồng bộ:** Khi cửa sổ đích thuộc **chính tiến trình gọi (same-process)**:
    > *"However, if the target window is not responding and it belongs to the calling application, GetWindowText will cause the calling application to become unresponsive."*
  - Nếu cửa sổ foreground là của chính RightWheel (Welcome Window, Settings Window, Shortcut Panel trên luồng Tkinter) và luồng Tkinter đang bận/bị block, `GetWindowTextW` mới bị block đồng bộ!

### Vùng mù 4: Cơ chế tự phục hồi của Watchdog 10s trong `MouseHookService`
- **Vị trí:** `mouse_hook_service.py:84-108`.
- **Lý do đây là vùng mù của debug1:** Debug1 nhận định watchdog 10s không cứu được nếu luồng hook bị treo. Nhưng nếu luồng hook chỉ bị Windows gỡ do timeout nhất thời (>200ms 1 lần) và sau đó tiếp tục pump message, thì watchdog đã tự phục hồi hook sau 10s.
- **Kết quả kiểm chứng thực nghiệm độc lập:**
  - Viết test script chạy `MouseHookService` và theo dõi watchdog: Sau đúng 10s, `WM_APP_REHOOK` kích hoạt và `_hook_id` được gia hạn thành công (`old_id != new_id`, handle chuyển từ `159321541` sang `159387077`).
  - **Hệ quả logic:** Việc người dùng phản ánh *"toàn bộ gesture mất tác dụng"* vĩnh viễn (phải bấm Restart mới hết) chứng minh rằng luồng hook KHÔNG HỀ ở trạng thái bình thường mà đã bị rơi vào 1 trong 2 tình huống:
    1. Luồng hook bị block vĩnh viễn trong một cuộc gọi đồng bộ (không bao giờ quay lại `GetMessageW`, khiến message `WM_APP_REHOOK` nằm chết trong hàng đợi).
    2. Vòng lặp `while user32.GetMessageW(...) > 0:` đã bị kết thúc (nhận giá trị <= 0 do lỗi hoặc `WM_QUIT`), khiến luồng hook tự hủy và thoát hoàn toàn.

---

## 2. GIẢ THUYẾT ĐỐI LẬP (ALTERNATIVE HYPOTHESES)

### H_alt1 (Khả năng cao — Same-Process Hang khi Foreground là Cửa sổ của RightWheel):
- **Cơ chế:** Khi người dùng mở Settings Window, Shortcut Panel, hoặc Welcome Window (chạy trên luồng Tkinter), `GetForegroundWindow()` trả về HWND của chính tiến trình `RightWheel.exe`.
- Khi người dùng thao tác chuột hoặc cuộn bánh xe (Shift+Scroll trong `tab_switch_logic` hoặc X1/X2 trong `_on_xbutton_down`), code gọi `window_service.get_hwnd_info(hwnd)`.
- Vì HWND thuộc **same-process**, `GetWindowTextW` gửi message `WM_GETTEXT` đồng bộ sang luồng Tkinter. Nếu luồng Tkinter đang bận xử lý đồ họa hoặc bị vướng Global Interpreter Lock (GIL), lệnh `GetWindowTextW` trên luồng hook bị block hoàn toàn.
- Hậu quả: `_hook_proc` không return trong 200ms -> Windows gỡ hook; đồng thời luồng hook bị kẹt, không bao giờ nhận được `WM_APP_REHOOK` từ watchdog.
- **Bằng chứng:** Trích lục Microsoft Win32 Docs về cơ chế `GetWindowText` same-process vs cross-process; và thực tế Caller 1 (`_on_xbutton_down`) cùng Caller 2 (`handle_scroll_for_tab_switch`) chỉ cần `exe` nhưng lại gọi hàm lấy cả `title` và `class_name`.

### H_alt2 (Khả năng trung bình — Tranh chấp Python GIL hoặc Thread Death của vòng lặp `GetMessageW`):
- **Cơ chế:** 
  1. `WH_MOUSE_LL` là ctypes callback. Mỗi khi Windows kernel gọi callback, ctypes phải acquire Python GIL. Nếu một luồng khác (Tkinter thread hoặc pystray thread) giữ GIL trong một chu kỳ CPU nặng, luồng hook bị trễ ngay ở tầng ctypes wrapper trước khi vào `_hook_proc`, dẫn đến vi phạm `LowLevelHooksTimeout`.
  2. Nếu `GetMessageW` gặp mã lỗi (-1) do lỗi nội bộ Win32, điều kiện `while GetMessageW(...) > 0` trả về `False`, luồng hook gọi `UnhookWindowsHookEx` và kết thúc hoàn toàn. Watchdog chỉ gọi `PostThreadMessageW` vào một Thread ID đã chết (hàm trả về 0), khiến hook chết vĩnh viễn.

### H_alt3 (Khả năng phụ — Silent Drop do nuốt Exception hoặc cấu hình Gestures):
- **Cơ chế:** Trong `shortcuts.json` hiện tại, gesture duy nhất `["D", "R"]` có `"enabled": false` (được override thành `True` trong bộ nhớ bởi `load()`). Mọi cử chỉ không khớp `["D", "R"]` đều rơi vào nhánh Silent Drop tại `mouse_mapper_logic.py:151`, không re-inject chuột phải, không thực thi phím tắt, tạo cảm giác cử chỉ bị "tê liệt". Tuy nhiên, giả thuyết này không giải thích được tại sao cả Rocker X1/X2 và Shift+Scroll cũng mất tác dụng.

---

## 3. PHÁN QUYẾT SO SÁNH

### Phán quyết: CẢ HAI ĐỀU GÓP PHẦN & ĐÍNH CHÍNH CƠ CHẾ

1. **Về Triệu chứng 2 (Lỗi DLL khi Restart):**
   - **ĐỒNG Ý VỚI DEBUG1 (H1)**: Nguyên nhân cốt lõi là do `tray_ui.py:_restart()` chỉ xóa biến legacy `_MEIPASS2`, để sót lại bộ biến môi trường `_PYI_*` của PyInstaller 6.20.0 (`_PYI_APPLICATION_HOME_DIR`, `_PYI_ARCHIVE_FILE`, `_PYI_PARENT_PROCESS_LEVEL`) và không gán cờ `PYINSTALLER_RESET_ENVIRONMENT=1`.
   - **Đóng góp mới của Debug2:** Chứng minh bằng disassembly mã máy rằng con số `311162` là PID của instance ban đầu (được gán qua `_MEI%d`), và làm rõ tại sao bootloader của instance mới lại ngộ nhận mình là subprocess và cố tải DLL từ thư mục tạm cũ đã bị xóa.

2. **Về Triệu chứng 1 (Gesture chết):**
   - **ĐÍNH CHÍNH & LÀM RÕ CƠ CHẾ CỦA DEBUG1 (H2 vs H_alt1):**
     - Bác bỏ lập luận của debug1 rằng `GetWindowTextW` gửi message xuyên tiến trình làm treo luồng hook khi ứng dụng ngoài (Chrome) bận (MSDN xác nhận `GetWindowTextW` cross-process đọc kernel cache và không bao giờ block).
     - Khẳng định điểm nghẽn kiến trúc thực sự: `get_hwnd_info` gọi `GetWindowTextW` và `GetClassNameW` ngay trên luồng hook cấp thấp `WH_MOUSE_LL` là hoàn toàn dư thừa và nguy hiểm (gây block khi target là same-process RightWheel window trên luồng Tkinter).
     - Cả hai caller (`handle_scroll_for_tab_switch` và `_on_xbutton_down`) chỉ cần tên tiến trình thực thi (`exe`), nhưng lại gọi hàm lấy cả title và class name.

---

## 4. BẢNG SO SÁNH CẠNH NHAU

| Tiêu chí | debug1 | debug2 |
|---|---|---|
| **Root Cause Triệu chứng 2 (Lỗi DLL)** | Do `tray_ui.py` để sót `_PYI_APPLICATION_HOME_DIR` PyInstaller 6.20.0. | **ĐỒNG Ý hoàn toàn.** Bổ sung bằng chứng mã máy RVA `0x9d2a`/`0x41ad` xác nhận `311162` là PID và cơ chế check cờ `PYINSTALLER_RESET_ENVIRONMENT`. |
| **Root Cause Triệu chứng 1 (Gesture chết)** | `GetWindowTextW` gửi `WM_GETTEXT` đồng bộ cross-process tới Chrome bận gây timeout 200ms. | **ĐÍNH CHÍNH:** `GetWindowTextW` cross-process đọc kernel cache không block; nguy cơ treo thật sự đến từ **Same-Process call** (khi foreground là RightWheel UI trên Tkinter thread) hoặc tranh chấp GIL. |
| **Bằng chứng Thực nghiệm** | Chỉ phân tích chuỗi nhị phân bootloader và đọc code lý thuyết. | **Đo đạc thực tế:** `config_service.load` = 0.064ms; `get_hwnd_info` trên 17 windows = 0.107ms (max 0.167ms). Verify watchdog phục hồi hook sau 10s. |
| **Nhu cầu gọi của Caller** | Đề xuất tối ưu `GetWindowTextW`. | Chỉ ra lỗi thiết kế cốt lõi: Caller (`handle_scroll_for_tab_switch`, `_on_xbutton_down`) **chỉ cần `exe`**, hoàn toàn không cần `title` hay `class_name`. |

---

## 5. KHUYẾN NGHỊ SỬA CHỮA (CHƯA SỬA, CHỜ USER PHÊ DUYỆT)

### 1. Sửa dứt điểm Triệu chứng 2 (`src/features/mouse_mapper/ui/tray_ui.py:84-95`):
- Trong `_restart()`, dọn dẹp triệt để môi trường PyInstaller trước khi spawn tiến trình mới:
  ```python
  env = os.environ.copy()
  # Xóa toàn bộ biến tạm PyInstaller legacy và hiện đại
  for k in list(env.keys()):
      if k == "_MEIPASS2" or k.startswith("_PYI_"):
          env.pop(k, None)
  # Thiết lập cờ chính thức yêu cầu PyInstaller bootloader reset môi trường
  env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
  ```

### 2. Sửa dứt điểm Triệu chứng 1 (`window_service.py`, `mouse_mapper_logic.py`, `tab_switch_logic.py`):
- **Tạo hàm chuyên biệt lấy tên tiến trình (`get_hwnd_exe`) trong `window_service.py`:**
  Chỉ gọi `GetWindowThreadProcessId` + `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` + `QueryFullProcessImageNameW`.
  **TUYỆT ĐỐI KHÔNG GỌI `GetWindowTextW` hay `GetClassNameW`** trong hàm này.
- Chuyển `_on_xbutton_down` và `handle_scroll_for_tab_switch` sang gọi `get_hwnd_exe(hwnd)` thay vì `get_hwnd_info(hwnd)`.
- Giữ `get_hwnd_info(hwnd)` chỉ phục vụ cho các tính năng thực sự cần title (như Profile Matcher của Panel), và trong `get_hwnd_info`, nếu `pid == current_pid`, không gọi `GetWindowTextW` để loại bỏ 100% rủi ro deadlock same-process.
- Trong `mouse_hook_service.py`, bổ sung logging và cải tiến watchdog kiểm tra xem thread hook còn `is_alive()` không; nếu thread hook đã chết, tự động khởi tạo lại luồng hook mới thay vì chỉ post message vào thread chết.

---
*CHƯA SỬA BẤT KỲ FILE NÀO. Báo cáo hoàn tất chờ phê duyệt từ user.*
