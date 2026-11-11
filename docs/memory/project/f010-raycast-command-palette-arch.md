---
id: f010_raycast_command_palette_arch
type: architecture
title: "F-010 Raycast & Linear Command Palette Modern UI Architecture"
tags: [ui, raycast, command_palette, volume, tkinter, modular]
keywords: [panel_window, panel_volume_widget, panel_item_renderer, kbd_badge, inline_volume]
status: active
created: 2026-11-11
updated: 2026-11-11
summary: "Modular architecture for Raycast-style command palette and inline volume widget."
---

# F-010 Raycast & Linear Command Palette Modern UI Architecture

## Overview
Re-architected the RightWheel floating shortcut panel to follow Raycast and Linear Command Palette design aesthetics:
1. **Window Coordinator** (`panel_window.py`):
   - Always-on-top, borderless with 1px `#27272a` boundary, background `#121214`.
   - Width `_W = 264` for balanced typography and breathing room.
   - Manages top-level lifecycle, coordinate positioning, keyboard bindings (0-9, Up, Down, Enter, Esc, BackSpace).
   - Coordinates inline volume widget and item renderer.
   - Shows footer status bar (`◈ Profile • ↑↓ Move • ↵ Open • Esc`).
2. **Inline Volume Slider Widget** (`panel_volume_widget.py`):
   - Directly embedded at the root level of the shortcut panel.
   - Dynamic speaker glyph (`🔇`, `🔈`, `🔉`, `🔊`), title, and real Windows master volume percentage.
   - 216x14px canvas slider track: allows clicking, dragging, and mouse wheeling to adjust system volume smoothly.
   - Clicking on speaker glyph toggles mute.
3. **Item & Kbd Badge Renderer** (`panel_item_renderer.py`):
   - Mechanical keyboard number badges (`kbd` style): `#1e1e24` bg, `#3f3f46` border, `#ffffff` bold text.
   - Type icon and category subtitles (`App`, `Folder`, `Web`, `System`, `Keys`, `Script`).
   - Left accent indicator bar (`#0078d4`) on the selected row.
   - Subtle section divider (`SYSTEM ACTIONS`) separating user shortcuts from utility actions.

## Conformance
- Strict compliance with SYSTEM LOCK:
  - `panel_volume_widget.py`: 136 lines
  - `panel_item_renderer.py`: 150 lines
  - `panel_window.py`: 200 lines
- 100% native Tkinter with zero browser dependencies.
