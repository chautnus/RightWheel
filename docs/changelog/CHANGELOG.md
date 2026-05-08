---
id: changelog_20260430
type: changelog
title: "MouseHotkey Changelog"
tags: [changelog, versions]
keywords: [v1, v2, releases, fixes]
status: active
created: 2026-04-30
updated: 2026-05-07
summary: "Version history for MouseHotkey from v1.0.0 to v2.5.0."
---

# Changelog

All notable changes to MouseHotkey are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.5.0] — 2026-05-07

### Added
- **Welcome / onboarding screen** (`welcome_window.py`) — hiển thị lần đầu chạy app, không hiện lại
  - Thiết kế hai tông màu: top nhạt (`#f5f5f5`) + body tối (`#141414`)
  - Feature list: icon trắng, trigger text xanh, mô tả xám
  - Checkbox "Run on startup"; nút "Get Started" → lưu `"welcomed": true` vào config
- **Windows startup toggle** (`startup_service.py`) — winreg `HKCU\...\Run\MouseHotkey`
  - `enable()`, `disable()`, `is_enabled()` — chỉ hoạt động khi chạy từ exe (PyInstaller frozen)
  - Toggle xuất hiện ở cả Welcome screen và footer của Settings
- **`folder_editor_dialog.py`** — modal riêng để edit shortcut bên trong folder
  - Full CRUD: Add, Edit, Delete, Up, Down; reuses `_AskDialog` từ settings_window
- Settings footer: startup checkbox + "💾 Save & Close" cạnh nhau (không còn button riêng lẻ)

### Fixed
- **Black window sau Save & Close (nguyên nhân 1):** `welcome_window.py` tạo `tk.Tk()` riêng → hai Tk instances xung đột → zombie window. Fix: welcome dùng `Toplevel(root)` trên cùng root của panel.
- **Black window vẫn còn (nguyên nhân 2):** `destroy()` post focus-transfer events vào queue; `root.withdraw()` đồng bộ chạy trước khi events đó được xử lý → root hiện ra sau withdraw. Fix: `root.after(0, root.withdraw)` — defer đến sau khi event queue flush.
- **Tab text xám trên nền trắng:** Windows ttk theme "vista"/"xpnative" override custom colors của Notebook. Fix: `style.theme_use("clam")`.
- **Folder shortcut editing không hoạt động:** `_edit()` chỉ rename label folder, không mở children. Fix: route folder clicks sang `FolderEditorDialog`.
- **Double emoji trên folder items:** label lưu là `"📁 Name"` nhưng `_refresh()` thêm `📁` nữa. Fix: bỏ prefix khỏi format string trong `_refresh()`.
- **Welcome button bị co nhỏ:** hardcode 460px block `fill="x"`. Fix: auto-size từ `winfo_reqwidth/reqheight`; button dùng `fill="x"` + `ipady=10`.
- **Welcome icons không thấy / header không đọc được:** icons → `fg="white"`; header "MouseHotkey" → `fg="#111111"` trên `bg="#f5f5f5"`.

### Changed
- `welcome_window.py`: standalone `tk.Tk()` → `tk.Toplevel(root)`, gọi từ `panel_window._run()` sau `root.withdraw()`
- `settings_window.py`: `ttk.Notebook` với "Default" + "Profiles" tab; `style.theme_use("clam")`; VERSION = "2.5.0"
- `main.py`: bỏ import welcome_window (đã chuyển vào panel_window._run)

### Build
- `dist/MouseHotkey.exe` v2.5.0 (07/05/2026)

---

## [2.4.0] — 2026-05-07

### Added
- **Context-aware profiles** — bộ shortcut khác nhau theo app đang active
  - `window_service.py` (NEW): ctypes-only — `GetWindowTextW`, `GetClassNameW`, `QueryFullProcessImageNameW`; không dùng psutil
  - `config_service.py` viết lại: schema v2, `resolve_profile()`, AND-logic `_matches()`, auto-migration v1→v2
  - `profile_editor.py` (NEW): `ProfileEditor(tk.Frame)` — left list panel + right detail panel; full CRUD match rules + shortcuts
  - `panel_logic.py`: wired window detection + profile resolution vào `show()`; property `active_profile`
- Schema v2: `{ "version": 2, "default": [...], "profiles": [{name, match:[{by, value}], shortcuts:[...]}] }`
- v1 → v2 migration tự động trong `config_service.load()` (rename `"shortcuts"` → `"default"`, thêm `"profiles": []`)
- Match rule types: `exe` (basename, case-insensitive), `title_contains`, `class_name` (exact)
- Panel: blue badge "◈ ProfileName" khi active profile không phải Default

