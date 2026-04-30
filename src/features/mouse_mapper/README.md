# Feature: mouse_mapper

## Trách nhiệm từng file

| File | Trách nhiệm | Dự kiến dòng |
|------|-------------|--------------|
| `types/mouse_mapper_types.py` | Dataclasses, Enums: `MapperState`, `MouseEvent`, `HotkeyConfig` | ~40 |
| `services/mouse_hook_service.py` | Global mouse listener (pynput). Emit raw events, suppress/pass-through | ~80 |
| `services/hotkey_service.py` | Inject keystrokes qua win32api (Alt+Tab, Alt+Shift+Tab) | ~40 |
| `logic/mouse_mapper_logic.py` | State machine: IDLE → RIGHT_HELD → HOLD_CANCELLED. Quyết định suppress/inject | ~100 |
| `ui/tray_ui.py` | System tray icon (pystray), menu toggle enable/disable, exit | ~60 |
| `__init__.py` | Re-export public API | ~5 |

## Luồng dữ liệu

```
[Mouse Hardware]
      │ raw events
      ▼
mouse_hook_service  ──── MouseEvent ────▶  mouse_mapper_logic
      │                                          │
      │ suppress()                               │ inject hotkey
      ▼                                          ▼
[OS: block context menu]                  hotkey_service ──▶ [OS: Alt+Tab]
                                                │
                                          [MapperState update]
                                                │
                                                ▼
                                           tray_ui (status display)
```

## State Machine

```
IDLE ──(RightDown)──▶ RIGHT_HELD
  ▲                        │
  │                   ┌────┴───────────────────┐
  │             (scroll)                  (timeout 500ms)
  │                   │                        │
  │             inject Alt+Tab          HOLD_CANCELLED
  │             stay RIGHT_HELD               │
  │                                     (RightUp: suppress ctx menu)
  └────────────────────────────────────────────┘
         (RightUp sớm, chưa scroll → pass-through ctx menu)
```

## Dependencies

```
tray_ui → logic → services → types
main → tray_ui + mouse_hook_service (start/stop)
```

## Setup

```bash
pip install pynput pystray pillow pywin32
python src/main.py
```
