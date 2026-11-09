---
id: changelog_20260430
type: changelog
title: "MouseHotkey Changelog"
tags: [changelog, versions]
keywords: [v1, v2, releases, fixes]
status: active
created: 2026-04-30
updated: 2026-11-09
summary: "Version history for RightWheel from v1.0.0 to v2.15.0."
---

# Changelog

All notable changes to RightWheel are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.15.0] — 2026-11-09

### Fixed
- **PyInstaller Restart DLL load & low-level hook thread hang recovery** — fixed 2 critical reliability issues causing "Failed to load Python DLL" dialog on Restart and permanent freeze of gestures/X1/X2/Shift+Scroll:
  1. **"Failed to load Python DLL" on Restart (tray menu)** — `tray_ui._restart()` previously only stripped legacy `_MEIPASS2`. In PyInstaller 6.20.0, the bootloader relies on `_PYI_*` environment variables (`_PYI_APPLICATION_HOME_DIR`, `_PYI_ARCHIVE_FILE`, `_PYI_PARENT_PROCESS_LEVEL`). When restarting, the newly spawned process inherited `_PYI_APPLICATION_HOME_DIR` pointing to the previous instance's temp folder (`%TEMP%\_MEI<PID>`). The new bootloader mistook itself for a child worker process, skipped fresh extraction, and attempted to call `LoadLibrary` on `python314.dll` from the temp folder that the exiting parent process had already deleted. Fixed by popping all `_PYI_*` keys and `_MEIPASS2` from `os.environ` before spawning, and explicitly setting `PYINSTALLER_RESET_ENVIRONMENT = "1"`.
  2. **Gestures, X1/X2, and Shift+Scroll permanently dead during usage** — root cause identified across two compounding issues:
     - `get_hwnd_info()` synchronously called Win32 `GetWindowTextW` and `GetClassNameW` inside the `WH_MOUSE_LL` hook thread on every Shift+Scroll and X1/X2 event. When the active foreground window belongs to RightWheel itself (same-process Tkinter UI), `GetWindowTextW` sends a synchronous `WM_GETTEXT` message which hangs/deadlocks if Tkinter is busy or waiting on GIL, exceeding `LowLevelHooksTimeout` (200ms) and causing Windows to silently unhook or freeze the hook thread. Fixed by introducing lightweight `get_hwnd_exe(hwnd)` that queries only the process image name via kernel handle without touching window text/class, guarding `get_hwnd_info()` to skip `GetWindowTextW` if `pid == os.getpid()`, and using `get_hwnd_exe()` in `tab_switch_logic` and `mouse_mapper_logic`.
     - `MouseHookService` watchdog previously only posted `WM_APP_REHOOK` to the hook thread ID, but could not recover if the hook thread terminated (`GetMessageW` loop exited). Upgraded watchdog to check `if not self._thread.is_alive():` and cleanly spawn a new hook thread.
- Root-caused via `docs/debug/restart-dll-gesture-dead.debug1.md` + `.debug2.md` (verdict: both reports contributed — debug1 identified PyInstaller env leak & hook call latency; debug2 proved PID-based temp dir mechanism, pinpointed same-process `GetWindowTextW` deadlock, and verified watchdog thread-death gap).

