# Feature: shortcut_panel (v2)

## Trách nhiệm từng file

| File | Trách nhiệm | Dự kiến dòng |
|------|------------|--------------|
| `types/panel_types.py` | Dataclasses: `ShortcutItem`, `FolderItem`, `PanelConfig`, `NavState` | ~50 |
| `services/config_service.py` | Load/save JSON config, default config, migration | ~70 |
| `services/shortcut_executor.py` | Parse key string → SendInput (reuse hotkey_service pattern) | ~80 |
| `logic/panel_logic.py` | Navigation state: index, folder stack, show/hide/enter/select | ~100 |
| `ui/panel_window.py` | Tkinter frameless window: narrow+tall, numbered list, scroll highlight | ~140 |
| `ui/settings_window.py` | Tkinter settings UI: CRUD shortcuts, drag-reorder, save | ~140 |
| `__init__.py` | Re-export public API | ~5 |

## Luồng dữ liệu

```
[RMB + scroll up]
      │
      ▼
mouse_mapper_logic ──── show_panel() ────▶ panel_logic
                                                │
                                         load config (config_service)
                                                │
                                                ▼
                                         panel_window.render()
                                         (tkinter, always-on-top)
                                                │
                              ┌─────────────────┼──────────────────┐
                         scroll up/down    left-click folder    left-click shortcut
                              │                  │                   │
                         panel_logic         panel_logic         shortcut_executor
                         .navigate()         .enter_folder()     .execute(keys)
                              │                  │                   │
                         re-render           re-render          panel_window.close()

[Tray menu → Settings]
      │
      ▼
settings_window ──── edit ────▶ config_service.save() ──▶ panel_logic.reload()
```

## Config JSON schema

```json
{
  "version": 1,
  "shortcuts": [
    {"label": "VS Code",  "keys": "ctrl+shift+v", "type": "shortcut"},
    {"label": "Browser",  "keys": "ctrl+shift+b", "type": "shortcut"},
    {
      "label": "Tools",   "type": "folder",
      "children": [
        {"label": "Terminal", "keys": "ctrl+alt+t"},
        {"label": "Git",      "keys": "ctrl+shift+g"}
      ]
    }
  ]
}
```

## Panel UI spec

```
┌──────────┐
│ 0  Item  │  ← normal
│ 1  Item  │
│ 2  ITEM  │  ← highlighted (scroll here, font larger)
│ 3  Item  │
│ 4  📁 Fol│  ← folder (left-click to enter)
│ ...      │
└──────────┘
Width: 220px | Font normal: 13px | Font highlight: 17px bold
ESC / click outside → close without action
```

## State machine

```
HIDDEN
  → show(): load config → VISIBLE (index=0, stack=[root])

VISIBLE
  → scroll up/down:   navigate(±1) → re-render
  → LMB on shortcut:  execute → HIDDEN
  → LMB on folder:    push folder onto stack → re-render (stay VISIBLE)
  → ESC / blur:       HIDDEN
```

## Dependencies

```
panel_window  → panel_logic → config_service → panel_types
panel_window  → panel_logic → shortcut_executor
settings_window → config_service → panel_types
mouse_mapper_logic → panel_logic (show/hide)
main.py → panel_logic + settings_window (tray menu wiring)
```
