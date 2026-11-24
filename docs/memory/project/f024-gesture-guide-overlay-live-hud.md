---
id: f024-gesture-guide-overlay-live-hud
type: project
title: "F-024: Gesture Guide Overlay (Cửa sổ hướng dẫn cử chỉ trực tiếp khi giữ chuột phải)"
tags: [gesture, guide-overlay, mouse-mapper, hud, win32, live-hint, f024]
keywords: [gesture-guide, overlay, rmb-hold, hud, live-hints, sector-change, click-through, win32]
status: active
created: 2026-11-24
updated: 2026-11-24
summary: "F-024: Gesture Guide Overlay — HUD hướng dẫn cử chỉ trực tiếp 4 hướng góc dưới màn hình khi giữ chuột phải, cập nhật live theo nét vẽ"
---

# F-024: Gesture Guide Overlay — Cửa sổ Hướng dẫn Cử chỉ Trực tiếp

## 1. Why (Lý do & Nguồn gốc)
- **Vấn đề người dùng:** Cử chỉ chuột (Mouse Draw Gestures) là tính năng cốt lõi giúp tăng tốc độ thao tác trên Windows, nhưng rào cản lớn nhất đối với người dùng là *không nhớ vẽ hướng nào sẽ kích hoạt lệnh gì*, hoặc *quên các nhánh rẽ tiếp theo đối với các cử chỉ nhiều nét (multi-stroke gestures)* như `D_R`, `U_R`, `L_D_R`.
- **Giải pháp:** Port tính năng Gesture Guide Overlay từ Touchpad Gesture (F-032), chuyển đổi từ cơ chế 3/4 ngón sang **thao tác giữ chuột phải (RMB Hold)**.
- Khi người dùng giữ chuột phải, một HUD hướng dẫn tinh tế lập tức xuất hiện ở góc dưới bên phải màn hình, hiển thị 4 mũi tên hướng chính (LÊN, XUỐNG, TRÁI, PHẢI) cùng nhãn chức năng tương ứng theo thời gian thực.

---

## 2. What (Kiến trúc & Cơ chế Kỹ thuật)

### 2.1. Cấu trúc Overlay (`src/features/mouse_mapper/ui/gesture_guide_overlay.py`)
- **Kích thước & Vị trí:** Panel cố định `480x480px` đặt tại góc dưới bên phải màn hình làm việc:
  ```python
  px = vx + vw - _PANEL - _MARGIN  # _PANEL = 480, _MARGIN = 24
  py = vy + vh - _PANEL - _MARGIN
  ```
  Sử dụng `GetSystemMetrics(76..79)` để định vị chính xác trên cấu hình đa màn hình (Virtual Desktop / Multi-monitor).
- **Đặc tính Cửa sổ Win32 (Transparent & Click-Through):**
  - Cửa sổ Tkinter `tk.Toplevel(root)` với cờ `-transparentcolor #000001` và `overrideredirect(True)`.
  - Thiết lập thuộc tính Win32 mở rộng `GWL_EXSTYLE`:
    - `WS_EX_NOACTIVATE`: Ngăn tuyệt đối việc cướp focus của ứng dụng người dùng đang làm việc.
    - `WS_EX_TRANSPARENT`: Click-through 100%, mọi sự kiện click/di chuột đi xuyên qua canvas xuống cửa sổ bên dưới.
    - `WS_EX_LAYERED`: Cho phép render đồ họa alpha/transparency mượt mà.
    - `WS_EX_TOOLWINDOW`: Không xuất hiện trên Windows Taskbar hoặc danh sách Alt+Tab.
- **Biểu tượng trung tâm (RMB Glyph):** Vẽ hình khối chuột tối giản với nút chuột phải được tô sáng xanh neon (`#4EA8FF`), thể hiện trực quan trạng thái đang giữ chuột phải.
- **Mũi tên & Nhãn định hướng:**
  - 4 hướng chính: `UP`, `DOWN`, `LEFT`, `RIGHT`.
  - Hướng UP/DOWN: Nhãn nằm ở đầu mút mũi tên theo trục dọc.
  - Hướng LEFT/RIGHT: Nhãn nằm dịch xuống dưới đường kẻ mũi tên để tối ưu không gian hiển thị văn bản không bị che khuất.