### Added
- **Windows shortcut reference tab (F-006)** — new "Reference" tab in Settings listing 20+ common Windows and RightWheel shortcuts (`Win+D`, `Win+E`, `Win+Shift+S`, `Alt+Tab`, the app's own RMB gestures, etc.) with English descriptions, as a read-only `ttk.Treeview` lookup — no wiring to the shortcut-add form, just a cheatsheet. (Note: `Win+<letter>` combos already worked before this — `shortcut_executor.py`'s key map already had `"win"` and a-z mapped; this tab just documents what's available.)
- **Volume control via scroll (F-006)** — a new `show_volume_slider` action for the shortcut panel (same pattern as `open_settings`/`toggle_pause`) opens a small HUD at the cursor position; scrolling while it's shown sends `VK_VOLUME_UP`/`VK_VOLUME_DOWN` (0xAF/0xAE) via `SendInput` per tick, no `pycaw`/Core Audio dependency added. The slider starts at a neutral 50% (relative delta only, since media-key injection can't read the OS's actual volume %) and auto-dismisses after 3s idle, on `Escape`, or on an outside click. Built as a fully independent module (`volume_overlay.py`) reusing the existing transparent-backdrop overlay pattern from `PanelWindow` — unlike `TrailOverlay` (which must avoid stealing focus with `WS_EX_NOACTIVATE`), this overlay needs real focus to receive scroll/`Escape`, and is positioned via Tkinter's own `winfo_pointerx()`/`winfo_pointery()` rather than a Win32 `GetCursorPos` call. Does not touch `mouse_mapper`/the gesture engine at all.



### Fixed
- **Mouse gesture engine, reliability (F-005)** — 5 bugs found via hands-on testing of F-004's `.exe` build, none of which were caught by automated verify-cmd (all are OS-level behaviors: window focus, modal menu loops, process lifecycle):
  1. **Rocker-gesture (X1/X2) worked once per session, then went dead** — root cause: `_on_xbutton_down()` never recorded that X1/X2 had been used, so releasing RMB afterward fell into the plain "short tap" branch and called `inject_right_click()`, popping a real Chromium context menu. That menu enters a modal loop that swallows every subsequent mouse event (further X1/X2 presses, plain right-clicks) until the user dismisses it by hand — this, not focus-stealing, was the actual cause of "only works the first time." Fixed with a `_xbutton_used` flag: set when X1/X2 successfully switches a tab, reset on the next `right_down`, and checked on `right_up` to skip `inject_right_click()` entirely when set.
  2. **Trail overlay stole focus from the browser** — the fullscreen transparent `Toplevel` never had `WS_EX_NOACTIVATE` set, so Windows made it the foreground window the moment it appeared and didn't hand focus back to Chromium when it closed; `SendInput`/`GetForegroundWindow()`-dependent calls (X1/X2, gesture shortcuts) that ran afterward could misfire. Fixed by OR-ing `WS_EX_NOACTIVATE | WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOOLWINDOW` onto the window's extended style via `SetWindowLongPtrW` — note the real top-level HWND on Windows Tkinter is `GetParent(widget.winfo_id())`, not `winfo_id()` itself.
  3. **Trail line opened with a stray straight segment** — the first point was anchored to the RMB-down coordinate, but Tkinter takes ~20-50ms to construct the overlay window, during which the real cursor had already moved; the first `_poll()` tick then drew a chord from the stale down-position to the now-distant cursor. Fixed by sampling `GetCursorPos()` fresh right after the canvas is ready, instead of reusing the down-event coordinates.
  4. **Plain right-clicks occasionally ate the context menu** — `main.py` hardcoded `move_threshold=8`, overriding the project's own `50`px tremor-tolerance default (set a while back for exactly this reason). Combined with F-004's Silent Drop (an unmatched gesture now sends nothing at all), any natural hand tremor above 8px during a normal right-click got misread as a failed gesture and swallowed the context menu. Fixed by dropping the override and letting `MouseMapperLogic()` use its real default.
  5. **Restart (tray menu) intermittently showed "Failed to remove temporary folder"** — `os.execve` on Windows doesn't replace the process atomically like POSIX; it spawns a new one while the old one's DLL handles inside PyInstaller's onefile `%TEMP%\_MEIxxxxxx` extraction dir are still closing, racing the bootloader's own cleanup. Replaced with a detached `subprocess.Popen` (`shell=True`, `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`) that waits ~1s (`ping -n 2`, not `timeout` — the latter errors out with no console to redirect from) before relaunching, then `sys.exit(0)`s cleanly so the old process's bootloader can finish deleting its temp folder.
- Root-caused via `docs/debug/gesture-trail-x1x2-flaky.debug1.md` + `.debug2.md` (verdict: both reports' findings contributed — debug2's independent pass caught the X1/X2 root cause debug1 had missed).



### Fixed
- **Mouse gesture engine (F-004)** — F-003's gesture-to-shortcut feature didn't actually work in practice; fixed 3 compounding bugs found via `docs/debug/gesture-no-trigger.debug1.md`/`.debug2.md`:
  1. **UX**: double-clicking a row in the gesture list silently toggled it off (`enabled: false`), saved immediately — removed the `<Double-Button-1>` binding; the preset's own `enabled` state is now also auto-restored to `true` on load if it was left `false` by this bug.
  2. **Algorithm**: `GestureRecognizer` quantized a spurious diagonal segment (e.g. `"DR"`) at the corner between two cardinal strokes — reproducible on >60% of perfectly square 90° drags, not just human hand-curve (Anchor Residual Vector Addition). Added `normalize_directions()`, a pure function that collapses `[A, diag(A,B), B]` → `[A, B]` for the 8 orthogonal pairs while leaving intentional diagonal presets (e.g. `["DR"]`) untouched.
  3. **Context menu leak**: the "reverse cancellation" mechanism added in F-003 (`inject_right_down()` early + `inject_right_up()` on match) formed a complete right-click pair at the OS level, triggering a real `WM_CONTEXTMENU` that ate the `Ctrl+W` keystroke right after it — exactly the class of bug this project removed once before (v2.0.0, `inject_right_cleanup()`). Fixed by removing `inject_right_down()`/`inject_right_up()` from the `GESTURE` path entirely: a matched gesture executes its shortcut directly with no synthetic click at all, and an unmatched gesture is now a **Silent Drop** (nothing sent, right_up fully suppressed) instead of falling back to Edge/extension passthrough.
- **Trade-off accepted**: removing the early `inject_right_down()` means RightWheel no longer passes through *any* application's native right-drag gesture (not just Edge's — also Explorer drag-drop, canvas pan/rotate in image/CAD tools, etc.) once a drag crosses the gesture threshold (8px) while RMB is held. User confirmed not relying on that behavior.

