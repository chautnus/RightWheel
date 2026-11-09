# Design Blueprint: Real Windows Master Volume & Click-to-Slider Flow (F-008)

## 1. Modules bị chạm (Existing Modules)
- `src/features/shortcut_panel/ui/panel_window.py` (~238 dòng -> rút gọn sau khi bỏ widget header còn ~205 dòng)
- `src/features/shortcut_panel/ui/volume_overlay.py` (~181 dòng -> chuyển sang gọi `volume_service` ~160 dòng)
- `src/features/shortcut_panel/ui/general_volume_tab.py` (~138 dòng -> cập nhật ~130 dòng)

## 2. File mới (New Module)
- `src/features/shortcut_panel/services/volume_service.py` (~110 dòng)
  - Trách nhiệm: Giao tiếp với Windows Core Audio API (`IAudioEndpointVolume` qua COM `ole32.dll`) để lấy và gán âm lượng thực tế của máy.
  - Exports:
    - `get_master_volume() -> float` (trả về giá trị 0.0 đến 1.0)
    - `set_master_volume(level: float) -> None`
    - `step_volume(delta: int, step: float = 0.05) -> float`
    - `get_mute() -> bool`, `set_mute(mute: bool) -> None`

## 3. Quy chuẩn màu sắc UI (WCAG AA Contrast Check)
- **Shortcut Panel (`panel_window.py`)**:
  - Dòng menu Volume ở trang đầu: Text `#ffffff` trên Background `#27272a` (Selected, ratio ~13:1 ✓) hoặc `#a1a1aa` trên `#121214` (Normal, ratio ~7:1 ✓).
  - Không còn canvas widget trên header.
- **Volume Overlay HUD (`volume_overlay.py`)**:
  - Nền Capsule `#18181b`, viền `#3f3f46`.
  - Icon & Text %: Text `#ffffff` trên Background `#18181b` (ratio ~16:1 ✓).
  - Thanh tiến trình: `#0078d4` trên `#27272a`.

## 4. Thứ tự triển khai
1. `volume_service.py` (Core Audio endpoint COM logic)
2. `panel_window.py` (loại bỏ widget header, bổ sung cập nhật nhãn âm lượng thật vào dòng menu trang đầu)
3. `volume_overlay.py` (tích hợp `volume_service` đọc âm lượng thật khi mở, set âm lượng thật khi cuộn)
4. `general_volume_tab.py` (cập nhật hiển thị và cấu hình)
5. Kiểm tra cú pháp tĩnh, kiểm tra độ dài file ≤ 250 dòng, build lại `.exe`
