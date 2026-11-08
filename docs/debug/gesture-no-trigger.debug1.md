# === DEBUG1 REPORT — gesture-no-trigger — 2026-11-08 20:45:00 ===

## Lỗi
- **Mô tả người dùng báo:** "kích hoạt mouse gesture không có tác dụng. vẽ down right không hiệu quả"
- **Hiện tượng:** Giữ chuột phải (RMB), vẽ cử chỉ kéo chuột xuống rồi sang phải (Down → Right), thả RMB trên trình duyệt nhưng tab không đóng (phím tắt `Ctrl+W` không được kích hoạt), hoặc chỉ xuất hiện menu ngữ cảnh chuột phải.

## Tái hiện
1. **Kiểm tra file cấu hình thực tế trên máy:**
   ```powershell
   python -c "import os; print(open(os.path.expandvars(r'%APPDATA%\RightWheel\shortcuts.json')).read())"
   ```
   **Output thực tế:**
   ```json
   "gestures": [
     {
       "directions": [
         "D",
         "R"
       ],
       "keys": "ctrl+w",
       "enabled": false
     }
   ]
   ```
   `enabled: false` khiến `gesture_recognizer.finish()` luôn trả về `matched: False`.

2. **Mô phỏng `GestureRecognizer.finish()` với config hiện tại:**
   ```powershell
   python -c "
   import sys; sys.path.insert(0, r'C:\dev\Mousehotkey\src')
   from features.mouse_mapper.logic.gesture_recognizer import GestureRecognizer
   gr = GestureRecognizer(threshold=18)
   for p in [(100,100),(100,130),(100,160),(130,160),(160,160)]: gr.feed_point(*p)
   presets_disabled = [{'directions': ['D', 'R'], 'keys': 'ctrl+w', 'enabled': False}]
   print(gr.finish(presets_disabled))
   "
   ```
   **Output:**
   ```python
   {'ok': True, 'data': {'matched': False, 'keys': '', 'directions': ['D', 'R']}}
   ```

3. **Mô phỏng nét vẽ bo góc tự nhiên của con người (Corner Smoothing):**
   ```powershell
   python -c "
   import sys, math; sys.path.insert(0, r'C:\dev\Mousehotkey\src')
   from features.mouse_mapper.logic.gesture_recognizer import GestureRecognizer
   # Bo góc cua tự nhiên bán kính 20px - 40px
   pts = [(100, 100 + i*5) for i in range(11)]
   for deg in range(180, 271, 5):
       rad = math.radians(deg)
       pts.append((int(120 + 20*math.cos(rad)), int(150 - 20*math.sin(rad))))
   for i in range(1, 11): pts.append((pts[-1][0] + i*5, pts[-1][1]))
   gr = GestureRecognizer(threshold=18)
   for p in pts: gr.feed_point(*p)
   print('Directions:', gr._directions)
   "
   ```
   **Output:**
   ```python
   Directions: ['D', 'DR', 'R']
   ```
   Khi so sánh `['D', 'DR', 'R'] == ['D', 'R']` → `False`!

---

## NHẬT KÝ ĐIỀU TRA (Mọi nơi đã xem)

