# RightWheel — Project-Level Agent Rules

> Các quy tắc này **ghi đè** mọi heuristic mặc định của agent.  
> Đọc toàn bộ trước khi thực hiện bất kỳ thay đổi nào.

---

## 🔒 LOCKED BEHAVIORS — KHÔNG ĐƯỢC TỰ Ý THAY ĐỔI

Các behavior dưới đây đã được xác nhận hoạt động đúng ở v2.10.7.  
**Mọi thay đổi liên quan phải được user phê duyệt rõ ràng trước khi implement.**

### 1. State Machine — `mouse_mapper_logic.py`

```
_on_right_down  → suppress RMB, lưu vị trí, chuyển sang RIGHT_HELD
_on_move        → nếu vượt threshold → GESTURE, inject retroactive right_down
_on_scroll      → chuyển sang SCROLLING
                  + nếu panel: scroll ĐẦU TIÊN chỉ gọi panel.show() (KHÔNG navigate)
                              scroll SAU gọi panel.navigate(delta)
                  + nếu không có panel: hotkey_service.begin_switch / cycle
_on_right_up    → SCROLLING + panel: chỉ clear _alt_held, return True (suppress)
                                      KHÔNG gọi panel.select_current()
                                      Panel ở lại mở
                → SCROLLING + no panel: hotkey_service.end_switch(), return True
                → RIGHT_HELD: inject_right_click() (context menu passthrough)
                → GESTURE: return False (let right_up reach app)
                → IDLE guard: return False (spurious event)
```

**Tại sao `_on_right_up` KHÔNG được gọi `panel.select_current()`:**  
Nhả RMB phải để panel ở lại. User chọn item bằng LMB click, phím số 0-9, hoặc Escape.  
Gọi `select_current()` ở đây làm panel đóng ngay khi nhả chuột — đây là behavior sai.

### 2. Panel UX Flow — Chuỗi tương tác đúng

```
1. Hold RMB + scroll ↑/↓  → panel hiện, index = 0 (không navigate ở scroll đầu)
2. Tiếp tục scroll (RMB vẫn giữ) → navigate lên/xuống
3. Nhả RMB → panel Ở LẠI (không đóng, không select)
4. Tương tác sau khi nhả RMB:
   - LMB click item   → select_at(i) → run item, close panel
   - Scroll wheel     → navigate (binding <MouseWheel> trong panel_window)
   - Phím 0-9         → jump to item
   - Escape           → hide panel
   - Click ngoài      → <FocusOut> → hide panel
```

### 3. Focus Management — `panel_logic.select_current()`

```python
# THỨ TỰ BẮT BUỘC — không được đảo:
if hwnd:
    ctypes.windll.user32.SetForegroundWindow(hwnd)  # 1. Restore focus TRƯỚC khi hide
self.hide()                                          # 2. Destroy panel
threading.Timer(0.25, execute_shortcut).start()      # 3. Fire shortcut sau 250ms
```

Gọi `SetForegroundWindow` sau khi panel bị destroy → silently fail, shortcut không chạy.

### 4. tkinter Threading

- **Chỉ một `tk.Tk()`** trong toàn app (trong `panel_window._run()`)
- Mọi dialog/window khác dùng `tk.Toplevel(root)`, KHÔNG tạo `tk.Tk()` mới
- Mọi cleanup sau `destroy()` → dùng `root.after(0, callback)`, KHÔNG gọi đồng bộ
- Giao tiếp hook thread → tkinter thread qua `queue.Queue` + `root.after(30, pump)`

### 5. Hook Proc Invariants

- Luôn kiểm tra `dwExtraInfo == INJECTED_MARKER` đầu tiên → skip synthetic events
- Toàn bộ dispatch trong `try/except` — không để Python exception leak ra C callback
- `wants_moves()` fast-path: chỉ route WM_MOUSEMOVE khi state == RIGHT_HELD

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
❌ begin_switch/cycle/end_switch với panel đang dùng → gửi Alt+Tab thay vì mở panel
```

---

## 📖 Tài liệu chi tiết

- Architecture: `docs/memory/project/architecture.md`
- Bug history: `docs/memory/project/bug_fixes.md`
- Panel scroll behavior: `docs/memory/project/panel_scroll_behavior.md`
- Changelog: `docs/changelog/CHANGELOG.md`
