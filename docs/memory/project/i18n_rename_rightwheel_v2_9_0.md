---
id: proj_i18n_rename_rightwheel_20260508
type: project
title: "i18n System + Rename MouseHotkey → RightWheel (v2.9.0)"
tags: [i18n, rename, rightwheel, localization, license, tray]
keywords: [i18n, t(), locale, multilingual, RightWheel, LemonSqueezy, license_types]
status: active
created: 2026-05-08
updated: 2026-05-08
summary: "Full i18n system (9 languages) + rename MouseHotkey→RightWheel + license UI localized + language selector in settings + build RightWheel.exe v2.9.0"
---

## Why

- License UI was hardcoded in Vietnamese — needed English + full multilingual support
- App name "MouseHotkey" is generic; "RightWheel" is branded and descriptive
- Users in 9 markets (EN/FR/PT/ES/IT/VI/ID/TH/ZH) need native UI

## What

### i18n Engine (`src/features/i18n/__init__.py`)

- `t(key, **kwargs)` — translate with `str.format(**kwargs)` interpolation, fallback to English, then key itself
- `init()` — auto-detect from `locale.getdefaultlocale()`, override with saved pref at `%APPDATA%\RightWheel\lang.txt`
- `set_locale(code)` — switch language + persist preference
- `available()` — list of `(code, native_name)` tuples for UI selector
- `ui_font(base)` — returns `"Microsoft YaHei"` for `zh`, `"Tahoma"` for `th`, otherwise `base`
- `current()` — returns current language code string

### Locale files (9 total)

| File | Language |
|------|----------|
| `en.py` | English (~82 keys) |
| `fr.py` | Français |
| `pt.py` | Português |
| `es.py` | Español |
| `it.py` | Italiano |
| `vi.py` | Tiếng Việt |
| `id.py` | Indonesia |
| `th.py` | ภาษาไทย |
| `zh.py` | 中文 (Simplified) |

### Key string categories (all in en.py)

- `app.*` — name, tagline, subtitle
- `welcome.*` — f1..f7 triggers+descs, run_on_startup, get_started
- `settings.*` — title, header, tabs, language label, restart_required
- `lic.*` — states, days_remaining, active_sub, key_label, activate, buy_now, success/failed/etc.
- `btn.*` — shortcut, app, url, folder, edit, delete, del, up, down, done, ok, cancel
- `dlg.*` — all dialog titles and field labels
- `recorder.*` — title, prompt, sub
- `folder.*` — title, subtitle
- `tray.*` — enable, settings, exit, trial, activate

### License service refactor (`license_service.py`)

- Removed hardcoded Vietnamese error strings from `activate()` / `deactivate()`
- `activate()` now returns machine-readable codes: `"success"`, `"no_key"`, `"connect_failed:{msg}"`, `"failed"`
- `deactivate()` returns: `"deactivated"`, `"no_license"`
- `license_window.py` maps codes → `t()` calls for display

### `license_types.py` refactor

- Removed `_STATE_META` dict with hardcoded Vietnamese labels
- `state_label(s)` now calls `t(f"lic.state.{s.value}")` — fully localized
- Badge colors kept in `_STATE_COLOR` dict (colors are language-neutral)

### Rename: MouseHotkey → RightWheel

| File | Change |
|------|--------|
| `config_service.py` | `CONFIG_DIR / "RightWheel"` |
| `license_service.py` | `_CONFIG_DIR / "RightWheel"` |
| `startup_service.py` | `_APP_NAME = "RightWheel"` |
| `tray_ui.py` | default title `"RightWheel"`, icon name `"RightWheel"` |
| `main.py` | docstring, sys.exit message, tray title via `t()` |
| `RightWheel.spec` | `name='RightWheel'` (new spec file) |

### Language selector (settings footer)

- `ttk.Combobox` in settings footer with native language names
- On select → `set_locale(code)` + show "Restart required" label in amber
- Preference persisted to `%APPDATA%\RightWheel\lang.txt`

### PyInstaller spec (`RightWheel.spec`)

- Added all 9 locale modules to `hiddenimports` (loaded dynamically via `importlib.import_module`)
- `name='RightWheel'` → produces `dist/RightWheel.exe`

## How to apply

- **Config dir moved**: `%APPDATA%\MouseHotkey\` → `%APPDATA%\RightWheel\`
  - On first run after upgrade, config will reset to defaults (no auto-migration across dir names)
  - Manual migration: copy `%APPDATA%\MouseHotkey\shortcuts.json` → `%APPDATA%\RightWheel\shortcuts.json`
- **Build**: `python -m PyInstaller RightWheel.spec --noconfirm`
- **Old spec**: `MouseHotkey.spec` still exists but is superseded by `RightWheel.spec`
- **Startup registry**: Old `MouseHotkey` registry key won't be cleaned up automatically; new key is `RightWheel`