### Added
- **Gesture trail overlay** — while drawing a gesture (RMB held + moved past threshold), a thin cyan line now follows the cursor on a transparent always-on-top overlay (`trail_overlay.py`, polls `GetCursorPos` at ~60fps, closes instantly on release — no fade).
- Gesture presets are now managed from a **4th tab ("Gestures") inside the main Settings window** instead of a separate tray-launched dialog — `gesture_settings_dialog.py` removed, tray no longer has a standalone "Cử chỉ chuột" entry.

## [2.14.0] — 2026-11-08

### Added
- **Mouse-only tab switch + gesture engine (F-003)** — two new mouse-only ways to control browser tabs while holding RMB, no keyboard needed:
  1. **X1/X2 tab switch**: press the side mouse button (X1=Back, X2=Forward) while holding RMB on a Chromium window to switch to the previous/next tab. New `WM_XBUTTONDOWN` handling in `mouse_hook_service.py`; new `hotkey_service.switch_tab_x1x2(forward)` (self-contained, does not depend on a physically-held Shift — unlike `switch_tab()` used by F-001). X1/X2 is suppressed for ANY foreground app while RMB is held (not just Chromium), reserved for future RMB+X1/X2 combos; released normally when RMB is not held.
  2. **8-direction mouse gesture → shortcut**: drawing a directional stroke sequence (U/D/L/R + 4 diagonals) while holding RMB executes a configurable shortcut (default: Down→Right = `Ctrl+W`, closes the tab). New `GestureRecognizer` module (`gesture_recognizer.py`, streaming O(1)/point, 15-18px stroke threshold, consecutive-direction dedup). Gestures that don't match any preset fall back to the existing Edge/extension passthrough unchanged.
  3. New `GestureSettingsDialog` (own file, opened from the tray menu) to add/edit/enable/disable gesture presets — kept out of `settings_window.py`, which stays at 149 lines.
  4. `shortcuts.json` schema bumped to `version: 3` with a new `"gestures"` list; migration from v1/v2 is automatic and additive (`default`/`profiles` untouched).
- **Bug fix found during design**: `MouseMapperLogic.wants_moves()` was only returning `True` for `RIGHT_HELD`, so move events stopped reaching the logic once a drag crossed into the `GESTURE` state — harmless before (GESTURE only re-injected `right_down` once), but would have silently broken gesture recognition. Fixed to include `GESTURE`.
- **Reverse-cancellation for RMB drag**: new `hotkey_service.inject_right_up()` (tagged `INJECTED_MARKER`), called only when a gesture matches a preset in the `GESTURE` state, to cleanly close out the `right_down` that was retroactively injected earlier for Edge/extension tracking. Deliberately scoped to the `GESTURE`+matched case only — the project previously removed an `inject_right_cleanup()` call (v2.0.0) because an orphaned synthetic `right_up` caused a spurious context menu; this one is narrower and was manually verified not to touch the `SCROLLING`/`RIGHT_HELD` paths.
- See `docs/adr/ADR-002-gesture-engine-architecture.md` for the architecture decision (GestureRecognizer as an independent module vs. embedding in the state machine).

