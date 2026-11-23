"""Configuration service: APPDATA migration, v4 schema migration, and config I/O for RightWheel."""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from src.core.app_paths import get_app_root, get_config_root

DEFAULT_COMMANDS: list[dict[str, Any]] = [
    {"type": "shortcut", "label": "Desktop", "keys": "win+d"},
    {"type": "shortcut", "label": "Search", "keys": "win+s"},
    {"type": "shortcut", "label": "Screenshot", "keys": "win+shift+s"},
    {"type": "shortcut", "label": "Clipboard History", "keys": "win+v"},
    {"type": "shortcut", "label": "Align Left", "keys": "win+left"},
    {"type": "shortcut", "label": "Align Right", "keys": "win+right"},
    {
        "type": "folder",
        "label": "System",
        "children": [
            {"type": "shortcut", "label": "Run", "keys": "win+r"},
            {"type": "shortcut", "label": "Settings Windows", "keys": "win+i"},
            {"type": "shortcut", "label": "Task Manager", "keys": "ctrl+shift+esc"},
        ],
    },
    {
        "type": "folder",
        "label": "App",
        "children": [
            {"type": "action", "label": "App Settings", "action": "open_settings"},
            {"type": "action", "label": "Pause RightWheel", "action": "toggle_pause"},
        ],
    },
    {
        "type": "sequence",
        "label": "Search Copied Text",
        "steps": [
            {"type": "shortcut", "keys": "ctrl+c", "delay_ms": 150},
            {"type": "url_clipboard", "url_template": "https://www.google.com/search?q={text}", "delay_ms": 10},
        ],
    },
    {
        "type": "sequence",
        "label": "ChatGPT: Paste Clipboard",
        "steps": [
            {"type": "shortcut", "keys": "ctrl+c", "delay_ms": 200},
            {"type": "url", "url": "https://chatgpt.com", "delay_ms": 3000},
            {"type": "shortcut", "keys": "ctrl+v", "delay_ms": 800},
            {"type": "shortcut", "keys": "enter", "delay_ms": 10},
        ],
    },
]

GESTURE_DESCRIPTIONS: dict[str, str] = {
    # Nhóm U: Lên
    "U": "Cuộn lên đầu trang / Mở tab mới",
    "U_D": "Tải lại trang (Refresh / F5)",
    "U_R": "Mở tab trình duyệt mới (New Tab)",
    "U_L": "Khôi phục tab vừa đóng (Reopen Closed Tab)",
    # Nhóm D: Xuống
    "D": "Cuộn xuống cuối trang / Thu nhỏ cửa sổ",
    "D_U": "Mở cửa sổ mới (New Window)",
    "D_R": "Đóng tab trình duyệt hiện tại (Close Tab)",
    "D_L": "Mở liên kết trong tab mới ngầm",
    # Nhóm L: Trái
    "L": "Quay lại trang trước (Back)",
    "L_R": "Chuyển sang tab bên phải",
    "L_U": "Chuyển sang tab bên trái",
    "L_D": "Đóng cửa sổ hiện tại (Alt+F4)",
    # Nhóm R: Phải
    "R": "Đi tới trang kế tiếp (Forward)",
    "R_L": "Chuyển sang tab trước đó",
    "R_U": "Phóng to toàn màn hình (F11)",
    "R_D": "Thu nhỏ cửa sổ xuống Taskbar",
    # Wheel & Action targets
    "COMMAND_PALETTE": "Mở Bảng lệnh phím tắt nhanh tại con trỏ chuột",
    "ALT_TAB": "Chuyển đổi qua lại giữa các ứng dụng đang mở (Alt+Tab)",
    "TASK_VIEW_NAV": "Chuyển đổi qua lại giữa các ứng dụng đang mở (Alt+Tab)",
}

_DRAW_GESTURE_ORDER = [
    # Nhóm U: Lên, Lên Xuống, Lên Phải, Lên Trái
    "U", "U_D", "U_R", "U_L",
    # Nhóm D: Xuống, Xuống Lên, Xuống Phải, Xuống Trái
    "D", "D_U", "D_R", "D_L",
    # Nhóm L: Trái, Trái Phải, Trái Lên, Trái Xuống
    "L", "L_R", "L_U", "L_D",
    # Nhóm R: Phải, Phải Trái, Phải Lên, Phải Xuống
    "R", "R_L", "R_U", "R_D",
]
_DRAW_GESTURE_INDEX = {code: i for i, code in enumerate(_DRAW_GESTURE_ORDER)}

