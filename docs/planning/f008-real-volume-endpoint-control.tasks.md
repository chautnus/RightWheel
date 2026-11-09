# Tasks: Real Windows Master Volume & Click-to-Slider Flow (f008-real-volume-endpoint-control)

Total: 5 tasks | Estimate: 2h | Status: 5/5 Done

## Tasks List

### Batch 1: Real Volume Core Audio Service & HUD Sync
- [x] **TSK-042**: Xây dựng `src/features/shortcut_panel/services/volume_service.py` kết nối trực tiếp Windows Core Audio Endpoint qua ctypes COM (US-024).
- [x] **TSK-043**: Cập nhật `panel_window.py`: Gỡ bỏ mini-widget trên header, đưa dòng bấm Volume kèm % thật vào trang đầu, mở Volume HUD khi chọn (US-025).
- [x] **TSK-044**: Cập nhật `volume_overlay.py`: Khởi tạo slider với âm lượng thật của máy, cuộn chuột thay đổi âm lượng thực tế của Windows (US-026).

### Batch 2: Settings UI, Verification & Rebuild
- [x] **TSK-045**: Cập nhật `general_volume_tab.py` cho cấu hình volume thực tế và dọn dẹp các tùy chọn cũ không còn phù hợp (US-024).
- [x] **TSK-046**: Kiểm tra cú pháp (py_compile), kiểm tra giới hạn dòng (≤ 250 dòng), đóng tiến trình cũ và build lại `dist/RightWheel.exe` (US-024..US-026).
