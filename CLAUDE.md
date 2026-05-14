# RightWheel — Project-Level Agent Rules

> Các quy tắc này **ghi đè** mọi heuristic mặc định của agent.  
> Đọc toàn bộ trước khi thực hiện bất kỳ thay đổi nào.

---

## 🔒 LOCKED BEHAVIORS — KHÔNG ĐƯỢC TỰ Ý THAY ĐỔI

Các behavior dưới đây đã được xác nhận hoạt động đúng ở **v2.10.8**.  
**Mọi thay đổi liên quan phải được user phê duyệt rõ ràng trước khi implement.**

### 1. State Machine — `mouse_mapper_logic.py`

```
_on_right_down  → suppress RMB, lưu vị trí, chuyển sang RIGHT_HELD
_on_move        → nếu vượt threshold → GESTURE, inject retroactive right_down
_on_scroll      → chuyển sang SCROLLING; hướng scroll ĐẦU TIÊN quyết định mode:
                  
                  Scroll ĐẦU TIÊN:
                    UP   + panel → panel.show(), _panel_mode = True
                    DOWN (hoặc không có panel) → hotkey_service.begin_switch(),
                                                  _panel_mode = False
                  
                  Scroll SAU (cùng RMB session):
                    _panel_mode == True  → panel.navigate(±1)
                    _panel_mode == False → hotkey_service.cycle()

_on_right_up    → SCROLLING + _panel_mode: _panel_mode = False, return True (suppress)
                                             Panel Ở LẠI mở — KHÔNG gọi select_current()
                → SCROLLING + Alt+Tab mode: hotkey_service.end_switch(), return True
                → RIGHT_HELD: inject_right_click() (context menu passthrough)
                → GESTURE: return False (let right_up reach app)
                → IDLE guard: return False (spurious event)
```

**Tại sao `_on_right_up` KHÔNG được gọi `panel.select_current()`:**  
Nhả RMB phải để panel ở lại. User chọn item bằng LMB click, phím số 0-9, hoặc Escape.  
Gọi `select_current()` ở đây làm panel đóng ngay khi nhả chuột — đây là behavior sai.

### 2. Dual-Mode Scroll — Quy tắc phân nhánh

```
RMB giữ + scroll UP   → Mở shortcut panel  (panel mode)
RMB giữ + scroll DOWN → Kích hoạt Alt+Tab  (switcher mode)
```

Một RMB session chỉ có MỘT mode. Mode được quyết định bởi hướng scroll **đầu tiên**.  
Các scroll tiếp theo trong cùng session giữ nguyên mode đó.

### 3. Panel UX Flow — Chuỗi tương tác đúng

```
1. Hold RMB + scroll ↑   → panel hiện tại index = 0 (scroll đầu KHÔNG navigate)
2. Tiếp tục scroll ↑/↓ (RMB vẫn giữ) → navigate lên/xuống trong panel
3. Nhả RMB → panel Ở LẠI (không đóng, không select, _panel_mode reset về False)
4. Tương tác sau khi nhả RMB:
   - LMB click item    → select_at(i) → run item, close panel
   - Scroll wheel      → navigate (binding <MouseWheel> trong panel_window)
   - Phím 0-9          → jump to item
   - Escape            → hide panel
   - Click ngoài panel → overlay <ButtonPress> → hide panel
```

### 4. Click-outside Detection — Transparent Overlay

`<FocusOut>` KHÔNG đáng tin cậy trên `overrideredirect(True)` windows trên Windows.  
Giải pháp: tạo một `tk.Toplevel` fullscreen, alpha=0.01, topmost, bind `<ButtonPress>` → `logic.hide()`.  
Panel window được `lift()` lên trên overlay để nhận click đúng cách.

```python
# Trong _do_show():
self._overlay = tk.Toplevel(self._root)
self._overlay.overrideredirect(True)
self._overlay.attributes("-topmost", True)
self._overlay.attributes("-alpha", 0.01)
self._overlay.geometry(f"{sw}x{sh}+0+0")
self._overlay.bind("<ButtonPress>", lambda _: self._logic.hide())
# ... tạo self._win, render, rồi:
self._win.lift()        # map window lên trên overlay trước
self._win.focus_force()
self._position()        # đặt vị trí SAU khi đã map — xem Rule 4b
```

**Luôn destroy overlay trong `_do_hide()`.** Không để overlay tồn tại khi panel đã đóng.  
**KHÔNG bind `<FocusOut>` trên `self._win`** — overlay đã xử lý click-outside; FocusOut gây đóng panel nhầm.

### 4b. Panel Positioning — Thứ tự bắt buộc trong `_do_show()`

```
THỨ TỰ SAI (panel hiện ở góc trên trái):
    _render() → _position() → lift() → focus_force()

THỨ TỰ ĐÚNG:
    _render() → lift() → focus_force() → _position()
```

**Tại sao:** Trên Windows, gọi `lift()` trên `overrideredirect(True)` Toplevel chưa được map sẽ đồng thời map window VÀ reset position về `+0+0` (default position). Nếu `_position()` chạy trước `lift()`, geometry bị overwrite → panel luôn xuất hiện góc trên trái màn hình.  
Fix: gọi `_position()` sau `lift()` + `focus_force()` để geometry được set sau khi window đã được map.

### 5. Focus Management — `panel_logic.select_current()`

