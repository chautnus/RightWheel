# ADR-007: Điều khiển Âm lượng Thực tế qua Windows Core Audio Endpoint (ctypes COM) & Click-to-Slider Flow

## Trạng thái
Accepted

## Ngữ cảnh
F-006 và F-007 đã cố gắng đưa Volume Control vào Shortcut Panel. Tuy nhiên:
1. Cơ chế trước đây sử dụng phím tắt giả lập `VK_VOLUME_UP` / `VK_VOLUME_DOWN` và khởi tạo slider ở mức 50% tương đối. Ứng dụng không thể biết âm lượng thật của máy là bao nhiêu và không đồng bộ với thanh volume thật của Windows.
2. Việc nhồi một thanh widget trực tiếp trên đầu Shortcut Panel làm vỡ trải nghiệm cuộn menu và gây vướng víu.
3. Người dùng yêu cầu: Quản lý volume theo đúng thực tế máy tính (không giả lập) và có một dòng bấm riêng ở ngay trang đầu của Panel, bấm vào thì mở thanh trượt Volume Slider.

## Các quyết định kiến trúc

### 1. Dịch vụ Windows Core Audio API thuần ctypes (`volume_service.py`)
- **Giao diện COM**: Sử dụng Windows Core Audio API có sẵn trên mọi phiên bản Windows 10/11 từ `ole32.dll`.
  - `CLSID_MMDeviceEnumerator`: `{BCDE0395-E52F-467C-8E3D-C4579291692E}`
  - `IID_IMMDeviceEnumerator`: `{A95664D2-9614-4F35-A746-DE8DB63617E6}`
  - `IID_IAudioEndpointVolume`: `{5CDF2C82-841E-4546-9722-0CF74078229A}`
- **VTable binding**:
  - `GetMasterVolumeLevelScalar` (VTable index 9): Đọc âm lượng thực tế hệ thống (0.0 đến 1.0).
  - `SetMasterVolumeLevelScalar` (VTable index 7): Cài đặt âm lượng thực tế hệ thống (0.0 đến 1.0).
  - `GetMute` (VTable index 15) và `SetMute` (VTable index 14).
- **An toàn thread (Thread-safety)**: Bọc hàm khởi tạo COM `CoInitialize` / `CoUninitialize` an toàn trên mọi thread gọi (Tkinter thread hoặc Background worker).

### 2. Dòng bấm Volume tại trang đầu Shortcut Panel & Loại bỏ Mini-Widget trên Header
- **Gỡ bỏ**: Xóa bỏ `_render_vol_bar` nhồi nhét trên đầu header của `panel_window.py`.
- **Dòng bấm ở trang đầu**:
  - Mục `show_volume_slider` nằm ở trang đầu (root list) của `shortcuts.json`.
  - Trong `_render()` của `panel_window.py`: Hiển thị rõ ràng: `🔊 Volume: {int(current_vol * 100)}%`.
  - Khi người dùng click chuột hoặc ấn phím số tương ứng: Shortcut Panel đóng lại (`hide()`) và kích hoạt mở `VolumeOverlay` tại vị trí chuột.

### 3. Đồng bộ 100% Âm lượng Thực tế trên Capsule HUD (`volume_overlay.py`)
- Khi `VolumeOverlay.show()` được gọi:
  - Gọi `volume_service.get_master_volume()` để lấy đúng mức âm lượng thực tế hiện tại của máy (ví dụ `0.68`).
  - Gán `self._level = real_vol` và hiển thị chính xác `68%`, icon loa phù hợp.
- Khi cuộn chuột trên HUD:
  - Gọi `volume_service.step_volume(delta, step)` để cập nhật âm lượng hệ thống thực tế của Windows.
  - Cập nhật hiển thị thanh trượt và nhãn % tức thì.

## Hậu quả & Đánh giá tác động
- **Tích cực**:
  - Âm lượng hiển thị và điều chỉnh trùng khớp 100% với Windows Volume.
  - Loại bỏ hoàn toàn sự lộn xộn ở header của Shortcut Panel, trả lại giao diện tối giản, thanh thoát.
  - 0 dependency bên ngoài mới, file mã nguồn độc lập, dễ bảo trì.
- **Tuân thủ giới hạn**: Tất cả các file duy trì dưới 250 dòng (SYSTEM LOCK).