## [2.13.0] — 2026-11-01

### Added
- **Restart button in tray menu (F-002)** — new "Restart" menu item next to Exit. Calls `icon.stop()` then `os.execv(sys.executable, [sys.executable] + sys.argv)` to relaunch the whole process in place, as a quick workaround when the gesture stops responding for unknown reasons (not covered by the existing sleep/wake/lock watchdog). Works both running from source and from the frozen PyInstaller exe. Localized `tray.restart` key added to all 9 locales.

## [2.12.0] — 2026-10-30

### Added
- **Shift+Scroll browser tab switch (F-001)** — hold Shift + scroll wheel to switch tabs in Chrome/Edge/Chromium-based browsers (Brave, Opera, Vivaldi). Scroll UP = next tab (Ctrl+Tab), DOWN = previous tab (Ctrl+Shift+Tab). Gated to the active foreground window being a known Chromium exe.
- Implementation: no new OS hook added. `GetAsyncKeyState(VK_SHIFT)` is polled directly inside the existing `WM_MOUSEWHEEL` branch of `mouse_hook_service.py` via a new optional `on_scroll_modifier` callback (default `None`, backward compatible). `hotkey_service.switch_tab(forward)` sends Ctrl+Tab/Ctrl+Shift+Tab using the blind-release-modifier technique (inject a `KEYEVENTF_KEYUP` for Shift right before Ctrl+Tab, only for the `forward` direction) instead of suppressing the real Shift key continuously — avoids breaking Shift+Click, uppercase typing, and Shift+Tab in forms. See `docs/adr/ADR-001-poll-shift-blind-release.md`.
- New module `src/features/mouse_mapper/logic/tab_switch_logic.py` (pure gate/direction helpers + orchestrator).

## [2.11.0] — 2026-05-14

### Fixed
- **Hook dies after sleep/wake/lock — app stops responding** — `WH_MOUSE_LL` is silently killed by Windows after sleep, session lock, or UAC prompt. No recovery mechanism existed; app had to be restarted.
- Fix: watchdog daemon thread posts `WM_APP_REHOOK` (0x8001) to the hook thread every 10 seconds. The `GetMessageW` loop intercepts this message, calls `UnhookWindowsHookEx` on the stale handle, and calls `SetWindowsHookExW` to re-register. Recovery guaranteed within 10 s of any such event.

### Added
- `MIT LICENSE` file — GitHub now detects and displays the license badge.

### Changed (website / SEO)
- `og-image.png` → `og-image.jpg` (969 KB → 102 KB, −90%)
- Added real screenshots (`RightWheel Screen 1.png`, `Screen 2.png`) with descriptive `alt` text — enables Google Images indexing.
- Fixed meta description truncation (175 → 158 chars).
- Added `og:locale`, fixed `twitter:description` length, `rel=sitemap` now absolute URL.
- Fixed CTA H2 to be keyword-bearing: "Try RightWheel — Mouse Shortcuts for Windows."
- Added Google Analytics 4 (`G-XC45ZRJ7Y9`).
- Removed conflicting `jekyll-gh-pages.yml` workflow — `deploy-pages.yml` is now the sole Pages deployer; `sitemap.xml`, `robots.txt`, `og-image` all return 200.

---

## [2.10.9] — 2026-05-13

### Fixed
- **Panel appears at top-left instead of cursor position** — `_position()` was called before `lift()`. On Windows, `lift()` maps an `overrideredirect` Toplevel and resets its geometry to `+0+0`. Fix: call `lift()` + `focus_force()` first, then `_position()`.
- Removed `<FocusOut>` binding on panel window — it conflicted with the overlay click-outside handler and caused spurious closes.

### Locked (CLAUDE.md Rule 4b)
- `_do_show()` ordering: `_render()` → `lift()` → `focus_force()` → `_position()`. Any other order breaks panel positioning on Windows.

