---
id: f011_cursor_click_emoji_cleanup_arch
type: architecture
title: "F-011 Cursor Position, Left Click Z-Order & Emoticon Cleanup Architecture"
tags: [ui, cursor-position, z-order, left-click, no-emoticon, tkinter]
keywords: [panel_window, panel_item_renderer, panel_volume_widget, settings_window, lift, z-order]
status: active
created: 2026-11-11
updated: 2026-11-11
summary: "Architecture fixes for exact cursor positioning, Tkinter overlay z-order lifting, and pure typographic UI."
---

# F-011 Cursor Position, Left Click Z-Order & Emoticon Cleanup Architecture

## Overview
1. **Direct Cursor Positioning**:
   - Replaced vertical centering logic `py - h // 2` with direct cursor placement `(px - 10, py - 10)`.
   - The top-left corner of the floating panel opens right under the cursor, keeping the mouse 10px inside the menu boundary.
   - Bounded by screen dimensions via `min/max` clamp so the window never overflows the right or bottom edges.
2. **Z-Order Stacking (Fixing Left Click)**:
   - Fixed `_tkinter.TclError` caused by invalid `pady=(6, 2)` argument in `tk.Frame` constructor in `panel_item_renderer.py`.
   - Replaced bare `self._win.lift()` with `self._win.lift(self._overlay)` in `panel_window.py`.
   - Guarantees that `self._win` is above the transparent fullscreen `self._overlay`, restoring 100% left-click interactivity on items, sliders, and controls.
3. **Pure Typographic UI (Zero Emoticons)**:
   - Removed all emoji glyphs from `panel_item_renderer.py` and `panel_volume_widget.py`.
   - Cleaned navigation sidebar in `settings_window.py` (removing `⚙`, `⌨`, `◈`, `🖱`, `📖`, `🔑`, `✓`).
   - Cleaned default preset definitions in `config_service.py`.
   - Added regex-based `_strip_emojis` function in `panel_item_renderer.py` to sanitize existing user configurations on render.

## Conformance
- Strict compliance with SYSTEM LOCK:
  - `panel_window.py`: 212 lines (≤ 250)
  - `panel_item_renderer.py`: 146 lines (≤ 250)
  - `panel_volume_widget.py`: 130 lines (≤ 250)
  - `settings_window.py`: 165 lines (≤ 250)
  - `config_service.py`: 202 lines (≤ 250)
  - `welcome_window.py`: 117 lines (≤ 250)
