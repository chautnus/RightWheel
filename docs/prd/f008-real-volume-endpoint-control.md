---
id: prd_f008-real-volume-endpoint-control_20261109
title: "Real Windows Master Volume & Click-to-Slider Flow (F-008)"
status: draft
version: 1.0
author: Antigravity / Claude
created: 2026-11-09
updated: 2026-11-09
tags: [volume-control, core-audio, com, endpoint-volume, shortcut-panel, hud, ctypes]
summary: "Thay thế cơ chế volume giả lập bằng kết nối trực tiếp Windows Core Audio API (IAudioEndpointVolume qua ctypes COM thuần). Bố trí dòng bấm Volume ở ngay trang đầu Shortcut Panel, bấm để hiện Volume Slider HUD hiển thị và điều khiển 100% âm lượng thực tế của máy."
---

# PRD: Real Windows Master Volume & Click-to-Slider Flow (F-008)

## 1. Overview
**Problem**:
1. Phím tắt và widget volume cũ chỉ giả lập mức âm lượng 50% tương đối, không đọc được âm lượng thực tế từ hệ điều hành Windows, gây sai lệch trải nghiệm người dùng.
2. Thiết kế nhồi widget volume trên đầu Shortcut Panel vướng víu và phá vỡ luồng cuộn chọn phím tắt mượt mà.

**Solution**:
1. Xây dựng `volume_service.py` dựa trên Windows Core Audio Endpoint (`IAudioEndpointVolume`) bằng `ctypes` thuần: Đọc và ghi đúng mức âm lượng thực tế (0% đến 100%).
2. Đặt một dòng menu chuyên biệt "🔊 Âm lượng (X%)" ngay trang đầu (root list) của Shortcut Panel. Khi người dùng click hoặc ấn phím số: Panel đóng và hiện Volume Slider HUD tại con trỏ chuột.
3. Volume Slider HUD khởi tạo với đúng mức âm lượng thực tế của máy, cuộn chuột để tăng/giảm âm lượng thực tế tức thì.

**Success Metrics**:
- Âm lượng trên slider trùng khớp 100% với âm lượng của Windows Volume Tray.
- Luồng tương tác tự nhiên: Bấm dòng Volume ở trang đầu -> Hiện slider -> Cuộn chuột chỉnh âm lượng thật.
- 0 dependency ngoài (chỉ dùng `ctypes` và `ole32.dll` có sẵn trên Windows).

## 2. User Stories & Acceptance Criteria

### US-024: Windows Core Audio Service thuần ctypes (`volume_service.py`)
**As a** ứng dụng RightWheel,  
**I want to** giao tiếp trực tiếp với Windows Core Audio API,  
**So that** tôi có thể lấy và cài đặt mức âm lượng chính xác của máy tính mà không cần cài thêm thư viện.
**Acceptance Criteria:**
- [ ] Hàm `get_master_volume() -> float` trả về giá trị âm lượng thực tế từ 0.0 đến 1.0.
- [ ] Hàm `set_master_volume(level: float) -> None` thay đổi âm lượng thực tế của Windows.
- [ ] Hàm `step_volume(delta: int, step: float = 0.05) -> float` thay đổi âm lượng thực tế theo bước nhảy và trả về giá trị mới.
- [ ] Hoạt động ổn định trên thread Tkinter (an toàn với COM apartment threading qua CoInitialize/CoUninitialize).

### US-025: Dòng bấm Volume tại trang đầu Shortcut Panel
**As a** người dùng Shortcut Panel,  
**I want to** thấy một dòng mục Volume rõ ràng ngay trang đầu kèm mức % hiện tại,  
**So that** tôi có thể bấm vào để mở thanh trượt mà không bị vướng header.
**Acceptance Criteria:**
- [ ] Gỡ bỏ widget thanh volume nhồi nhét trên đầu header của `panel_window.py`.
- [ ] Trang đầu Shortcut Panel luôn có một dòng menu hiển thị: ví dụ `🔊 Âm lượng (XX%)` hoặc `🔊 Volume (XX%)`.
- [ ] Bấm click chuột trái hoặc ấn phím số tương ứng sẽ đóng Shortcut Panel và mở ngay Volume Slider HUD.

### US-026: Volume Slider Capsule HUD đồng bộ âm lượng thực tế
**As a** người dùng đang điều chỉnh âm lượng,  
**I want to** thanh trượt hiển thị đúng mức âm lượng hiện tại của máy và cuộn chuột đổi âm lượng thật,  
**So that** tôi kiểm soát chính xác mức âm thanh mong muốn.
**Acceptance Criteria:**
- [ ] Khi HUD mở lên, slider và nhãn % hiển thị đúng mức âm lượng thực tế của máy tính.
- [ ] Cuộn chuột lên/xuống làm thay đổi âm lượng thực tế của máy tính và cập nhật hiển thị slider tức thì.
- [ ] Tự ẩn sau 3 giây hoặc khi click ngoài / bấm ESC.

## 3. Constraints & Dependencies
- Tuyệt đối không dùng `pycaw` hay `comtypes`.
- Toàn bộ file mã nguồn tuân thủ SYSTEM LOCK (≤ 250 dòng).
- Giữ nguyên các hành vi LOCKED trong `CLAUDE.md`.