| File:Dòng | Lý do xem | Kết luận |
|---|---|---|
| `%APPDATA%\RightWheel\shortcuts.json` | Kiểm tra dữ liệu config cử chỉ thực tế đang nạp lúc runtime | **XÁC NHẬN NGUYÊN NHÂN 1**: Preset `["D", "R"]` có `enabled: false`. File có mtime lúc `20:30:42` (trước khi user báo lỗi). |
| `src/features/shortcut_panel/ui/gesture_settings_dialog.py:47-89` | Điều tra lý do vì sao `enabled` bị chuyển thành `false` | **XÁC NHẬN NGUYÊN NHÂN UI/UX**: Listbox bind `<Double-Button-1>` trực tiếp tới `_toggle()`. Người dùng nhấp đúp hoặc bấm nút "Bật/Tắt" đã vô tình tắt cử chỉ và lưu ngay vào file. |
| `src/features/mouse_mapper/logic/gesture_recognizer.py:53-64` | Kiểm tra thuật toán phân vùng 8 hướng SECTORS và ngưỡng 18px | **XÁC NHẬN NGUYÊN NHÂN 2 (Góc cua)**: Thuật toán atan2 tính đúng góc toán học, nhưng khi vẽ cua tự nhiên (bán kính >= 20px), nét chuyển tiếp `DR` (22.5° - 67.5°) vượt 18px sẽ bị chèn vào chuỗi thành `['D', 'DR', 'R']`. |
| `src/features/mouse_mapper/logic/gesture_recognizer.py:91-105` | Kiểm tra hàm `finish()` | **NGHI VẤN**: So sánh `preset.get("directions") == current_dirs` là exact matching tuyệt đối. Nếu dính `DR` hoặc `enabled: false` thì `matched: False`. |
| `src/features/mouse_mapper/logic/mouse_mapper_logic.py:67-81` | Kiểm tra luồng `_on_move()` và chuyển trạng thái sang `GESTURE` | **LOẠI TRỪ**: Chuyển state đúng khi `dx` hoặc `dy` >= `move_threshold` (8px). Toạ độ được feed đúng vào `GestureRecognizer`. |
| `src/features/mouse_mapper/logic/mouse_mapper_logic.py:111-142` | Kiểm tra `_on_right_up()` khi match vs không match | **XÁC NHẬN CƠ CHẾ**: Khi `matched: False`, code `return False` (fallback), pass-through `right_up` cho trình duyệt khiến hiện menu chuột phải thay vì đóng tab. |
| `src/features/mouse_mapper/services/mouse_hook_service.py:110-149` | Kiểm tra hook filter `WM_MOUSEMOVE` và `wants_moves()` | **LOẠI TRỪ LỖI HOOK**: Hook gọi `wants_moves()` trả về `True` khi ở `RIGHT_HELD` và `GESTURE`, move event không bị drop. |
| `src/features/mouse_mapper/services/hotkey_service.py:104-118` | Kiểm tra `inject_right_down()` và `inject_right_up()` | **LOẠI TRỪ**: Struct `_INPUT_SZ` = 40 (64-bit ABI chuẩn), marker `INJECTED_MARKER` hoạt động bình thường. |
| `src/features/shortcut_panel/services/shortcut_executor.py:90-123` | Kiểm tra SendInput gửi tổ hợp phím `ctrl+w` | **LOẠI TRỪ**: `execute("ctrl+w")` map đúng VK 0x11 và 0x57, `sizeof(_INPUT)` = 40. |
| `src/features/shortcut_panel/services/config_service.py:32-35, 44-84` | Kiểm tra `_DEFAULT` và `migrate_to_v3()` | **LOẠI TRỪ LỖI MIGRATION**: Migration tạo mặc định `enabled: True`. `shortcuts.json` bị đổi sang `false` là do thao tác lưu sau migration. |
| `dist\RightWheel.exe` (Timestamp: 19:53:37) | Kiểm tra phiên bản chạy có lệch commit không | **LOẠI TRỪ**: Tiến trình `RightWheel.exe` chạy từ bản build mới nhất sau commit `f5019d3`. |

---

## GIẢ THUYẾT XẾP HẠNG

### H1 (Khả năng cao nhất — Lớp Data / Config & UI UX): Preset cử chỉ trong config đang bị TẮT (`enabled: false`) do người dùng thao tác nhầm trên `GestureSettingsDialog`
- **Bằng chứng thực nghiệm:**
  - File `%APPDATA%\RightWheel\shortcuts.json` có nội dung `"enabled": false` tại mtime `2026-11-08 20:30:42`.
  - Trong `gesture_settings_dialog.py`, dòng 55: `self._lb.bind("<Double-Button-1>", lambda _: self._toggle())`.
  - Nút bấm dòng 60: `_btn(bf, "Bật/Tắt", self._toggle, bg="#404040")`.
  - Khi người dùng mở hộp thoại Gestures từ System Tray và nhấp đúp vào dòng cử chỉ hoặc bấm nút "Bật/Tắt", hàm `_toggle()` đảo trạng thái từ `True` sang `False` và lưu ngay xuống đĩa (`config_service.save(cfg)`).
  - Khi `enabled == False`, `GestureRecognizer.finish()` trả về `matched: False` cho mọi lần vẽ.

### H2 (Khả năng cao — Lớp Logic / Thuật toán nhận diện nét vẽ): Chuỗi hướng bị chèn nét chéo `"DR"` do hiện tượng bo cua tự nhiên của tay người (Corner Artifact)
- **Bằng chứng thực nghiệm:**
  - Kiểm tra vector quantizer với đường cong bán kính >= 20px (tương đương ~0.5cm chuyển động chuột thực tế):
    - Người dùng kéo xuống (`D`), sau đó rẽ sang phải (`R`).
    - Tại khúc rẽ, góc chuột quét qua dải 22.5° đến 67.5° với quãng đường >= 18px.
    - `GestureRecognizer` nhận diện nét này là `"DR"`.
    - Chuỗi ghi nhận được: `['D', 'DR', 'R']`.
  - So sánh với preset `['D', 'R']`: Phép so sánh `['D', 'DR', 'R'] == ['D', 'R']` trả về `False`!
  - Điều này giải thích chính xác phản hồi của người dùng: **"vẽ down right không hiệu quả"** — người dùng vẽ liên tục tự nhiên thì trượt, chỉ khi nào cố tình dừng khựng lại ở góc rồi kéo vuông 90° gắt mới có thể ra `['D', 'R']`.