---

## [2.10.8] — 2026-05-13

### Changed
- **Dual-mode scroll**: RMB+scroll direction now determines session mode.
  - Scroll **UP** → open shortcut panel (`_panel_mode = True`)
  - Scroll **DOWN** → activate Alt+Tab window switcher (`_panel_mode = False`)
  - Subsequent scrolls in the same RMB session stay in chosen mode.
- **Click-outside via transparent overlay**: replaced unreliable `<FocusOut>` with a fullscreen `alpha=0.01` `tk.Toplevel` overlay. Any `<ButtonPress>` outside the panel fires `logic.hide()`. Panel is `lift()`ed above overlay to receive clicks correctly.
- `_panel_mode: bool` flag added to `MouseMapperLogic.__init__` (reset to `False` on each `_on_right_up`).
- `panel_window.py`: `_overlay: tk.Toplevel | None` added; destroyed in `_do_hide()`.

### Fixed
- Scroll DOWN no longer opens panel (regression since v2.10.5 where both directions triggered `panel.show()`).
- `<FocusOut>` was silently failing on `overrideredirect(True)` windows → click outside did nothing.

---

## [2.10.7] — 2026-05-13

### Fixed
- **Panel stays open after releasing RMB** — restored v2.9.x behavior. Releasing right mouse button no longer calls `panel.select_current()`. Panel remains open; user interacts via LMB click, scroll wheel, number keys 0-9, Escape, or click-outside.
- Root cause: `_on_right_up` erroneously called `panel.select_current()` (introduced in 2.10.5 by analogy with `hotkey_service.end_switch()`).

---

## [2.10.6] — 2026-05-13

### Fixed
- **First scroll opens panel at index 0** — navigate(-1) was called immediately after `panel.show()` causing `(0-1)%n = last item`. First scroll now only calls `show()`.
- Welcome screen now shows mouse PNG icon (PIL/ImageTk) instead of 🖱 emoji; fallback to emoji if PIL unavailable.

### Changed
- `RightWheel.spec` bundles `assets/icon.png` into frozen exe.

---

## [2.10.5] — 2026-05-13

### Fixed
- **Scroll now opens shortcut panel** instead of Alt+Tab (Windows task switcher). `_on_scroll` in `mouse_mapper_logic` was always calling `hotkey_service.begin_switch()` — the `mapper.panel` reference set in `main.py` was dead code since v2.10.1.

---

## [2.10.4] — 2026-05-13

### Added
- **App icon** — mouse PNG (dark gray + orange) converted to multi-size ICO (`assets/icon.ico`), applied to exe via `RightWheel.spec`.
- **Run Commands row in welcome screen** — `_FEATURE_KEYS` f8 added to `welcome_window.py` and all 9 i18n files (en, vi, zh, fr, es, pt, th, id, it).

---

## [2.10.2] — 2026-05-13

### Added
- **Command shortcut type in folder editor** — Add/edit shell commands inside folder submenus via `FolderEditorDialog`.

---

## [2.10.1] — 2026-05-13 (was v2.10.0 bump)

### Added
- **Hover-to-open folders** — hover cursor over a folder item for 400 ms → auto-opens subfolder (no click needed). Uses `<Enter>`/`<Leave>` bindings + `win.after(400, ...)`.

---

## [2.9.0] — 2026-05-08

### Added
- Full i18n system — 9 languages (EN, VI, ZH, FR, ES, PT, TH, ID, IT) via `features/i18n/` with dynamic locale loading
- Renamed app: MouseHotkey → **RightWheel**; new exe `RightWheel.exe`
- LemonSqueezy license system — 30-day trial, $5.99 perpetual license, 7-day cache
- Language selector dropdown in Settings footer
- GitHub Pages website at `chautnus.github.io/RightWheel`

---

## [2.5.0] — 2026-05-07

### Added
- **Welcome / onboarding screen** (`welcome_window.py`) — hiển thị lần đầu chạy app, không hiện lại
  - Thiết kế hai tông màu: top nhạt (`#f5f5f5`) + body tối (`#141414`)
  - Feature list: icon trắng, trigger text xanh, mô tả xám
  - Checkbox "Run on startup"; nút "Get Started" → lưu `"welcomed": true` vào config
