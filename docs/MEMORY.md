# RightWheel — Project Memory

last_updated: 2026-11-12 (v2.21.0 — Sequence: Gemini step + Edit existing steps; split clipboard_web_actions.py/sequence_step_dialogs.py)

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

## 🔒 Locked Behaviors (v2.11.0)

Xem `CLAUDE.md` ở project root để biết toàn bộ luật. Tóm tắt:
- `mouse_mapper_logic._on_scroll`: scroll UP → `panel.show()`, scroll DOWN → `hotkey_service.begin_switch()`
- Scroll đầu tiên → chỉ show/begin; scroll sau → `panel.navigate(delta)` hoặc `hotkey_service.cycle()`
- `mouse_mapper_logic._on_right_up` (SCROLLING+panel): KHÔNG gọi `panel.select_current()` — panel ở lại
- Click-outside: transparent overlay `alpha=0.01` + `<ButtonPress>` binding (KHÔNG dùng `<FocusOut>`)
- `panel_logic.select_current()`: `SetForegroundWindow` TRƯỚC `hide()`, Timer 0.25s sau — PHẢI PID-guard trước (bỏ qua nếu hwnd thuộc chính RightWheel, tránh tự bắn phím vào chân mình — xem bug_fixes.md "Self-Inflicted Keystroke")
- Chỉ một `tk.Tk()` trong toàn app

## Quick Reference

- **Entry point:** `src/main.py`
- **Hook:** `src/features/mouse_mapper/services/mouse_hook_service.py` (watchdog auto-respawns dead hook thread, not just rehook)
- **State machine:** `src/features/mouse_mapper/logic/mouse_mapper_logic.py` (LOCKED — X1/X2 rocker gesture removed in F-009, no longer intercepts side buttons)
- **Panel logic:** `src/features/shortcut_panel/logic/panel_logic.py` (6 MenuItem types incl. `SequenceItem`; PID-guards `SetForegroundWindow` against own hwnd)
- **Panel window (Raycast-style, F-010):** `src/features/shortcut_panel/ui/panel_window.py` — state-snapshot diffing in `_do_update()`, full `_render()` only when item list/breadcrumb/profile/paused actually changes; plain selection change calls `PanelItemRenderer.update_selection()` (no destroy/recreate → no flicker)
- **Item renderer:** `src/features/shortcut_panel/ui/panel_item_renderer.py` — keeps `_row_views` widget refs for in-place highlight updates
- **Shortcut executor:** `src/features/shortcut_panel/services/shortcut_executor.py` (198 lines) — `execute()`/`execute_app()`/`execute_url()`/`execute_command()`/`execute_sequence()` (multi-step, per-step try/except + delay); dispatches `"url_clipboard"`/`"gemini"` steps to `clipboard_web_actions.py`
- **Clipboard web actions (F-015):** `src/features/shortcut_panel/services/clipboard_web_actions.py` (65 lines) — `get_clipboard_text()` (raw Win32, no Tkinter dep), `execute_url_clipboard()` (URL-encodes into a `{text}` template), `execute_gemini()` (prompt + clipboard text → `gemini.google.com/app?prompt=`, unofficial Google behavior). Opens URLs itself (`webbrowser.open`) to avoid a circular import with `shortcut_executor.py`.
- **Config service:** `src/features/shortcut_panel/services/config_service.py` (schema v3, `parse_items()`/`items_to_raw()`)
- **Window detection:** `src/features/shortcut_panel/services/window_service.py` (same-process guard on `GetWindowTextW`)
- **Startup toggle:** `src/features/shortcut_panel/services/startup_service.py` (winreg)
- **Settings UI:** `src/features/shortcut_panel/ui/settings_window.py` — tabs: Default (`default_tab.py` + `default_tab_crud.py` mixin), General (`general_tab.py` — startup+language only, Volume removed F-013), Profiles (`profile_editor.py`), Gestures (`gestures_tab.py`), Reference (`reference_tab.py` + `reference_shortcuts_data.py` — searchable shortcut list)
- **Folder editor:** `src/features/shortcut_panel/ui/folder_editor_dialog.py`
- **Sequence editor (F-014/F-015):** `src/features/shortcut_panel/ui/sequence_editor_dialog.py` (211 lines) — builds `SequenceItem.steps` (Keys/App/Web/Script/Web+Clip/Gemini), standalone in-memory buffer; list/button/save orchestration only. Has an **Edit** button + double-click-to-edit (F-015) alongside Add/Delete/▲▼.
- **Sequence step dialogs (F-015):** `src/features/shortcut_panel/ui/sequence_step_dialogs.py` (98 lines) — `ask_<type>(parent, init=None)` per step type (reuses `KeyRecorderDialog`/`_AskDialog`, both support `init` for pre-fill) + `STEP_KINDS` map; shared by Add and Edit so the two flows can't drift apart.
- **Key recorder:** `src/features/shortcut_panel/ui/key_recorder_dialog.py` — click-buttons for Ctrl/Shift/Alt/⊞Win/arrows/Home/End/PgUp/PgDn (avoids Win key being intercepted by Windows when typed physically)
- **Welcome screen:** `src/features/shortcut_panel/ui/welcome_window.py`
- **Config:** `%APPDATA%\RightWheel\shortcuts.json` (schema v3)
- **i18n engine:** `src/features/i18n/__init__.py` — `t(key)`, `init()`, `set_locale()`, 9 locales
- **License:** `src/features/licensing/` — LemonSqueezy API, trial 30d, 7d cache
- **Spec:** `RightWheel.spec` (PyInstaller 6.22.3 — core/hooks-contrib version must stay matched, see antigravity-calibration.md). ⚠ Known leftover: `hiddenimports` still lists `features.shortcut_panel.services.volume_service`, deleted in F-013 — logs a harmless `ERROR: Hidden import ... not found` on every build, not yet cleaned up.
- **GitHub:** https://github.com/chautnus/mousehotkey
- **Portable exe:** `dist/RightWheel.exe` (v2.21.0)
- **App icon:** `assets/icon.ico` + `assets/icon.png` (mouse PNG, multi-size)
- **Removed (F-013):** Volume feature entirely gone — `volume_service.py`/`panel_volume_widget.py`/`volume_overlay.py`/`general_volume_tab.py` all deleted. Volume control is now only reachable via a Sequence's Web(Clip) step or ordinary OS volume keys.
- **CLAUDE.md:** `CLAUDE.md` — project agent rules & locked behaviors