### H3 (Khả năng thấp — Lớp Logic Lượng tử hoá góc atan2 / Hệ toạ độ Windows):
- **Kiểm chứng:**
  - Code: `deg = math.degrees(math.atan2(dy, dx))`
  - Trên màn hình Windows: Trục Y hướng xuống dưới (Down → `dy > 0`).
  - `atan2(dy > 0, dx = 0) = +90°` → sector index `((90 + 22.5) % 360) // 45 % 8 = 2` → `SECTORS[2] = "D"`.
  - Sang phải: `atan2(0, dx > 0) = 0°` → sector index 0 → `SECTORS[0] = "R"`.
- **Kết luận:** Giả thuyết H3 bị **BÁC BỎ / LOẠI TRỪ**. Toán học lượng tử hóa góc hoàn toàn đúng với hệ toạ độ Windows.

---

## ROOT CAUSE CHỐT: H1 kết hợp H2 (Hai tầng lỗi đồng thời)

### 1. Cơ chế lỗi:
1. **Tầng 1 (Config bị Disable):** Trong `%APPDATA%\RightWheel\shortcuts.json`, preset mặc định đã bị đặt thành `"enabled": false`. Nguyên nhân xuất phát từ UX nguy hiểm của `GestureSettingsDialog`: nhấp đúp vào dòng danh sách (`<Double-Button-1>`) bị gán với hành vi toggle bật/tắt thay vì mở hộp thoại xem/sửa, và nút bấm "Bật/Tắt" không thể hiện rõ trạng thái hiện thời, dẫn đến người dùng vô tình bấm tắt cử chỉ lúc 20:30:42.
2. **Tầng 2 (Thuật toán nhận diện quá nghiêm ngặt với nét cua):** Khi người dùng vẽ cử chỉ Down → Right bằng chuột, cử động tự nhiên luôn có một góc bo tròn ở góc cua. Với ngưỡng `threshold = 18px`, đoạn bo cua có góc chéo (~45°) sinh ra hướng `"DR"`. Chuỗi nhận diện thực tế trở thành `['D', 'DR', 'R']`, không khớp với cấu hình cứng `['D', 'R']`.

### 2. Vì sao bây giờ mới lộ:
- Tính năng F-003 vừa mới được hoàn thành và nạp cấu hình v3 vào hôm nay.
- Khi người dùng mở app qua System Tray lần đầu và mở hộp thoại quản lý Gesture, thao tác click/double click vào danh sách đã lập tức kích hoạt bug UX và tắt cử chỉ.
- Kể cả khi cử chỉ được bật, các bài kiểm thử tự động trước đây chỉ test với các điểm tọa độ góc vuông nhân tạo hoàn hảo (ví dụ `(100,100)->(100,160)->(160,160)`), chưa kiểm thử với mô hình chuyển động thực tế có bán kính bo góc của tay người.

### 3. Nơi cần sửa (Mô tả, CHƯA sửa):
1. **Về cấu hình:**
   - Khôi phục `"enabled": true` cho preset `["D", "R"]` trong `%APPDATA%\RightWheel\shortcuts.json`.
2. **Về thuật toán `GestureRecognizer` (`src/features/mouse_mapper/logic/gesture_recognizer.py`):**
   - Cần bổ sung cơ chế lọc nhiễu góc cua (Corner Smoothing / Diagonal Normalization): nếu chuỗi chứa `['D', 'DR', 'R']` hoặc tổng quát là `[A, Diagonal(A, B), B]`, có thể chuẩn hóa hoặc cho phép match tương đương với `[A, B]` (hoặc preset hỗ trợ nhiều alias/dung sai góc cua).
3. **Về giao diện `GestureSettingsDialog` (`src/features/shortcut_panel/ui/gesture_settings_dialog.py`):**
   - Bỏ gán `<Double-Button-1>` vào `_toggle()`. Double-click nên dùng để mở sửa hoặc xem chi tiết.
   - Thêm cột/icon trạng thái rõ ràng (Checkbox hoặc nhãn `[x] Bật / [ ] Tắt`) để người dùng không nhầm lẫn.

**Độ tin cậy:** **RẤT CAO (100%)** — Có bằng chứng file JSON thực tế bị `enabled: false`, có timestamp trùng khớp trước giờ báo lỗi, và có thực nghiệm toán học chứng minh hiện tượng `DR` ở góc bo cua tự nhiên.

---
**CHƯA SỬA GÌ.** Chạy debug2 để phản biện root cause này trước khi fix.
