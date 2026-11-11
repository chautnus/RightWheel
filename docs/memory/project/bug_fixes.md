---
id: proj_bug_fixes_20260430
type: project
title: "MouseHotkey — Critical Bug Fixes & Root Causes"
tags: [bugs, ctypes, hook, alt-tab, context-menu]
keywords: [ghost-right-up, suppress, INJECTED_MARKER, freeze, hook-timeout]
status: active
created: 2026-04-30
updated: 2026-11-11
summary: "Root causes and fixes for all critical bugs found during v1→v2.20 development (including PyInstaller restart DLL, hook hang recovery, self-inflicted keystroke into own window)."
---

## Critical Bugs and Fixes

---

### [v2.15.0] Restart "Failed to load Python DLL" & Gesture/Hook Thread Hang Recovery

**Bối cảnh:** Sau các bản phát hành cử chỉ chuột (F-003, F-004, F-005), người dùng gặp 2 lỗi nghiêm trọng: (1) khi đang sử dụng thì toàn bộ gesture (RMB drag, X1/X2, Shift+Scroll) mất tác dụng vĩnh viễn, và (2) khi bấm Restart ở menu khay để khắc phục thì hiện hộp thoại lỗi `Failed to load Python DLL '...\AppData\Local\Temp\_MEI<PID>\python314.dll'. LoadLibrary: The specified module could not be found.`

**1. Lỗi "Failed to load Python DLL" khi Restart (PyInstaller 6.20.0 env leak)**
- **Symptom:** Bấm "Restart" trên khay hệ thống, RightWheel tắt và báo lỗi không tìm thấy `python314.dll` trong thư mục `_MEIxxxxxx`.
- **Root cause:** 
  - Trong PyInstaller 6.20.0, bootloader dùng `_MEI%d` với PID của tiến trình cha để tạo thư mục tạm.
  - Khi khởi động, bootloader kiểm tra `PYINSTALLER_RESET_ENVIRONMENT` và các biến môi trường `_PYI_*` (`_PYI_APPLICATION_HOME_DIR`, `_PYI_ARCHIVE_FILE`, `_PYI_PARENT_PROCESS_LEVEL`).
  - Code `_restart()` trong `tray_ui.py` trước đây chỉ `pop("_MEIPASS2")` (biến cũ đã bị PyInstaller loại bỏ).
  - Tiến trình mới kế thừa `_PYI_APPLICATION_HOME_DIR` trỏ về `_MEI<PID_cha>`. Bootloader mới ngộ nhận mình là child worker process, bỏ qua việc giải nén mới và gọi `LoadLibrary` vào thư mục tạm của cha. Do tiến trình cha đã `sys.exit(0)`, bootloader cha đã xoá sạch thư mục tạm đó, dẫn đến văng lỗi `LoadLibrary`.
- **Fix:**
  - Trong `tray_ui.py`: xoá toàn bộ biến bắt đầu bằng `_PYI_` và `_MEIPASS2` trong `env`.
  - Thiết lập rõ ràng `env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"`.

**2. Lỗi Gesture, X1/X2, Shift+Scroll tê liệt vĩnh viễn (Same-Process Win32 Hang & Hook Thread Death)**
- **Symptom:** Trong lúc dùng bình thường, đột ngột mọi gesture chuột, phím X1/X2 và cuộn tab Shift+Scroll đều không hoạt động; chuột vật lý vẫn bình thường.
- **Root cause (layered):**
  - **Điểm treo same-process:** `handle_scroll_for_tab_switch()` và `_on_xbutton_down()` đều chạy trực tiếp trên luồng hook cấp thấp `WH_MOUSE_LL` và gọi `window_service.get_hwnd_info(hwnd)`. Hàm này gọi `GetWindowTextW`. Nếu cửa sổ active thuộc chính tiến trình RightWheel (ví dụ: Settings Window, Shortcut Panel, Welcome Window), theo đặc tả Win32, `GetWindowTextW` gửi message `WM_GETTEXT` đồng bộ sang luồng Tkinter. Nếu luồng Tkinter đang bận hoặc vướng GIL, luồng hook bị block hoàn toàn, vượt ngưỡng `LowLevelHooksTimeout` (200ms) khiến Windows âm thầm gỡ bỏ hook hoặc treo luồng.
  - Cả 2 caller trên thực chất chỉ cần `exe` (để kiểm tra trình duyệt Chromium), không hề cần `title` hay `class_name`.
  - **Lỗ hổng watchdog:** Watchdog 10s trong `MouseHookService` chỉ gửi `WM_APP_REHOOK` qua `PostThreadMessageW(self._thread_id, ...)`. Nếu luồng hook đã bị kết thúc (`GetMessageW` loop kết thúc), watchdog gửi vào thread id đã chết và không thể phục hồi hook.