### 2.2. Vòng đời Tích hợp vào MouseMapperLogic
- **Bắt đầu giữ chuột (`on_hold_start`):**
  - Kích hoạt ngay tại thời điểm `WM_RBUTTONDOWN` (trước khi chuột di chuyển vượt ngưỡng `move_threshold = 18px`).
  - Cho phép người dùng chỉ cần giữ chuột phải tại chỗ là thấy ngay menu gợi ý 4 hướng mà chưa cần vẽ nét nào.
- **Cập nhật theo nhánh vẽ (`on_sector_change`):**
  - Khi chuột bắt đầu kéo và `GestureRecognizer.feed_point(x, y)` commit một sector hướng chính mới (`CARDINAL_NAMES = {"R": "RIGHT", "L": "LEFT", "U": "UP", "D": "DOWN"}`).
  - `MouseMapperLogic._maybe_report_sector_change()` phát tín hiệu `on_sector_change(path)` chứa danh sách các hướng đã đi qua (ví dụ: `["DOWN"]`).
  - Overlay gọi `update_sectors()`: loại bỏ hướng vừa đi qua, tính toán lại các cử chỉ có prefix khớp với đường dẫn hiện tại để hiển thị gợi ý cho nét rẽ tiếp theo (ví dụ: đang ở `D`, gợi ý tiếp `R` -> "Đóng tab").
- **Kết thúc cử chỉ (`on_gesture_end`):**
  - Khi nhả chuột phải `WM_RBUTTONUP` (kể cả nhấp chuột phải ngắn hoặc hoàn tất vẽ cử chỉ): đóng ngay overlay (`guide_overlay.stop()`), giải phóng canvas và kích hoạt `trim_memory()` sau 300ms.

### 2.3. Thuật toán Tra cứu Nhãn Động (`_guide_labels_for_path` trong `src/main.py`)
1. **Ưu tiên Hồ sơ Ứng dụng Active:** Gọi `resolve_active_profile_full(GetForegroundWindow())`. Nếu ứng dụng có hồ sơ riêng (Chrome, VS Code, v.v.), lấy danh sách `effective_gestures` của profile đó.
2. **Fallback:** Nếu không có profile riêng, lấy danh sách cử chỉ từ `config_service.load()["gestures"]` (Global Profile).
3. **Prefix Matching:** Chuẩn hóa các hướng cử chỉ qua `normalize_directions()`, tìm cử chỉ có độ dài ngắn nhất khớp tiền tố với đường dẫn hiện tại (`candidate_path`).
4. **Hiển thị Nhãn Thân thiện:**
   - Ưu tiên 1: `preset["description"]` (Mô tả chức năng rõ ràng).
   - Ưu tiên 2: `preset["label"]` (Tên nhãn ngắn).
   - Ưu tiên 3: Tra cứu qua từ điển mục đích `IntentService.catalog` để lấy tên tiếng Việt/Anh chuẩn.
   - Ưu tiên 4: Phím tắt gán `preset["keys"]`.
   - Nếu chưa gán: Hiển thị `"Chưa gán"` (`guide_unassigned`).

---

## 3. How to Apply & Lưu ý An toàn
1. **Thread Safety:** Toàn bộ lệnh tương tác với Tkinter (`start`, `update_sectors`, `stop`) đều được bọc qua `root.after(0, ...)`, đảm bảo thread-safe khi gọi từ luồng hook chuột cấp thấp `WH_MOUSE_LL`.
2. **Zero Latency & No Interference:** Nhờ cờ `WS_EX_TRANSPARENT | WS_EX_NOACTIVATE`, overlay hoàn toàn vô hình đối với hệ thống input của Windows, không gây drop FPS và không can thiệp vào tiến trình active.
3. **Short Tap Handling:** Trong trường hợp người dùng chỉ nhấp chuột phải để mở context menu (không vẽ cử chỉ), `on_gesture_end()` được gọi ngay lập tức trước khi `hotkey_service.inject_right_click()` phát lệnh, đảm bảo context menu Windows xuất hiện tự nhiên không bị gián đoạn.
