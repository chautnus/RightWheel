---
id: proj_architecture_20260430
type: project
title: "MouseHotkey v2 — Architecture Decisions"
tags: [architecture, ctypes, hook, state-machine, tkinter, feature-sliced]
keywords: [WH_MOUSE_LL, INJECTED_MARKER, wants_moves, state-machine, panel, tray]
status: active
created: 2026-04-30
updated: 2026-05-07
summary: "Core architectural decisions for the ctypes mouse hook, state machine, and UI threading model."
---

## Architecture: MouseHotkey v2

### Why Feature-Sliced Design
Two independent features (mouse_mapper, shortcut_panel) with zero cross-dependency except a single `panel` reference injected at wire-up time in `main.py`. This keeps each feature testable and replaceable.

**Structure:**
```
src/features/
├── mouse_mapper/
│   ├── logic/         mouse_mapper_logic.py  (state machine)
│   ├── services/      mouse_hook_service.py, hotkey_service.py
│   ├── types/         mouse_mapper_types.py
│   └── ui/            tray_ui.py
└── shortcut_panel/
    ├── logic/         panel_logic.py
    ├── services/      config_service.py, shortcut_executor.py,
    │                  window_service.py, startup_service.py
    ├── types/         panel_types.py
    └── ui/            panel_window.py, settings_window.py,
                       profile_editor.py, folder_editor_dialog.py,
                       welcome_window.py
```

### Why ctypes WH_MOUSE_LL (not pynput)
pynput cannot suppress individual mouse events per-event — it either suppresses all or none. WH_MOUSE_LL via ctypes gives us `CallNextHookEx` vs return non-zero control per event.

**How to apply:** Any mouse event interception must stay in `mouse_hook_service.py` using the ctypes pattern.

### INJECTED_MARKER = 0xFEED1234
When we synthesize a right_down/right_click via `SendInput`, the hook sees it again. We stamp `dwExtraInfo = 0xFEED1234` and skip events with that marker. Without this, synthetic events loop back through our state machine.

**How to apply:** Always check `extra_info == INJECTED_MARKER` at the top of the hook proc before any other logic.

### wants_moves() Fast-Path
Edge fires 200+ WM_MOUSEMOVE per second. Routing all of them through Python's ctypes boundary causes the 300ms Windows hook timeout. `wants_moves()` returns `True` only while state == RIGHT_HELD; otherwise the hook skips WM_MOUSEMOVE entirely (returns CallNextHookEx immediately in C callback).

**How to apply:** Any new event type that is high-frequency must have a similar fast-path gate.

### try/except in Hook Proc
If Python raises inside the ctypes callback and the function returns a ctypes object instead of a plain int, Windows gets garbage and the hook dies silently. The try/except wraps the entire dispatch and returns `0` on any exception.

### State Machine
```
IDLE → RIGHT_HELD (on right_down)
RIGHT_HELD → GESTURE (on move ≥ threshold) → re-injects right_down for Edge
RIGHT_HELD → SCROLLING (on scroll)
any → IDLE (on right_up)
```
GESTURE: suppress original right_down was already done; re-inject so Edge/browser gets it for their own gesture system.

### Threading Model
- Hook thread: calls `logic.handle()` under `threading.Lock`
- tkinter thread: daemon thread; uses `queue.Queue` + `root.after(20, pump)` loop
- Callbacks from logic post into queue; UI reads from queue on main tkinter thread

### Focus Management — overrideredirect Windows (v2.2)
Panel dùng `overrideredirect(True)` để frameless. Hệ quả: Windows **không track focus** cho loại window này — khi bị destroy, focus không tự về cửa sổ trước.

**Pattern bắt buộc khi thực thi shortcut:**
1. `show()` (hook thread): gọi `GetForegroundWindow()` → lưu `_prev_hwnd` trước khi panel steal focus
2. `select_current()` (tkinter thread): gọi `SetForegroundWindow(_prev_hwnd)` **trước** `hide()` — lúc này panel vẫn focused, process vẫn là foreground, Windows chấp nhận
3. `hide()` → panel bị destroy
4. `Timer(0.25, execute)` → đợi focus transition xong rồi `SendInput`

**Rule:** `SetForegroundWindow` chỉ được chấp nhận từ foreground process. Gọi sau khi window bị destroy → silently fail.

### Quy tắc tkinter: Chỉ Một tk.Tk() Duy Nhất (v2.5)

Tkinter chỉ hỗ trợ một `tk.Tk()` instance trong một process. Mọi cửa sổ phụ (dialogs, settings, welcome) đều phải dùng `tk.Toplevel(root)` trên cùng một root.

**Pattern bắt buộc:**
```python
# Trong panel_window._run() — root duy nhất của app
self._root = tk.Tk()
self._root.withdraw()
show_if_first_run(self._root)  # truyền root, KHÔNG tạo Tk() mới trong welcome_window

# Mọi dialog/window đều nhận root hoặc parent để tạo Toplevel
win = tk.Toplevel(root)
```

**Hậu quả của vi phạm:** Khi một Toplevel bị destroy, focus chuyển về Tk root thứ hai (nếu có) → zombie window xuất hiện, không đóng được.

---

### after(0) Pattern — Defer Cleanup Sau Destroy Events (v2.5)

Khi một Toplevel bị `destroy()`, tkinter post một chuỗi focus-transfer events vào event queue. Nếu gọi `root.withdraw()` đồng bộ ngay sau `destroy()`, withdraw chạy TRƯỚC khi events được xử lý → Windows deiconify root sau khi withdraw hoàn thành.

**Pattern bắt buộc khi destroy một Toplevel:**
```python
def _save(self) -> None:
    if self._win and self._win.winfo_exists():
        self._win.destroy()
    self._win = None
    self._root.after(0, self._root.withdraw)  # defer đến sau khi event queue flush
```

**Rule:** Bất kỳ hành động nào cần chạy sau khi destroy events được xử lý → dùng `root.after(0, callback)`, KHÔNG gọi đồng bộ.

---

### ttk Dark Theme — Bắt Buộc Dùng "clam" (v2.5)

Windows ttk default theme ("vista"/"xpnative") dùng Windows visual styles API, override toàn bộ custom color settings trong `style.configure()`. Để dark theme hoạt động trên ttk widgets (đặc biệt Notebook tabs), phải dùng theme "clam".

```python
style = ttk.Style()
style.theme_use("clam")  # PHẢI gọi trước bất kỳ configure nào
style.configure("TNotebook", background=_BG, borderwidth=0)
style.configure("TNotebook.Tab", background=_BG2, foreground=_FG,
                padding=[14, 6], font=("Segoe UI", 10))
style.map("TNotebook.Tab",
          background=[("selected", _ACC), ("active", "#3a3a3a")],
          foreground=[("selected", "#fff"), ("active", "#fff")])
```

**Rule:** Mọi usage của ttk widgets với custom dark colors trên Windows → LUÔN bắt đầu bằng `style.theme_use("clam")`.

---

### Alt+Tab Sequencing
`begin_switch(forward)` → sends Alt down + Tab down/up. Each subsequent `cycle()` sends Tab down/up (Alt stays held). `end_switch()` sends Alt up. **No KEYEVENTF_EXTENDEDKEY on VK_MENU** — using extended key flag breaks Alt+Tab on some Windows builds.
