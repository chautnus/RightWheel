---
id: proj_context_aware_profiles_20260507
type: project
title: "Context-Aware Profiles — Full Implementation"
tags: [profiles, window-detection, config-v2, ui]
keywords: [profile, resolve_profile, window_service, config v2, match rules, ProfileEditor]
status: active
created: 2026-05-07
updated: 2026-05-07
summary: "Schema v2 + window detection + profile CRUD UI — different shortcut sets per active application"
---

## Why

User requested different shortcut sets based on the active window (e.g., Word vs Canva vs Default). The existing v1 config only had a single flat "shortcuts" array. Needed: multi-profile support with exe/title/class matching, full settings UI, and zero breaking change for existing configs.

## What

### Files created / modified

| File | Change |
|------|--------|
| `types/panel_types.py` | Added `MatchRule` and `Profile` dataclasses |
| `services/window_service.py` | **NEW** — ctypes-only exe+title+class detection via `GetWindowTextW`, `GetClassNameW`, `QueryFullProcessImageNameW` |
| `services/config_service.py` | **REWRITTEN** — schema v2, `resolve_profile()`, `_matches()`, v1→v2 auto-migration in `load()` |
| `logic/panel_logic.py` | Wired `window_service` + `resolve_profile` into `show()`; added `active_profile` property |
| `ui/profile_editor.py` | **NEW** — `ProfileEditor(tk.Frame)`: left list panel + right detail panel (name, match rules, shortcuts) |
| `ui/settings_window.py` | Added `ttk.Notebook` with "Default" tab + "Profiles" tab; version bumped to 2.4.0; all `"shortcuts"` keys → `"default"` |
| `ui/panel_window.py` | Shows active profile name in panel header (blue badge) when not Default |

### Schema v2

```json
{
  "version": 2,
  "default": [ ...shortcuts... ],
  "profiles": [
    {
      "name": "Microsoft Word",
      "match": [ { "by": "exe", "value": "WINWORD.EXE" } ],
      "shortcuts": [ ...word-specific shortcuts... ]
    }
  ]
}
```

**v1 → v2 migration:** automatic in `config_service.load()` — renames `"shortcuts"` → `"default"`, adds `"profiles": []`, saves immediately.

### Match rule types

| `by` | Logic | Example value |
|------|-------|---------------|
| `exe` | basename, case-insensitive | `WINWORD.EXE` |
| `title_contains` | window title contains string (lowercase) | `Canva` |
| `class_name` | Win32 class name, exact | `OpusApp` |

Multiple rules = AND logic. First matching profile wins. Fallback → Default.

### Key functions

```python
# window_service.py
def get_hwnd_info(hwnd: int) -> tuple[str, str, str]:
    # Returns (exe_basename, window_title, class_name)
    # Uses: GetWindowTextW, GetClassNameW, GetWindowThreadProcessId,
    #       OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION), QueryFullProcessImageNameW

# config_service.py
def resolve_profile(exe, title, class_name, data) -> tuple[str, list]:
    # Returns (profile_name, raw_shortcuts_list)

def _matches(rules, exe, title, class_name) -> bool:
    # AND logic — all rules must match; empty rules → never match
```

### panel_logic.show() flow

```
GetForegroundWindow(hwnd)
  → window_service.get_hwnd_info(hwnd)  → (exe, title, class_name)
  → config_service.resolve_profile(...)  → (profile_name, raw)
  → config_service.parse_items(raw)      → list[MenuItem]
  → self._active_profile = profile_name
  → self._items = resolved items
  → on_show callback
```

### profile_editor.py — ProfileEditor widget

- Left pane (160px fixed): listbox of profile names + Add/Delete
- Right pane (expand): placeholder or detail (name entry + 💾, match rules listbox, shortcuts listbox)
- Inline `_ask()` dialog (dark theme) — avoids circular import with settings_window
- Self-contained: embed with `ProfileEditor(parent).pack(fill="both", expand=True)`

## How to apply

- Open Settings → "Profiles" tab to create/manage profiles
- Add match rules (exe, title_contains, or class_name)
- Add shortcuts to each profile
- When panel opens, the header shows a blue "◈ ProfileName" badge if a profile matched
- Fallback to Default if no profile matches

## CLAUDE.md rules triggered this session

- Rule 3B (MACRO-TASK): `/design-feature` was run in prior session → blueprint already existed
- Rule 2: All modified files checked under 250 lines (settings_window.py trimmed from 260→244)
- Rule 4: Targeted reads only — no speculative scanning
