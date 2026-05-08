---
id: prd_mousehotkey_v2_20260430
type: prd
title: "MouseHotkey v2 — Product Requirements"
tags: [prd, v2, shortcut-panel, alt-tab, gesture]
keywords: [RMB, scroll, panel, folder, settings, tray]
status: active
created: 2026-04-30
updated: 2026-04-30
summary: "Full product requirements for MouseHotkey v2 with shortcut panel and Alt+Tab switcher."
---

## Product: MouseHotkey v2

### Goals
Allow power users to trigger keyboard shortcuts and switch windows using only the mouse (right-click + scroll), without lifting their hand to the keyboard.

### User Stories

#### Core Mouse Combos
- **RMB + scroll down:** Cycle Alt+Tab forward (hold Alt across scrolls; release on RMB release)
- **RMB + scroll up:** Open shortcut panel
- **RMB + drag (≥8px):** Pass through to OS/Edge as a native gesture (retroactive right_down injection)
- **RMB tap (no scroll/drag):** Normal right-click context menu

#### Shortcut Panel
- Appears near cursor as a dark, narrow floating window
- Items numbered 0–9; press number key to activate
- Scroll up/down to navigate highlighted item; Enter to activate
- Items: shortcuts (label + key combo) and folders (2-level max)
- Folder: opens sub-list; Esc or back button to return
- Panel stays open after RMB released
- Dismissed by: clicking outside, pressing Esc, or executing a shortcut
- Max 10 items per level

#### Settings UI
- Accessible via system tray → Settings…
- Add shortcut (label + key string e.g. `ctrl+shift+v`)
- Add folder (label only; children managed separately — currently top-level only)
- Edit and delete items
- Reorder with Up/Down buttons
- Double-click to edit
- Save & Close persists to JSON and reloads panel

#### System Tray
- Green dot icon = enabled, red = disabled
- Toggle enable/disable via tray menu
- Exit cleanly (stops hook thread)

### Acceptance Criteria
- [x] RMB+scroll-down triggers Alt+Tab without context menu
- [x] RMB+drag does not break Edge swipe gestures
- [x] RMB+scroll-up shows shortcut panel
- [x] Number keys 0–9 activate items from panel
- [x] Scroll navigates panel while visible
- [x] Folder navigation works (enter + back)
- [x] Settings persists to `%APPDATA%\MouseHotkey\shortcuts.json`
- [x] Tray icon reflects enabled state
- [x] App packaged as portable exe (PyInstaller --onefile)

### Out of Scope (v2)
- Multi-level folders (>2 levels)
- Scroll-left/right combos
- Custom icon themes
- Auto-update mechanism
