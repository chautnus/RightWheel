---
id: proj_panel_scroll_behavior_20260513
type: project
title: "Panel Scroll Behavior — Locked UX Contract (v2.10.8)"
tags: [panel, scroll, state-machine, ux, locked, dual-mode]
keywords: [RMB, scroll, navigate, select_current, _on_right_up, _on_scroll, panel.show, _panel_mode, overlay]
status: active
created: 2026-05-13
updated: 2026-05-14
summary: "Definitive scroll+panel+Alt+Tab dual-mode spec locked at v2.10.8. Confirmed working and user-approved as of v2.11.0."
---

## Locked Behavior: Panel Scroll Interaction (v2.10.8 → v2.11.0)

Đây là UX contract đã được xác nhận và **yêu thích** bởi user (confirmed v2.11.0).  
Mọi thay đổi phải có phê duyệt rõ ràng.

> "tao thích tính năng giữ chuột phải kéo xuống là mở alt-tab, sau đó vẫn giữ chuột phải, cuộn lên xuống để di chuyển giữa các tab" — user feedback 2026-05-14

---

## Dual-Mode Scroll — Quy tắc cốt lõi

```
RMB giữ + scroll UP   → Mở shortcut panel   (_panel_mode = True)
RMB giữ + scroll DOWN → Kích hoạt Alt+Tab   (_panel_mode = False)
```

Hướng scroll **đầu tiên** trong một RMB session quyết định mode cho toàn bộ session đó.

---

## Chuỗi tương tác đầy đủ

```
1. User nhấn giữ RMB
   → _on_right_down: state = RIGHT_HELD, suppress RMB event

2a. User scroll UP (RMB vẫn giữ) — SCROLL ĐẦU TIÊN
   → _on_scroll: state → SCROLLING
   → panel.show()          — reset index = 0
   → _panel_mode = True
   → _alt_held = True
   → KHÔNG gọi navigate() ở scroll đầu
   → suppress scroll event (return True)

2b. User scroll DOWN (RMB vẫn giữ) — SCROLL ĐẦU TIÊN
   → _on_scroll: state → SCROLLING
   → hotkey_service.begin_switch(forward=True)  — giữ Alt, tap Tab
   → _panel_mode = False
   → _alt_held = True
   → suppress scroll event

3a. Các scroll tiếp theo — PANEL MODE (_panel_mode = True)
   → panel.navigate(-1) nếu UP, navigate(+1) nếu DOWN

3b. Các scroll tiếp theo — ALT+TAB MODE (_panel_mode = False)
   → hotkey_service.cycle(forward)

4. User nhả RMB
   → _on_right_up: prev = SCROLLING
   → _alt_held = True → nhánh:
     Panel mode: _panel_mode = False, panel Ở LẠI, return True
     Alt+Tab:    hotkey_service.end_switch() (nhả Alt), return True
   → _alt_held = False

5. User tương tác với panel (sau khi nhả RMB)
   A. LMB click item     → panel_window <Button-1> → logic.select_at(i)
                         → SetForegroundWindow(prev_hwnd) → hide() → Timer(0.25s, execute)
   B. Scroll wheel       → panel_window <MouseWheel> → logic.navigate(±1)
   C. Phím 0-9           → panel_window key binding → _jump(n) → select_at(n)
   D. Enter              → panel_window <Return> → select_current()
   E. Escape             → panel_window <Escape> → logic.hide()
   F. Click ngoài panel  → overlay <ButtonPress> → logic.hide()
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

Alt+Tab cần `end_switch()` vì `begin_switch()` đã giữ Alt key → phải release.  
Panel không giữ phím nào → không cần release gì.  
Gọi `select_current()` ở đây làm panel đóng ngay khi nhả chuột → sai.

---

## Click-outside: Transparent Overlay (không phải FocusOut)

`<FocusOut>` không đáng tin cậy trên `overrideredirect(True)` windows trên Windows.  
Giải pháp: tạo `tk.Toplevel` fullscreen, `alpha=0.01`, `topmost=True`, bind `<ButtonPress>`.

```python
self._overlay = tk.Toplevel(self._root)
self._overlay.overrideredirect(True)
self._overlay.attributes("-topmost", True)
self._overlay.attributes("-alpha", 0.01)
self._overlay.geometry(f"{sw}x{sh}+0+0")
self._overlay.bind("<ButtonPress>", lambda _: self._logic.hide())
# Panel window được tạo sau, rồi lift() lên trên overlay:
self._win.lift()
```

---

## Code tham chiếu (v2.10.8)

**`mouse_mapper_logic._on_scroll`** — file: `src/features/mouse_mapper/logic/mouse_mapper_logic.py`
```python
def _on_scroll(self, direction):
    if self._state not in (MapperState.RIGHT_HELD, MapperState.SCROLLING):
        return False
    self._state = MapperState.SCROLLING
    panel   = getattr(self, "panel", None)
    forward = (direction == ScrollDirection.DOWN)

    if not self._alt_held:
        if direction == ScrollDirection.UP and panel:
            panel.show()
            self._panel_mode = True
        else:
            if panel and panel.visible:
                panel.hide()
            hotkey_service.begin_switch(forward)
            self._panel_mode = False
        self._alt_held = True
    else:
        if self._panel_mode and panel:
            panel.navigate(-1 if direction == ScrollDirection.UP else 1)
        else:
            hotkey_service.cycle(forward)
    return True
```

**`mouse_mapper_logic._on_right_up`** — phần xử lý _alt_held:
```python
if self._alt_held:
    if self._panel_mode:
        self._panel_mode = False   # panel stays open; user interacts freely
    else:
        hotkey_service.end_switch()
    self._alt_held = False
```

---

## Lịch sử bug liên quan

| Commit | Bug | Fix |
|--------|-----|-----|
| `2788c81` | `_on_scroll` gọi `hotkey_service.begin_switch()` thay vì `panel.show()` | Bug tiềm ẩn từ v2.10.1 |
| `3ffbcb8` | Fix scroll→panel nhưng thêm `panel.select_current()` vào `_on_right_up` → panel đóng ngay | Introduced v2.10.5 |
| `3ffbcb8` | `panel.navigate(delta)` gọi ngay sau `panel.show()` → scroll UP chọn item cuối | Introduced v2.10.5 |
| `307137e` | Fix scroll đầu tiên chỉ `show()` | Fixed v2.10.6 |
| `05acf49` | Fix bỏ `panel.select_current()` khỏi `_on_right_up` | Fixed v2.10.7 |
| `—` | Scroll DOWN cũng chỉ mở panel, không Alt+Tab; `<FocusOut>` click-outside không hoạt động | Fixed v2.10.8 |
