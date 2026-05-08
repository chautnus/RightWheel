---
id: proj_key_recorder_build_fix_20260506
type: project
title: "Key Recorder Dialog & PyInstaller tkinter Fix"
tags: [settings, tkinter, pyinstaller, key-recorder, build]
keywords: [_KeyRecorder, KeyPress, hiddenimports, excludes, tkinter]
status: active
created: 2026-05-06
updated: 2026-05-06
summary: "Added key recorder dialog for capturing shortcuts by pressing keys; fixed tkinter missing from PyInstaller build."
---

## 1. Key Recorder Dialog (`_KeyRecorder`)

### Why
Settings window trước đây dùng `simpledialog.askstring()` — user phải **gõ text** `ctrl+shift+v` thủ công. User cần **nhấn phím thật** để ghi nhận tổ hợp.

### What
Thêm class `_KeyRecorder(tk.Toplevel)` vào `settings_window.py` (trước class `SettingsWindow`):
- Modal dialog, `grab_set()` + `focus_set()`
- Bind `<KeyPress>` / `<KeyRelease>` để track modifier state (`_mods: set[str]`)
- `_MOD_MAP`: map keysym tkinter (`Control_L`, `Shift_R`, `Alt_L`, `Super_L`…) → tên chuẩn (`ctrl`, `shift`, `alt`, `win`)
- Khi nhấn phím không phải modifier: build string theo thứ tự `ctrl+shift+alt+win+<key>`, hiển thị real-time
- `Enter` → confirm, `Esc` / close → cancel
- Class method `ask(parent, init="") -> str | None`

### How to apply
Thay `self._ask("...", "Keys ...")` bằng `_KeyRecorder.ask(self._win, init)` tại 2 chỗ:
- `_add_shortcut()`: không có init
- `_edit()`: init = `item.get("keys", "")`

---

## 2. PyInstaller Build Fix — tkinter Missing

### Why
`MouseHotkey.spec` cũ (v1) có `tkinter` trong danh sách `excludes` để giảm size — v1 không dùng tkinter. V2 dùng tkinter cho panel và settings → exe crash ngay khi import.

### What
Sửa `MouseHotkey.spec`:
- **Xóa** `'tkinter'` khỏi `excludes`
- **Thêm** vào `hiddenimports`: `'tkinter'`, `'tkinter.simpledialog'`, `'_tkinter'`

### How to apply
Mỗi khi thêm dependency mới, kiểm tra `excludes` trong spec trước khi build. Nếu thấy module bị exclude mà code đang dùng → di chuyển sang `hiddenimports`.

---

## 3. PermissionError Khi Build

### Cause
Exe cũ đang chạy → Windows lock file → PyInstaller không thể ghi đè.

### Fix
Tắt process trước khi build: `taskkill /F /IM MouseHotkey.exe` hoặc tắt từ system tray.

---

## Build Info
- **File:** `dist/MouseHotkey.exe`
- **Size:** ~30 MB (tăng từ 27 MB do thêm tkinter + Tcl/Tk)
- **Build date:** 2026-05-06
- **Python:** 3.14.3 / PyInstaller 6.20.0