- **Windows startup toggle** (`startup_service.py`) — winreg `HKCU\...\Run\MouseHotkey`
  - `enable()`, `disable()`, `is_enabled()` — chỉ hoạt động khi chạy từ exe (PyInstaller frozen)
  - Toggle xuất hiện ở cả Welcome screen và footer của Settings
- **`folder_editor_dialog.py`** — modal riêng để edit shortcut bên trong folder
  - Full CRUD: Add, Edit, Delete, Up, Down; reuses `_AskDialog` từ settings_window
- Settings footer: startup checkbox + "💾 Save & Close" cạnh nhau (không còn button riêng lẻ)

### Fixed
- **Black window sau Save & Close (nguyên nhân 1):** `welcome_window.py` tạo `tk.Tk()` riêng → hai Tk instances xung đột → zombie window. Fix: welcome dùng `Toplevel(root)` trên cùng root của panel.
- **Black window vẫn còn (nguyên nhân 2):** `destroy()` post focus-transfer events vào queue; `root.withdraw()` đồng bộ chạy trước khi events đó được xử lý → root hiện ra sau withdraw. Fix: `root.after(0, root.withdraw)` — defer đến sau khi event queue flush.
- **Tab text xám trên nền trắng:** Windows ttk theme "vista"/"xpnative" override custom colors của Notebook. Fix: `style.theme_use("clam")`.
- **Folder shortcut editing không hoạt động:** `_edit()` chỉ rename label folder, không mở children. Fix: route folder clicks sang `FolderEditorDialog`.
- **Double emoji trên folder items:** label lưu là `"📁 Name"` nhưng `_refresh()` thêm `📁` nữa. Fix: bỏ prefix khỏi format string trong `_refresh()`.
- **Welcome button bị co nhỏ:** hardcode 460px block `fill="x"`. Fix: auto-size từ `winfo_reqwidth/reqheight`; button dùng `fill="x"` + `ipady=10`.
- **Welcome icons không thấy / header không đọc được:** icons → `fg="white"`; header "MouseHotkey" → `fg="#111111"` trên `bg="#f5f5f5"`.

### Changed
- `welcome_window.py`: standalone `tk.Tk()` → `tk.Toplevel(root)`, gọi từ `panel_window._run()` sau `root.withdraw()`
- `settings_window.py`: `ttk.Notebook` với "Default" + "Profiles" tab; `style.theme_use("clam")`; VERSION = "2.5.0"
- `main.py`: bỏ import welcome_window (đã chuyển vào panel_window._run)

### Build
- `dist/MouseHotkey.exe` v2.5.0 (07/05/2026)

---

## [2.4.0] — 2026-05-07

### Added
- **Context-aware profiles** — bộ shortcut khác nhau theo app đang active
  - `window_service.py` (NEW): ctypes-only — `GetWindowTextW`, `GetClassNameW`, `QueryFullProcessImageNameW`; không dùng psutil
  - `config_service.py` viết lại: schema v2, `resolve_profile()`, AND-logic `_matches()`, auto-migration v1→v2
  - `profile_editor.py` (NEW): `ProfileEditor(tk.Frame)` — left list panel + right detail panel; full CRUD match rules + shortcuts
  - `panel_logic.py`: wired window detection + profile resolution vào `show()`; property `active_profile`
- Schema v2: `{ "version": 2, "default": [...], "profiles": [{name, match:[{by, value}], shortcuts:[...]}] }`
- v1 → v2 migration tự động trong `config_service.load()` (rename `"shortcuts"` → `"default"`, thêm `"profiles": []`)
- Match rule types: `exe` (basename, case-insensitive), `title_contains`, `class_name` (exact)
- Panel: blue badge "◈ ProfileName" khi active profile không phải Default

### Changed
- Config key `"shortcuts"` → `"default"` (breaking change, mitigated by auto-migration)
- `types/panel_types.py`: added `MatchRule` và `Profile` dataclasses

### Build
- `dist/MouseHotkey.exe` v2.4.0 (07/05/2026, intermediate build)

---

## [2.2.0] — 2026-05-07

### Added
- Version hiển thị trong Settings window (góc trên phải: `v2.2.0`)
- Hằng số `VERSION` trong `settings_window.py`

