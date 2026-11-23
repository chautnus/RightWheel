# BATCH 3: Python Command Palette Modernization & Build

feature: f016-v3-ui-rightwheel-customization-and-draw-gestures
batch: 3
tasks: T-95, T-96

## Tasks

### T-95: Modernize src/features/shortcut_panel/ui/panel_window.py
- Cập nhật `panel_window.py`:
  - Nâng chiều rộng cửa sổ lên `_W = 320` chuẩn Raycast floating HUD.
  - Tích hợp `ActionDispatcher`: Thực thi tất cả các loại item (Shortcut, App, URL, Run Shell, Sequence Macro, Text, WebClip) thông qua `ActionDispatcher`.
  - Tích hợp `ConfigReloadWatcher`: Lắng nghe thay đổi file cấu hình từ WebView2 để tự động gọi `logic.reload_config()` mà không cần khởi động lại ứng dụng.
  - Gỡ bỏ lệnh gọi pop-up Tkinter cũ `show_welcome(self._root)` trong `_run()` để tránh đè lên giao diện Welcome V3.
  - Khi người dùng chọn action `open_settings`, kích hoạt `open_settings_adaptive()` để mở WebView2 Settings.
- Cập nhật các chuỗi ngôn ngữ trong `src/core/i18n.py` và `src/features/i18n/` liên quan đến Welcome/Wizard.

### T-96: Automated Tests, PyInstaller Rebuild & Git Remote Push
- Chạy toàn bộ test suite: `pytest`.
- Đóng gói file thực thi độc lập: `python -m PyInstaller RightWheel.spec --noconfirm`.
- Xác minh file `dist/RightWheel.exe` tạo mới thành công.
- Tự động `git add`, `git commit` và `git push origin main`.
- Cập nhật báo cáo `docs/planning/f016-v3-ui-rightwheel-customization-and-draw-gestures.report.md`.

## Verification
- `pytest` 100% passed.
- `dist/RightWheel.exe` tồn tại và có kích thước ~30MB.
- `git status` clean và đã push remote.