```python
# THỨ TỰ BẮT BUỘC — không được đảo:
if hwnd:
    ctypes.windll.user32.SetForegroundWindow(hwnd)  # 1. Restore focus TRƯỚC khi hide
self.hide()                                          # 2. Destroy panel
threading.Timer(0.25, execute_shortcut).start()      # 3. Fire shortcut sau 250ms
```

Gọi `SetForegroundWindow` sau khi panel bị destroy → silently fail, shortcut không chạy.

### 6. tkinter Threading

- **Chỉ một `tk.Tk()`** trong toàn app (trong `panel_window._run()`)
- Mọi dialog/window khác dùng `tk.Toplevel(root)`, KHÔNG tạo `tk.Tk()` mới
- Mọi cleanup sau `destroy()` → dùng `root.after(0, callback)`, KHÔNG gọi đồng bộ
- Giao tiếp hook thread → tkinter thread qua `queue.Queue` + `root.after(30, pump)`

### 7. Hook Proc Invariants

- Luôn kiểm tra `dwExtraInfo == INJECTED_MARKER` đầu tiên → skip synthetic events
- Toàn bộ dispatch trong `try/except` — không để Python exception leak ra C callback
- `wants_moves()` fast-path: chỉ route WM_MOUSEMOVE khi state == RIGHT_HELD

### 8. Hook Watchdog — Auto-Recovery sau Sleep/Wake/Lock

`WH_MOUSE_LL` bị Windows kill silently sau sleep, session lock, hoặc UAC. Không có error, không có callback — hook đơn giản ngừng hoạt động.

Fix (v2.11.0): watchdog daemon post `WM_APP_REHOOK` (0x8001) mỗi 10 giây → `GetMessageW` loop bắt và re-register:

```python
if msg.message == WM_APP_REHOOK:
    if self._hook_id:
        user32.UnhookWindowsHookEx(self._hook_id)
    self._hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, self._proc, None, 0)
```

**KHÔNG xóa `_start_watchdog()` trong `_run()`** — đây là fix cho bug mất hook sau sleep.  
Recovery: tối đa 10 giây sau wake/unlock.

```
❌ Không có watchdog → hook chết sau sleep, app phải restart thủ công
```

---

## ⚠️ FILES CÓ NGƯỠNG SYSTEM LOCK

| File | Lines | Status |
|------|-------|--------|
| `src/features/shortcut_panel/ui/settings_window.py` | ~150 | WARNING (gần 150) |
| `src/features/mouse_mapper/logic/mouse_mapper_logic.py` | ~100 | OK |
| `src/features/shortcut_panel/logic/panel_logic.py` | ~160 | WARNING |

> File vượt 250 dòng → SYSTEM LOCK theo CLAUDE.md global. Chạy `/split-plan` trước.

---

## 📋 QUICK REFERENCE

| Thành phần | File |
|---|---|
| Entry point | `src/main.py` |
| Mouse hook | `src/features/mouse_mapper/services/mouse_hook_service.py` |
| **State machine (LOCKED)** | `src/features/mouse_mapper/logic/mouse_mapper_logic.py` |
| Keystroke injection | `src/features/mouse_mapper/services/hotkey_service.py` |
| **Panel logic (LOCKED)** | `src/features/shortcut_panel/logic/panel_logic.py` |
| **Panel window (LOCKED)** | `src/features/shortcut_panel/ui/panel_window.py` |
| Settings UI | `src/features/shortcut_panel/ui/settings_window.py` |
| Folder editor | `src/features/shortcut_panel/ui/folder_editor_dialog.py` |
| Welcome screen | `src/features/shortcut_panel/ui/welcome_window.py` |
| Config service | `src/features/shortcut_panel/services/config_service.py` |
| i18n engine | `src/features/i18n/__init__.py` |
| Build spec | `RightWheel.spec` |
| Bundled assets | `assets/icon.ico`, `assets/icon.png` |

---

## 🚫 ANTI-PATTERNS ĐÃ TỪNG GÂY BUG

```
❌ Gọi panel.select_current() trong _on_right_up → panel đóng ngay khi nhả RMB
❌ Gọi panel.navigate(delta) ở scroll đầu tiên → (0-1)%n = last item
❌ Gọi SetForegroundWindow sau khi panel đã bị destroy → shortcut không fire
❌ Tạo tk.Tk() thứ hai trong welcome_window → zombie black window
❌ Gọi root.withdraw() đồng bộ ngay sau destroy() → race condition hiện root
❌ KEYEVENTF_EXTENDEDKEY trên VK_MENU → Alt+Tab không hoạt động
❌ begin_switch/cycle/end_switch khi _panel_mode=True → gửi Alt+Tab thay vì navigate panel
❌ Dùng <FocusOut> để detect click-outside trên overrideredirect window → không tin cậy trên Windows
❌ Scroll UP và DOWN đều mở panel → vi phạm dual-mode spec (UP=panel, DOWN=Alt+Tab)
❌ Gọi _position() trước lift() → lift() reset geometry về +0+0, panel xuất hiện góc trên trái
❌ Xóa _start_watchdog() trong mouse_hook_service._run() → hook chết sau sleep, không tự hồi phục
```

---

## 📖 Tài liệu chi tiết

- Architecture: `docs/memory/project/architecture.md`
- Bug history: `docs/memory/project/bug_fixes.md`
- Panel scroll behavior: `docs/memory/project/panel_scroll_behavior.md`
- Changelog: `docs/changelog/CHANGELOG.md`