### Fixed
- **Shortcut không thực thi** — root cause: `SetForegroundWindow` bị Windows reject silently khi gọi từ background timer thread (process không còn là foreground sau khi panel bị destroy)
- Fix: gọi `SetForegroundWindow(prev_hwnd)` trong `select_current()` TRƯỚC `hide()`, trên tkinter thread, trong khi panel vẫn focused → Windows chấp nhận → focus về đúng cửa sổ đích
- Tăng delay trước `SendInput` từ 150ms → 250ms để đảm bảo focus transition hoàn tất

### Changed
- `panel_logic.py`: loại bỏ `_fire()` method; logic focus restore giờ nằm inline trong `select_current()`
- `settings_window.py`: title bar và header đều hiển thị version

### Build
- `dist/MouseHotkey.exe` ~30 MB (07/05/2026)

---

## [2.1.0] — 2026-05-06

### Added
- `_KeyRecorder` dialog trong `settings_window.py`: user nhấn phím thật thay vì gõ text để ghi shortcut
- Real-time preview tổ hợp phím trong dialog (e.g. `ctrl+shift+v`)
- Hỗ trợ modifier: Ctrl, Shift, Alt, Win (cả Left/Right variant)

### Fixed
- `MouseHotkey.spec`: tkinter bị exclude trong spec cũ → exe crash với `ModuleNotFoundError: No module named 'tkinter'`
  - Xóa `tkinter` khỏi `excludes`; thêm `tkinter`, `tkinter.simpledialog`, `_tkinter` vào `hiddenimports`

### Build
- `dist/MouseHotkey.exe` ~30 MB (Python 3.14.3 / PyInstaller 6.20.0)

---

## [2.0.0] — 2026-04-30

### Added
- Shortcut panel: frameless dark floating window triggered by RMB+scroll-up
- Panel navigation: scroll up/down, number keys 0–9, Enter to activate
- Folder support in panel: 2-level hierarchy, Esc to go back
- Settings window: add/edit/delete/reorder shortcuts and folders (tkinter Listbox CRUD)
- Config persistence: `%APPDATA%\MouseHotkey\shortcuts.json`
- `on_settings` callback wired from tray → settings window open
- Feature-Sliced Design architecture: mouse_mapper + shortcut_panel features
- `PanelLogic` callbacks: `on_show`, `on_hide`, `on_update`
- `shortcut_executor.py`: VK_MAP + SendInput key sequence

### Changed
- Refactored from single-file v1 to multi-module Feature-Sliced structure
- `MouseMapperLogic` now holds optional `panel: PanelLogic` reference (injected in main.py)
- Scroll-up: opens panel (was no-op in v1)
- Scroll-down: Alt+Tab cycle (unchanged behavior, cleaner implementation)

### Fixed
- Mouse freeze: suppress both right_down AND right_up; re-inject synthetic right_click on tap
- Edge gesture broken: added GESTURE state with retroactive `inject_right_down()`
- Hook dying in Edge: try/except guard + `wants_moves()` fast-path for WM_MOUSEMOVE
- Context menu after scroll: removed orphan `inject_right_cleanup()` call
- Spurious Alt+Tab: added `if prev == IDLE: return False` guard in `_on_right_up()`
- Alt+Tab not working: removed `KEYEVENTF_EXTENDEDKEY` from VK_MENU SendInput

---

## [1.0.0] — 2026-04-29

### Added
- WH_MOUSE_LL ctypes global mouse hook (Windows-only)
- RMB+scroll-down → Alt+Tab (begin/cycle/end pattern)
- RMB+drag passthrough for Edge gestures (GESTURE state)
- INJECTED_MARKER (0xFEED1234) on dwExtraInfo to skip synthetic events
- `wants_moves()` fast-path to skip WM_MOUSEMOVE when not RIGHT_HELD
- System tray icon (pystray): green/red dot, enable toggle, exit
- PyInstaller --onefile packaging → dist/MouseHotkey.exe (~16MB)
- GitHub repo: https://github.com/chautnus/mousehotkey (tagged v1.0.0)
- `run.bat` for dev launch

### Fixed
- ctypes c_long return type: return plain int not ctypes.c_long object
- pynput replacement: rewrote to ctypes WH_MOUSE_LL for per-event suppression