- **Fix:**
  - `window_service.py`: Thêm hàm `get_hwnd_exe(hwnd)` tối ưu, chỉ mở process handle và gọi `QueryFullProcessImageNameW`, hoàn toàn không gọi `GetWindowTextW` hay `GetClassNameW`.
  - `window_service.get_hwnd_info(hwnd)`: Thêm guard kiểm tra `pid == os.getpid()`, bỏ qua `GetWindowTextW` nếu là cửa sổ nội bộ để tránh treo same-process.
  - `mouse_mapper_logic.py` & `tab_switch_logic.py`: Chuyển sang dùng `get_hwnd_exe(hwnd)` thay vì `get_hwnd_info(hwnd)`.
  - `mouse_hook_service.py`: Watchdog kiểm tra `if not self._thread.is_alive():`, nếu luồng đã chết thì giải phóng hook cũ và tự động spawn luồng hook mới.
- **Tham chiếu:** `docs/debug/restart-dll-gesture-dead.debug1.md` và `docs/debug/restart-dll-gesture-dead.debug2.md`.

---

### [v2.10.x] Panel Scroll Regression Series — 3 bugs introduced & fixed

**Bối cảnh:** v2.10.1 thêm `PanelLogic` vào `main.py` với `mapper.panel = panel` nhưng `mouse_mapper_logic._on_scroll` **không bao giờ được cập nhật** để dùng `self.panel`. Bug tồn tại từ v2.10.1 đến v2.10.4 nhưng không ai phát hiện.

**Bug 1 — Scroll gọi Alt+Tab thay vì mở panel (v2.10.1–v2.10.4)**  
`_on_scroll` vẫn gọi `hotkey_service.begin_switch()` → Win11 hiển thị browser recent tabs.  
Fix (commit `3ffbcb8`): Kiểm tra `self.panel` trong `_on_scroll`; nếu có → gọi `panel.show()` và `panel.navigate()`.

**Bug 2 — Scroll UP chọn item cuối thay vì item đầu (introduced tại `3ffbcb8`)**  
`panel.show()` reset index=0. Ngay sau đó `panel.navigate(-1)` được gọi → `(0-1)%n = n-1`.  
Fix (commit `307137e`): Scroll đầu tiên chỉ gọi `panel.show()`, KHÔNG gọi `navigate()`.

**Bug 3 — Panel đóng ngay khi nhả RMB (introduced tại `3ffbcb8`)**  
`_on_right_up` thêm `panel.select_current()` theo analogy với `hotkey_service.end_switch()`. Nhưng Alt+Tab cần release Alt key; panel không giữ phím nào → không cần làm gì, panel phải ở lại.  
Fix (commit `05acf49`): Xóa `panel.select_current()` khỏi `_on_right_up`. Panel ở lại mở, user tương tác bằng LMB/scroll/số/Escape.

**Rule đúc kết:**
- `_on_right_up` khi SCROLLING + panel: **không gọi select_current()**. Chỉ clear `_alt_held`, return True (suppress RMB up).
- Scroll đầu tiên: **chỉ `panel.show()`**, không `navigate()`.
- Xem toàn bộ spec tại `docs/memory/project/panel_scroll_behavior.md`.

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

### Self-Inflicted Keystroke Into Own Window (recurring bug class — seen 2x: `app-hang-suddenly-closes`, `sequence-paste-enter-hang`)
**Symptom:** App hangs/freezes hard (Windows "Application Hang", `AppHangXProcB1`, `Sig[5]=RightWheel.exe`) right after using a feature that fires `SendInput` keystrokes (Shortcut/Sequence execution), specifically when the user had just been interacting with a RightWheel window (Settings, a dialog) immediately before.
**Root cause:** Any code path that calls `SetForegroundWindow(hwnd)` then `SendInput(...)` using a stored `hwnd` (e.g. `PanelLogic._prev_hwnd`, captured via `GetForegroundWindow()` when the panel opened) can end up targeting **RightWheel's own window** if that window was itself foreground at capture time. This brings the app's own UI back to front and then injects the synthetic keystrokes into its own Tkinter interface, causing internal event-loop conflicts severe enough to deadlock the whole process. Two independent debug1→debug2 cycles converged on this exact mechanism from different trigger features.
**Fix pattern:** before any `SetForegroundWindow(hwnd)`/keystroke-injection call that uses a *captured* hwnd (not necessarily user-chosen at that instant), compare its owning PID against `os.getpid()` via `GetWindowThreadProcessId(hwnd, ...)` and skip the self-targeting call entirely if they match:
```python
pid = wt.DWORD(0)
ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
if pid.value != os.getpid():
    ctypes.windll.user32.SetForegroundWindow(hwnd)
```
**How to apply:** this is the SAME guard pattern already used in `window_service.get_hwnd_info()` to skip `GetWindowTextW` for same-process hwnds (see restart-dll-gesture-dead fix). **Any new feature that stores an hwnd and later calls `SetForegroundWindow`/injects input against it must apply this guard** — it is not a one-off fix, it's a required pattern for this codebase. Also don't assume a "safe" fixed delay number from one context (e.g. the 250ms in `ShortcutItem`'s timer) transfers its *reasoning* to a new context without re-verifying — debug2 measured Tkinter `destroy()` at ~1.5ms and disproved the "250ms lets the window finish closing" theory; the real reason for that number is "let the OS release held modifier/physical keys," which is a different justification that happened to still apply.
