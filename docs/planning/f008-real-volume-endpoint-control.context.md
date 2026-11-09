## Elicitation — 2026-11-09

Problem:
1. Giao diện trước đây nhồi widget volume mini lên đầu Shortcut Panel gây vướng víu, khó thao tác.
2. Cơ chế volume trước đây chỉ "giả lập" mức 50% tương đối và bắn phím VK_VOLUME_UP/DOWN, không đồng bộ với mức âm lượng thực tế của Windows.

Goal:
1. Đưa mục "🔊 Volume Control" thành một dòng phím tắt rõ ràng, độc lập ngay trang đầu (root list) của Shortcut Panel (hiển thị kèm mức % âm lượng thực tế hiện tại, ví dụ: "🔊 Âm lượng (65%)").
2. Khi người dùng bấm (click LMB hoặc ấn phím số tương ứng): Panel ẩn và mở thanh trượt Volume Slider (Capsule HUD) tại vị trí con trỏ chuột.
3. Quản lý âm lượng theo ĐÚNG THỰC TẾ của máy thông qua Windows Core Audio Endpoint (IAudioEndpointVolume qua ctypes COM thuần — không phụ thuộc thư viện ngoài), đọc và set mức volume chuẩn xác 0%–100%.

Scope IN:
- Bổ sung module `volume_service.py` (sử dụng ctypes gọi IAudioEndpointVolume từ ole32.dll) để đọc mức volume thực tế (get_volume: 0.0 - 1.0) và gán volume thực tế (set_volume, step_volume).
- Loại bỏ widget nhồi nhét trên đầu header của `panel_window.py`.
- Đặt dòng "🔊 Âm lượng (X%)" ngay dòng đầu tiên (hoặc vị trí top-level) của Shortcut Panel. Khi người dùng bấm chuột hoặc gõ phím số, kích hoạt mở Volume Slider HUD.
- Cập nhật `volume_overlay.py`: Khởi tạo slider với đúng mức âm lượng thực tế của Windows tại thời điểm mở; mỗi nấc cuộn chuột tăng/giảm âm lượng thực tế của máy và cập nhật slider + nhãn % tức thì.
- Cập nhật tab General & Volume trong Settings để đọc/hiển thị mức volume thực tế.

Scope OUT:
- Không sửa đổi State Machine chuột trong `mouse_mapper_logic.py` (LOCKED).
- Không cài thêm package bên thứ ba (`pycaw`, `comtypes`) — thực thi thuần qua Windows API `ole32.dll` + `ctypes`.

Stories: US-024, US-025, US-026
Constraints: Mọi file UI/Service ≤ 250 dòng (SYSTEM LOCK). Đảm bảo COM thread-safety (gọi CoInitialize/CoUninitialize an toàn).


---

## PRD — 2026-11-09

Path: docs/prd/f008-real-volume-endpoint-control.md
Version: 1.0
Summary: Thay thế cơ chế volume giả lập bằng kết nối trực tiếp Windows Core Audio API (IAudioEndpointVolume qua ctypes COM thuần). Bố trí dòng bấm Volume ở ngay trang đầu Shortcut Panel, bấm để hiện Volume Slider HUD hiển thị và điều khiển 100% âm lượng thực tế của máy.

---

## Architecture — 2026-11-09

Pattern: Windows Core Audio COM Endpoint + Click-to-Slider HUD Flow
ADR-007: Điều khiển Âm lượng Thực tế qua Windows Core Audio Endpoint (ctypes COM ole32.dll) → docs/adr/ADR-007-real-volume-endpoint-coreaudio.md


---

## Tasks — 2026-11-09

Total: 5 tasks, 2h estimate
Path: docs/planning/f008-real-volume-endpoint-control.tasks.md
Batch 1: TSK-042, TSK-043, TSK-044
Batch 2: TSK-045, TSK-046