DEFAULT_MOUSE_GESTURES: list[dict[str, Any]] = [
    {"kind": "draw", "directions": ["D", "R"], "shape": "D_R", "keys": "ctrl+w", "type": "KEY_COMBO", "target": "ctrl+w", "enabled": True, "label": "Close Tab", "description": "Đóng tab trình duyệt hiện tại (Close Tab)"},
    {"kind": "draw", "directions": ["U", "R"], "shape": "U_R", "keys": "ctrl+t", "type": "KEY_COMBO", "target": "ctrl+t", "enabled": True, "label": "New Tab", "description": "Mở tab trình duyệt mới (New Tab)"},
    {"kind": "draw", "directions": ["L"], "shape": "L", "keys": "alt+left", "type": "KEY_COMBO", "target": "alt+left", "enabled": True, "label": "Back", "description": "Quay lại trang trước (Back)"},
    {"kind": "draw", "directions": ["R"], "shape": "R", "keys": "alt+right", "type": "KEY_COMBO", "target": "alt+right", "enabled": True, "label": "Forward", "description": "Đi tới trang kế tiếp (Forward)"},
    {"kind": "wheel", "direction": "UP", "type": "COMMAND_PALETTE", "target": "COMMAND_PALETTE", "enabled": True, "label": "Show Shortcut Panel", "description": "Mở Bảng lệnh phím tắt nhanh tại con trỏ chuột"},
    {"kind": "wheel", "direction": "DOWN", "type": "TASK_VIEW_NAV", "target": "ALT_TAB", "enabled": True, "label": "Alt+Tab Switcher", "description": "Chuyển đổi qua lại giữa các ứng dụng đang mở (Alt+Tab)"},
]

DEFAULT_UNIFIED_CONFIG: dict[str, Any] = {
    "version": 4,
    "profiles": [
        {
            "id": "global",
            "name": "Global Profile",
            "is_default": True,
            "match": [],
            "commands": DEFAULT_COMMANDS,
            "gestures": DEFAULT_MOUSE_GESTURES,
        }
    ],
}


