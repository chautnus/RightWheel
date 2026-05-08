---
id: proj_ui_v2_5_redesign_20260507
type: project
title: "UI v2.5 — Welcome Screen, Startup Toggle, Settings Redesign"
tags: [ui, welcome, startup, settings, tkinter, winreg]
keywords: [welcome_window, startup_service, ttk.Notebook, folder_editor_dialog, onboarding]
status: active
created: 2026-05-07
updated: 2026-05-07
summary: "Welcome/onboarding screen, Windows startup toggle, Settings UI redesign với ttk.Notebook và folder editor dialog"
---

## Why

User yêu cầu:
1. Màn hình chào đón lần đầu chạy app — giới thiệu tính năng, không hiện lại
2. Toggle khởi động cùng Windows (registry)
3. Settings UI quá xấu — cần redesign đẹp hơn
4. Edit shortcut trong folder bị broken — cần dialog riêng

## What

### Files mới

#### `services/startup_service.py` (49 dòng)
Quản lý Windows registry startup entry.

```python
_RUN_KEY  = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "MouseHotkey"

def _exe_path() -> str:
    # Chỉ hoạt động khi frozen (PyInstaller exe)
    return sys.executable if getattr(sys, "frozen", False) else ""

def is_enabled() -> bool: ...   # QueryValueEx → True/False
def enable()    -> bool: ...    # SetValueEx REG_SZ với exe path
def disable()   -> None: ...    # DeleteValue, bỏ qua nếu không tồn tại
```

**Lưu ý:** `enable()` trả về `False` khi chạy từ source (dev mode). Không có registry pollution trong development.

---

#### `ui/welcome_window.py` (92 dòng)
First-run onboarding. Chỉ hiện khi `config["welcomed"]` chưa có / False.

**Kiến trúc:**
- `show_if_first_run(root: tk.Tk)` — nhận root từ panel_window, tạo Toplevel
- Gọi từ `panel_window._run()` SAU `self._root.withdraw()`, TRƯỚC `mainloop()`
- `root.wait_window(win)` — block mainloop đến khi user bấm "Get Started"

**Layout hai tông màu:**
```
┌─────────────────────────────┐  bg=#f5f5f5 (sáng)
│  🖱  (emoji 36pt)           │
│  MouseHotkey  (đen, bold)   │
│  Smart shortcuts on RMB     │
├─────────────────────────────┤  divider #dddddd
│  Feature list (tối #141414) │  bg=#1e1e1e (card)
│  🖱  RMB+Scroll Up  → ...   │  icon=white, trigger=blue, desc=gray
│  ⌨   Press key / click row  │
│  ...                        │
│  ☐ Run on startup           │  bg tối
│  [   Get Started →   ]      │  fill=x, ipady=10, bg=_ACC
└─────────────────────────────┘
```

**Auto-size:**
```python
win.update_idletasks()
w = max(win.winfo_reqwidth(), 460)
h = max(win.winfo_reqheight(), 400)
sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
```

**On close:**
```python
def _close() -> None:
    (startup_service.enable if sv.get() else startup_service.disable)()
    d = config_service.load()
    d["welcomed"] = True
    config_service.save(d)
    win.destroy()
```

---

#### `ui/folder_editor_dialog.py` (142 dòng)
Modal dialog cho CRUD shortcuts bên trong một folder item.

- Constructor: `FolderEditorDialog(parent, folder_idx, logic)` — `parent.wait_window()` block
- Listbox hiển thị: `"  LabelName   →   ctrl+v"`
- Buttons: ➕ Add, ✏ Edit, ✕ Del, ↑ Up, ↓ Down, ✓ Done
- Reuses `_AskDialog` từ `settings_window` (local import để tránh circular)
- Tất cả thao tác save config và gọi `logic.reload()`

---

### Files cập nhật

#### `ui/settings_window.py` (250 dòng — SYSTEM LOCK boundary)
- `ttk.Notebook` với 2 tabs: "Default" và "Profiles"
- `style.theme_use("clam")` — dark Notebook tabs
- `style.map` với `("active", "#3a3a3a")` cho hover state
- Footer: startup checkbox bên trái + "💾 Save & Close" bên phải
- `_edit()`: route folder items sang `FolderEditorDialog`
- `_refresh()`: folder items teal via `itemconfigure`, shortcuts có icon ⌨
- `_save()`: `root.after(0, root.withdraw)` — defer withdraw

**CẢNH BÁO:** File đang ở đúng 250 dòng. Mọi thêm logic mới cần extract sang module riêng trước.

#### `ui/panel_window.py` (158 dòng)
- Thêm import + gọi `show_if_first_run(self._root)` trong `_run()`
- Profile badge rendering (đã có từ v2.4)

#### `main.py` (35 dòng)
- Bỏ import và call welcome_window — đã chuyển vào panel_window._run()

## How to apply

### Thêm tính năng mới vào Settings
1. Kiểm tra `settings_window.py` ≤ 249 dòng trước khi thêm
2. Nếu > 249: extract logic sang module riêng (e.g. `shortcut_crud.py`)
3. Tab mới → thêm method `_build_[name]_tab()` và `nb.add(tab, text="...")`

### Thêm startup logic
- Dùng `startup_service.enable()` / `disable()` — returns `False` khi dev mode, safe to call
- `is_enabled()` để init checkbox state

### Welcome screen
- Config flag: `data["welcomed"] = True` sau khi user bấm Get Started
- Reset: xóa key "welcomed" khỏi config JSON để hiện lại màn hình welcome

## CLAUDE.md rules triggered

- Rule 2 (SYSTEM LOCK): settings_window.py bị monitor chặt tại 250 dòng
- Rule 3B (MACRO-TASK): /design-feature đã chạy cho profiles; welcome/startup là extension
- Rule 4: Targeted reads only cho các file liên quan
- Rule 5: /sync-memory sau khi hoàn thành
