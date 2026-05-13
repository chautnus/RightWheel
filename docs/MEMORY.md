# RightWheel — Project Memory

last_updated: 2026-05-13 (v2.10.7 — panel scroll behavior locked; app icon; Command feature; 9-lang f8 strings)

## Overview
Windows tray app that maps mouse combos (RMB+scroll) to keyboard hotkeys and a shortcut panel. Python + ctypes WH_MOUSE_LL hook. Feature-Sliced Design.

## Domains

| Domain | Path | Description |
|--------|------|-------------|
| project | [memory/project/](memory/project/INDEX.md) | Architecture decisions, bug fix history |
| prd | [prd/](prd/INDEX.md) | Product requirements v1 and v2 |
| changelog | [changelog/](changelog/INDEX.md) | Version history |
| user | [memory/user/](memory/user/INDEX.md) | User preferences and profile |
| feedback | [memory/feedback/](memory/feedback/INDEX.md) | Collaboration feedback |
| reference | [memory/reference/](memory/reference/INDEX.md) | External resources and URLs |

## 🔒 Locked Behaviors (v2.10.7)

Xem `CLAUDE.md` ở project root để biết toàn bộ luật. Tóm tắt:
- `mouse_mapper_logic._on_scroll`: scroll đầu → `panel.show()` only; scroll sau → `panel.navigate(delta)`
- `mouse_mapper_logic._on_right_up` (SCROLLING+panel): KHÔNG gọi `panel.select_current()` — panel ở lại
- `panel_logic.select_current()`: `SetForegroundWindow` TRƯỚC `hide()`, Timer 0.25s sau
- Chỉ một `tk.Tk()` trong toàn app

## Quick Reference

- **Entry point:** `src/main.py`
- **Hook:** `src/features/mouse_mapper/services/mouse_hook_service.py`
- **State machine:** `src/features/mouse_mapper/logic/mouse_mapper_logic.py`
- **Panel logic:** `src/features/shortcut_panel/logic/panel_logic.py`
- **Config service:** `src/features/shortcut_panel/services/config_service.py` (schema v2)
- **Window detection:** `src/features/shortcut_panel/services/window_service.py`
- **Startup toggle:** `src/features/shortcut_panel/services/startup_service.py` (winreg)
- **Settings UI:** `src/features/shortcut_panel/ui/settings_window.py` ⚠ 250 lines (SYSTEM LOCK boundary)
- **Profile editor:** `src/features/shortcut_panel/ui/profile_editor.py`
- **Folder editor:** `src/features/shortcut_panel/ui/folder_editor_dialog.py`
- **Welcome screen:** `src/features/shortcut_panel/ui/welcome_window.py`
- **Config:** `%APPDATA%\RightWheel\shortcuts.json` (schema v2)
- **i18n engine:** `src/features/i18n/__init__.py` — `t(key)`, `init()`, `set_locale()`, 9 locales
- **License:** `src/features/licensing/` — LemonSqueezy API, trial 30d, 7d cache
- **Spec:** `RightWheel.spec` (supersedes MouseHotkey.spec)
- **GitHub:** https://github.com/chautnus/mousehotkey
- **Portable exe:** `dist/RightWheel.exe` (v2.10.7)
- **App icon:** `assets/icon.ico` + `assets/icon.png` (mouse PNG, multi-size)
- **CLAUDE.md:** `CLAUDE.md` — project agent rules & locked behaviors