def sort_gestures(gestures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return gestures sorted by kind (wheel first) and hierarchical first-stroke order."""
    def _key(g: dict[str, Any]) -> tuple:
        kind = str(g.get("kind", "draw")).lower()
        if kind == "wheel":
            direction = str(g.get("direction", "")).upper()
            return (0, 0 if direction == "UP" else 1, "")

        shape = str(g.get("shape") or "").upper()
        if not shape:
            dirs = g.get("directions") or []
            shape = "_".join(dirs).upper() if isinstance(dirs, list) else str(dirs).upper()
        idx = _DRAW_GESTURE_INDEX.get(shape, 999)
        return (1, idx, shape)

    return sorted(gestures, key=_key)


def migrate_to_v4(legacy_shortcuts: dict[str, Any]) -> dict[str, Any]:
    """Migrate legacy shortcuts.json to unified Schema v4 profiles.json."""
    if not isinstance(legacy_shortcuts, dict):
        return dict(DEFAULT_UNIFIED_CONFIG)

    commands = legacy_shortcuts.get("default") or legacy_shortcuts.get("shortcuts") or DEFAULT_COMMANDS
    gestures_raw = legacy_shortcuts.get("gestures") or DEFAULT_MOUSE_GESTURES

    migrated_gestures: list[dict[str, Any]] = []
    for g in gestures_raw:
        if not isinstance(g, dict):
            continue
        dirs = g.get("directions") or []
        shape = "_".join(dirs) if isinstance(dirs, list) else str(g.get("shape", ""))
        keys = g.get("keys") or g.get("target") or ""
        desc = g.get("description") or GESTURE_DESCRIPTIONS.get(shape) or GESTURE_DESCRIPTIONS.get(g.get("target", "")) or ""
        migrated_gestures.append({
            "kind": g.get("kind", "draw"),
            "directions": dirs,
            "shape": shape,
            "keys": keys,
            "type": g.get("type", "KEY_COMBO"),
            "target": keys,
            "enabled": bool(g.get("enabled", True)),
            "label": g.get("label", shape),
            "description": desc,
        })

    profiles_list: list[dict[str, Any]] = [
        {
            "id": "global",
            "name": "Global Profile",
            "is_default": True,
            "match": [],
            "commands": list(commands),
            "gestures": migrated_gestures,
        }
    ]

    # Convert any existing legacy profiles
    for p in legacy_shortcuts.get("profiles", []):
        if not isinstance(p, dict):
            continue
        pid = str(p.get("id") or p.get("name", "app")).lower()
        profiles_list.append({
            "id": pid,
            "name": str(p.get("name") or pid),
            "is_default": False,
            "match": p.get("match") or [{"by": "exe", "value": str(p.get("exe") or "")}],
            "commands": list(p.get("commands") or p.get("shortcuts") or []),
            "gestures": list(p.get("gestures") or []),
        })

    return {"version": 4, "profiles": profiles_list}


def load_unified_profiles() -> dict[str, Any]:
    """Load profiles.json from %APPDATA%\\RightWheel, migrating from shortcuts.json if needed."""
    config_root = get_config_root()
    profiles_path = config_root / "profiles.json"
    shortcuts_path = config_root / "shortcuts.json"

    if profiles_path.exists():
        try:
            with open(profiles_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data.get("version") == 4 and "profiles" in data:
                # Ensure default gestures have action descriptions populated
                for prof in data.get("profiles", []):
                    for g in prof.get("gestures", []):
                        if not g.get("description"):
                            shape = str(g.get("shape") or "".join(g.get("directions", [])) or g.get("direction", "")).upper()
                            target = str(g.get("target") or g.get("type", "")).upper()
                            desc = GESTURE_DESCRIPTIONS.get(shape) or GESTURE_DESCRIPTIONS.get(target)
                            if desc:
                                g["description"] = desc
                return data
        except Exception:
            pass

    # Migrate from shortcuts.json if available
    if shortcuts_path.exists():
        try:
            with open(shortcuts_path, "r", encoding="utf-8") as f:
                legacy = json.load(f)
            doc = migrate_to_v4(legacy)
            save_unified_profiles(doc)
            return doc
        except Exception:
            pass

    # Fallback to default
    doc = dict(DEFAULT_UNIFIED_CONFIG)
    save_unified_profiles(doc)
    return doc


def save_unified_profiles(doc: dict[str, Any]) -> None:
    """Save profiles.json to %APPDATA%\\RightWheel and sync shortcuts.json for compatibility."""
    config_root = get_config_root()
    config_root.mkdir(parents=True, exist_ok=True)

    # Ensure top-level default/shortcuts/gestures sync into global profile if present
    if isinstance(doc, dict):
        default_cmds = doc.get("default") or doc.get("shortcuts")
        gestures = doc.get("gestures")
        profiles = doc.get("profiles", [])
        if profiles and isinstance(profiles, list):
            global_prof = next((p for p in profiles if p.get("is_default") or p.get("id") == "global"), profiles[0])
            if default_cmds is not None:
                global_prof["commands"] = list(default_cmds)
                global_prof["shortcuts"] = list(default_cmds)
            if gestures is not None:
                global_prof["gestures"] = list(gestures)

    profiles_path = config_root / "profiles.json"
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)

    # Dual-write sync to shortcuts.json for compatibility
    try:
        shortcuts_path = config_root / "shortcuts.json"
        profiles = doc.get("profiles", [])
        global_prof = next((p for p in profiles if p.get("is_default") or p.get("id") == "global"), None)
        global_commands = global_prof.get("commands", []) if global_prof else []
        global_gestures = global_prof.get("gestures", []) if global_prof else []
        v3_payload = {
            "version": 3,
            "default": global_commands,
            "shortcuts": global_commands,
            "gestures": global_gestures,
            "profiles": [
                {
                    "id": p.get("id", "profile"),
                    "name": p.get("name", p.get("id", "Profile")),
                    "match": p.get("match", []),
                    "shortcuts": p.get("commands", []),
                    "commands": p.get("commands", []),
                    "gestures": p.get("gestures", []),
                }
                for p in profiles if not (p.get("is_default") or p.get("id") == "global")
            ],
        }
        with open(shortcuts_path, "w", encoding="utf-8") as f:
            json.dump(v3_payload, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def load_app_settings() -> dict[str, Any]:
    """Load app_settings.json from %APPDATA%\\RightWheel."""
    path = get_config_root() / "app_settings.json"
    defaults = {
        "language": "vi",
        "autostart": True,
        "ui_engine": "webview",
        "show_welcome": True,
        "gesture_trail": True,
    }
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                defaults.update(data)
        except Exception:
            pass
    return defaults


def save_app_settings(data: dict[str, Any]) -> None:
    """Save app_settings.json to %APPDATA%\\RightWheel."""
    config_root = get_config_root()
    config_root.mkdir(parents=True, exist_ok=True)
    path = config_root / "app_settings.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
