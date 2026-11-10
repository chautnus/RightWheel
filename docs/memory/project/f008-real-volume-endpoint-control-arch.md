# F-008 — Architecture notes (ADR-007)

Nguồn phân tích: thực thi qua kênh khác (không qua MCP bridge của session này) — Claude validate độc lập 2026-11-10.

- `volume_service.py`: Windows Core Audio `IAudioEndpointVolume` qua pure `ctypes` COM (0 dependency, không `pycaw`) — đọc/ghi % âm lượng thực tế thay vì giả lập.
- **BUG NGHIÊM TRỌNG đã fix (xem [[antigravity-calibration]] 2026-11-09 entry)**: `_CLSID_MMDeviceEnumerator` GUID thiếu 1 byte Data4 → `CoCreateInstance` luôn fail âm thầm (try/except nuốt lỗi) → tính năng không hoạt động từ lúc ship tới lúc phát hiện. Bài học: code dùng raw COM GUID/vtable PHẢI có verify-cmd gọi thực nghiệm thật (so giá trị set/get round-trip), không chỉ py_compile.
- Click-to-slider flow: bỏ mini-widget header, dòng Volume %thật ở trang đầu Panel, click/phím số mở Capsule HUD đồng bộ giá trị thật.
