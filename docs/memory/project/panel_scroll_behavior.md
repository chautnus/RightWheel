---
id: proj_panel_scroll_behavior_20260513
type: project
title: "Panel Scroll Behavior — Locked UX Contract (v2.10.7)"
tags: [panel, scroll, state-machine, ux, locked]
keywords: [RMB, scroll, navigate, select_current, _on_right_up, _on_scroll, panel.show]
status: active
created: 2026-05-13
updated: 2026-05-13
summary: "Confirmed correct scroll+panel interaction flow locked at v2.10.7. Do not change without explicit user approval."
---

## Locked Behavior: Panel Scroll Interaction (v2.10.7)

Đây là UX contract đã được xác nhận bởi user. Mọi thay đổi phải có phê duyệt rõ ràng.

---

## Chuỗi tương tác đầy đủ

```
1. User nhấn giữ RMB
   → _on_right_down: state = RIGHT_HELD, suppress RMB event

2. User scroll (RMB vẫn giữ) — SCROLL ĐẦU TIÊN
   → _on_scroll: state = RIGHT_HELD → SCROLLING
   → panel: panel.show() — reset index = 0
   → panel: KHÔNG gọi navigate() ở đây
   → _alt_held = True
   → suppress scroll event (return True)

3. User scroll tiếp (RMB vẫn giữ) — CÁC SCROLL SAU
   → _on_scroll: state = SCROLLING (giữ nguyên)
   → panel: panel.navigate(-1) nếu UP, navigate(+1) nếu DOWN
   → suppress scroll event

4. User nhả RMB
   → _on_right_up: prev = SCROLLING
   → _alt_held = True → clear về False
   → panel: KHÔNG gọi select_current() — panel Ở LẠI
   → return True (suppress RMB up, không show context menu)

5. User tương tác với panel (sau khi nhả RMB)
   A. LMB click item   → panel_window <Button-1> → logic.select_at(i)
                       → SetForegroundWindow(prev_hwnd) → hide() → Timer(0.25s, execute)
   B. Scroll wheel     → panel_window <MouseWheel> → logic.navigate(±1)
   C. Phím 0-9         → panel_window key binding → _jump(n) → select_at(n)
   D. Enter            → panel_window <Return> → select_current()
   E. Escape           → panel_window <Escape> → logic.hide()
   F. Click ngoài      → panel_window <FocusOut> → logic.hide()
   G. Hover folder 400ms → _on_hover → logic.select_at(idx) → mở subfolder
```

---

## Tại sao scroll đầu tiên KHÔNG navigate

`panel.show()` reset `_index = 0`. Nếu navigate(-1) được gọi ngay sau:
```
(0 + (-1)) % n = -1 % n = n-1  →  item CUỐI CÙNG được highlight
```
Đây là behavior sai. Fix: scroll đầu tiên chỉ gọi `show()`.

---

## Tại sao `_on_right_up` KHÔNG gọi `panel.select_current()`

Alt+Tab cũ cần `end_switch()` (Alt↑) vì `begin_switch()` đã giữ Alt key.  
Panel không giữ phím nào → không cần release gì.  
Gọi `select_current()` ở đây làm panel đóng ngay khi nhả chuột → sai.

---

## Code tham chiếu (v2.10.7)

**`mouse_mapper_logic._on_scroll`** — file: `src/features/mouse_mapper/logic/mouse_mapper_logic.py`
```python
def _on_scroll(self, direction):
    if self._state not in (MapperState.RIGHT_HELD, MapperState.SCROLLING):
        return False
    self._state = MapperState.SCROLLING
    panel = getattr(self, "panel", None)
    if panel:
        delta = -1 if direction == ScrollDirection.UP else 1
        if not self._alt_held:
            panel.show()        # scroll đầu: chỉ show, index reset = 0
            self._alt_held = True
        else:
            panel.navigate(delta)  # scroll sau: navigate
    else:
        # fallback: hotkey Alt+Tab
        ...
    return True
```

**`mouse_mapper_logic._on_right_up`** — phần xử lý _alt_held:
```python
if self._alt_held:
    panel = getattr(self, "panel", None)
    if not panel:
        hotkey_service.end_switch()  # chỉ với Alt+Tab fallback
    # panel: không làm gì → panel ở lại
    self._alt_held = False
```

---

## Lịch sử bug liên quan

| Commit | Bug | Fix |
|--------|-----|-----|
| `2788c81` | `_on_scroll` gọi `hotkey_service.begin_switch()` thay vì `panel.show()` | — chưa fix, bug tiềm ẩn từ đầu |
| `3ffbcb8` | Fix scroll→panel nhưng thêm `panel.select_current()` vào `_on_right_up` → nhả RMB đóng panel ngay | Introduced |
| `3ffbcb8` | `panel.navigate(delta)` gọi ngay sau `panel.show()` → scroll UP chọn item cuối | Introduced |
| `307137e` | Fix scroll đầu tiên chỉ `show()` | Fixed |
| `05acf49` | Fix bỏ `panel.select_current()` khỏi `_on_right_up` | Fixed |