### Changed
- Config key `"shortcuts"` → `"default"` (breaking change, mitigated by auto-migration)
- `types/panel_types.py`: added `MatchRule` và `Profile` dataclasses

### Build
- `dist/MouseHotkey.exe` v2.4.0 (07/05/2026, intermediate build)

---

## [2.2.0] — 2026-05-07

### Added
- Version hiển thị trong Settings window (góc trên phải: `v2.2.0`)
- Hằng số `VERSION` trong `settings_window.py`

### Fixed
- **Shortcut không thực thi** — root cause: `SetForegroundWindow` bị Windows reject silently khi gọi từ background timer thread (process không còn là foreground sau khi panel bị destroy)
- Fix: gọi `SetForegroundWindow(prev_hwnd)` trong `select_current()` TRƯỚC `hide()`, trên tkinter thread, trong khi panel vẫn focused → Windows chấp nhận → focus về đúng cửa sổ đích
- Tăng delay trước `SendInput` từ 150ms → 250ms để đảm bảo focus transition hoàn tất

### Changed
- `panel_logic.py`: loại bỏ `_fire()` method; logic focus restore giờ nằm inline trong `select_current()`
- `settings_window.py`: title bar và header đều hiển thị version

### Build
- `dist/MouseHotkey.exe` ~30 MB (07/05/2026)

---

## [2.1.0] — 2026-05-06

### Added
- `_KeyRecorder` dialog trong `settings_window.py`: user nhấn phím thật thay vì gõ text để ghi shortcut
- Real-time preview tổ hợp phím trong dialog (e.g. `ctrl+shift+v`)
- Hỗ trợ modifier: Ctrl, Shift, Alt, Win (cả Left/Right variant)

### Fixed
- `MouseHotkey.spec`: tkinter bị exclude trong spec cũ → exe crash với `ModuleNotFoundError: No module named 'tkinter'`
  - Xóa `tkinter` khỏi `excludes`; thêm `tkinter`, `tkinter.simpledialog`, `_tkinter` vào `hiddenimports`

### Build
- `dist/MouseHotkey.exe` ~30 MB (Python 3.14.3 / PyInstaller 6.20.0)

---

## [2.0.0] — 2026-04-30

### Added
- Shortcut panel: frameless dark floating window triggered by RMB+scroll-up
- Panel navigation: scroll up/down, number keys 0–9, Enter to activate
- Folder support in panel: 2-level hierarchy, Esc to go back
- Settings window: add/edit/delete/reorder shortcuts and folders (tkinter Listbox CRUD)
- Config persistence: `%APPDATA%\MouseHotkey\shortcuts.json`
- `on_settings` callback wired from tray → settings window open
- Feature-Sliced Design architecture: mouse_mapper + shortcut_panel features
- `PanelLogic` callbacks: `on_show`, `on_hide`, `on_update`
- `shortcut_executor.py`: VK_MAP + SendInput key sequence

### Changed
- Refactored from single-file v1 to multi-module Feature-Sliced structure
- `MouseMapperLogic` now holds optional `panel: PanelLogic` reference (injected in main.py)
- Scroll-up: opens panel (was no-op in v1)
- Scroll-down: Alt+Tab cycle (unchanged behavior, cleaner implementation)

### Fixed
- Mouse freeze: suppress both right_down AND right_up; re-inject synthetic right_click on tap
- Edge gesture broken: added GESTURE state with retroactive `inject_right_down()`
- Hook dying in Edge: try/except guard + `wants_moves()` fast-path for WM_MOUSEMOVE
- Context menu after scroll: removed orphan `inject_right_cleanup()` call
- Spurious Alt+Tab: added `if prev == IDLE: return False` guard in `_on_right_up()`
- Alt+Tab not working: removed `KEYEVENTF_EXTENDEDKEY` from VK_MENU SendInput

---

## [1.0.0] — 2026-04-29

### Added
- WH_MOUSE_LL ctypes global mouse hook (Windows-only)
- RMB+scroll-down → Alt+Tab (begin/cycle/end pattern)
- RMB+drag passthrough for Edge gestures (GESTURE state)
- INJECTED_MARKER (0xFEED1234) on dwExtraInfo to skip synthetic events
- `wants_moves()` fast-path to skip WM_MOUSEMOVE when not RIGHT_HELD
- System tray icon (pystray): green/red dot, enable toggle, exit
- PyInstaller --onefile packaging → dist/MouseHotkey.exe (~16MB)
- GitHub repo: https://github.com/chautnus/mousehotkey (tagged v1.0.0)
- `run.bat` for dev launch

### Fixed
- ctypes c_long return type: return plain int not ctypes.c_long object
- pynput replacement: rewrote to ctypes WH_MOUSE_LL for per-event suppression
