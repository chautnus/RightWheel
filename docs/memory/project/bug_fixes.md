---
id: proj_bug_fixes_20260430
type: project
title: "MouseHotkey — Critical Bug Fixes & Root Causes"
tags: [bugs, ctypes, hook, alt-tab, context-menu]
keywords: [ghost-right-up, suppress, INJECTED_MARKER, freeze, hook-timeout]
status: active
created: 2026-04-30
updated: 2026-05-07
summary: "Root causes and fixes for all critical bugs found during v1→v2→v2.5 development."
---

## Critical Bugs and Fixes

---

### [v2.5] Black Window Sau Save & Close — Hai tk.Tk() Instances
**Symptom:** Sau khi bấm "Save & Close" trong Settings, xuất hiện một cửa sổ đen không đóng được. Chỉ đóng được khi exit app.

**Root cause (lần 1):** `welcome_window.py` tạo `tk.Tk()` riêng biệt. Tkinter chỉ cho phép MỘT `tk.Tk()` trong một process. Hai instances xung đột → khi Settings Toplevel bị destroy, focus chuyển về Tk root thứ hai (welcome's root) đang ẩn → nó hiện ra như zombie window.

**Fix:** `welcome_window.py` phải dùng `tk.Toplevel(root)` trên root của `panel_window._run()`. Gọi `show_if_first_run(self._root)` từ bên trong `_run()` sau `self._root.withdraw()`.

```python
# ĐÚNG — trong panel_window._run()
self._root = tk.Tk()
self._root.withdraw()
show_if_first_run(self._root)  # Toplevel trên cùng root, không tạo Tk() mới

# SAI — trong welcome_window.py (cũ)
root = tk.Tk()  # ← tạo Tk() thứ hai → zombie window
root.mainloop()
```

**Rule:** Toàn app chỉ được có MỘT `tk.Tk()`. Tất cả cửa sổ phụ dùng `tk.Toplevel(root)`.

---

### [v2.5] Black Window Vẫn Còn — Focus-Transfer Race Condition
**Symptom:** Sau fix lần 1, vẫn còn cửa sổ (lần này là cửa sổ profile) không đóng được sau Save & Close.

**Root cause:** Khi `Toplevel.destroy()` được gọi, Windows post một chuỗi focus-transfer events vào tkinter event queue (chuẩn bị chuyển focus về parent). Nếu `root.withdraw()` chạy ngay đồng bộ, nó chạy TRƯỚC khi các events đó được xử lý → sau khi events được xử lý, root đã withdraw rồi nhưng Windows vẫn deiconify nó để nhận focus → root bị hiện ra ngoài ý muốn.

**Fix:** Dùng `root.after(0, root.withdraw)` để defer withdraw đến sau khi event queue flush:

```python
def _save(self) -> None:
    ...
    if self._win and self._win.winfo_exists():
        self._win.destroy()
    self._win = None
    self._root.after(0, self._root.withdraw)  # flush events trước rồi mới withdraw
```

**Rule:** Bất kỳ cleanup nào cần chạy SAU khi destroy events được xử lý → dùng `root.after(0, callback)`.

---

### [v2.5] Tab Text Xám Trên Nền Trắng (ttk Theme Override)
**Symptom:** Các tab trong ttk.Notebook hiển thị chữ xám trên nền trắng, không đọc được.

**Root cause:** Windows ttk theme mặc định là "vista" hoặc "xpnative". Các theme này override toàn bộ custom color settings của `style.configure("TNotebook.Tab", ...)` — chúng dùng Windows visual styles API thay vì tkinter rendering.

**Fix:** `style.theme_use("clam")` — theme "clam" dùng tkinter tự render, không call Windows API → custom colors được tôn trọng.

```python
style = ttk.Style()
style.theme_use("clam")  # PHẢI đặt trước configure
style.configure("TNotebook", background=_BG, borderwidth=0)
style.configure("TNotebook.Tab", background=_BG2, foreground=_FG, ...)
style.map("TNotebook.Tab",
          background=[("selected", _ACC), ("active", "#3a3a3a")],
          foreground=[("selected", "#fff"), ("active", "#fff")])
```

**Rule:** Khi dùng ttk widget với custom dark colors trên Windows, LUÔN gọi `style.theme_use("clam")` trước.

---

### [v2.5] Double Emoji Trên Folder Items
**Symptom:** Folder items trong Listbox hiển thị "📁 📁 FolderName".

**Root cause:** Folder label được lưu vào config dưới dạng `"📁 FolderName"` (thêm prefix trong `_add_folder()`), nhưng `_refresh()` cũng thêm `📁 ` vào format string khi render.

**Fix:** Bỏ prefix emoji khỏi format string trong `_refresh()`:

```python
# SAI
self._lb.insert("end", f"  📁  {it['label']}  ({n} items)")

# ĐÚNG (label đã có 📁 rồi)
self._lb.insert("end", f"  {it['label']}  ({n} items)")
```

**Rule:** Không lưu display prefix (emoji, icon) vào data — hoặc lưu vào data, hoặc thêm khi render. Không cả hai.

---

### [v2.5] Folder Shortcut Editing Không Hoạt Động
**Symptom:** Chọn folder item → Edit → chỉ cho phép đổi tên folder, không edit được shortcuts bên trong.

**Root cause:** `_edit()` trong `settings_window.py` không kiểm tra `item.get("type") == "folder"` để route sang dialog riêng — nó xử lý mọi item như shortcut.

**Fix:** Thêm routing trong `_edit()` + tạo `folder_editor_dialog.py`:

```python
def _edit(self) -> None:
    idx = self._sel()
    if idx is None: return
    data = config_service.load()
    item = data["default"][idx]
    if item.get("type") == "folder":
        from .folder_editor_dialog import FolderEditorDialog
        FolderEditorDialog(self._win, idx, self._logic)
        self._refresh()
        return
    # ... xử lý shortcut bình thường
```

---

### [v2.2] Shortcut Execution Silently Fails (SetForegroundWindow rejected)
**Symptom:** Panel selects item, closes, but nothing happens — no shortcut fires. Affects all shortcuts including system-wide ones like Win+L.

**Root cause (layered):**
1. Panel dùng `overrideredirect(True)` — khi bị destroy, Windows **không tự khôi phục focus** về cửa sổ trước. SendInput gửi vào void.
2. Fix đầu (delay 150ms) không đủ — vấn đề là **không có cửa sổ nào có focus**, không phải thời gian.
3. Fix thứ hai (SetForegroundWindow trong `_fire()` thread) — **Windows reject silently**. Rule của Windows: chỉ foreground process mới được gọi SetForegroundWindow thành công. Lúc timer thread chạy (t+150ms), panel đã bị destroy, process không còn là foreground.

**Fix đúng (v2.2):** Gọi `SetForegroundWindow(prev_hwnd)` trong `select_current()` TRƯỚC `hide()`, trên tkinter thread, trong khi panel vẫn còn focused và process vẫn là foreground. Windows chấp nhận. Sau đó 250ms delay cho focus transition hoàn tất trước khi SendInput.

**Rule quan trọng:** `SetForegroundWindow` phải được gọi từ foreground process. Nếu gọi từ background thread sau khi window bị destroy → silently fail, không có exception.

**File:** `src/features/shortcut_panel/logic/panel_logic.py` → `select_current()`

```python
# ĐÚNG: gọi trước hide(), trên tkinter thread
if hwnd:
    ctypes.windll.user32.SetForegroundWindow(hwnd)
self.hide()
threading.Timer(0.25, shortcut_executor.execute, args=[keys]).start()

# SAI: gọi trong timer thread (process không còn là foreground)
# threading.Timer(0.15, self._fire, args=[hwnd, keys]).start()
```

### Mouse Freeze After RMB Hold
**Symptom:** After holding right mouse button, releasing it left the OS thinking RMB was still held — all left clicks stopped working.
**Root cause:** We suppressed `right_down` (returning non-zero from hook) but then let `right_up` pass through. OS received `right_up` without a matching `right_down` → stuck state.
**Fix:** Suppress both `right_down` AND `right_up`. Re-inject `right_click` (down+up pair with `INJECTED_MARKER`) when state was RIGHT_HELD at release time.

### Edge Gesture Broken
**Symptom:** Edge's "hold RMB + drag" gesture (back/forward) stopped working.
**Root cause:** Suppressing `right_down` prevented Edge from ever seeing `WM_RBUTTONDOWN`, so it could never start a gesture.
**Fix:** Added `GESTURE` state. When move_threshold pixels detected while RIGHT_HELD, transition to GESTURE and call `inject_right_down()` retroactively — Edge now gets its `WM_RBUTTONDOWN` and can start the gesture.

### Hook Dying in Edge
**Symptom:** After using Edge a few times, the mouse hook would silently die.
**Root cause (1):** Unhandled exception in hook proc returned a `ctypes.c_long` object instead of int — Windows killed the hook.
**Root cause (2):** Edge fires 200+ `WM_MOUSEMOVE` per second; routing all through Python caused the 300ms Windows hook callback timeout.
**Fix:** Wrapped hook dispatch in `try/except`; added `wants_moves()` fast-path to skip Python processing for `WM_MOUSEMOVE` when not needed.

### Context Menu After Scroll
**Symptom:** After RMB+scroll, releasing RMB showed the context menu.
**Root cause:** We sent an orphan `right_up` via `inject_right_cleanup()` which `DefWindowProc` interpreted as a context menu trigger.
**Fix:** Removed `inject_right_cleanup()`. Just suppress the `right_up` in SCROLLING state (return non-zero). No synthetic `right_up` needed.

### Spurious Alt+Tab on Idle Right-Click
**Symptom:** A plain right-click sometimes triggered Alt+Tab.
**Root cause:** `_on_right_up()` fell through to the SCROLLING branch when state was IDLE (app started, first right-click before any scroll).
**Fix:** Added explicit guard: `if prev == MapperState.IDLE: return False` at top of `_on_right_up()`.

### Alt+Tab Not Working
**Symptom:** `begin_switch()` sent inputs but Alt+Tab window never appeared.
**Root cause:** Used `KEYEVENTF_EXTENDEDKEY` on `VK_MENU` (Alt key). On some Windows builds this sends Right-Alt instead of Left-Alt, which doesn't trigger Alt+Tab.
**Fix:** Removed `KEYEVENTF_EXTENDEDKEY` from the VK_MENU `SendInput` call.

### ctypes Return Value Error
**Symptom:** `TypeError: return value should be a 'c_long' object` in hook proc.
**Root cause:** Hook proc returned `ctypes.c_long(value)` object — ctypes expected a plain Python int when `restype = ctypes.c_long`.
**Fix:** Return plain `int` values (0 or 1) from hook proc.
