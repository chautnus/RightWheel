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
]

DEFAULT_MOUSE_GESTURES: list[dict[str, Any]] = [
    {"kind": "draw", "directions": ["D", "R"], "shape": "D_R", "keys": "ctrl+w", "type": "KEY_COMBO", "target": "ctrl+w", "enabled": True, "label": "Close Tab"},
    {"kind": "draw", "directions": ["U", "R"], "shape": "U_R", "keys": "ctrl+t", "type": "KEY_COMBO", "target": "ctrl+t", "enabled": True, "label": "New Tab"},
    {"kind": "draw", "directions": ["L"], "shape": "L", "keys": "alt+left", "type": "KEY_COMBO", "target": "alt+left", "enabled": True, "label": "Back"},
    {"kind": "draw", "directions": ["R"], "shape": "R", "keys": "alt+right", "type": "KEY_COMBO", "target": "alt+right", "enabled": True, "label": "Forward"},
    {"kind": "wheel", "direction": "UP", "type": "COMMAND_PALETTE", "target": "COMMAND_PALETTE", "enabled": True, "label": "Show Shortcut Panel"},
    {"kind": "wheel", "direction": "DOWN", "type": "TASK_VIEW_NAV", "target": "ALT_TAB", "enabled": True, "label": "Alt+Tab Switcher"},
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
    """Return gestures sorted by kind and shape."""
    def _key(g: dict[str, Any]) -> tuple:
        kind = str(g.get("kind", "draw")).lower()
        shape = str(g.get("shape") or "".join(g.get("directions", [])) or g.get("direction", "")).upper()
        return (0 if kind == "wheel" else 1, shape)
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
        migrated_gestures.append({
            "kind": g.get("kind", "draw"),
            "directions": dirs,
            "shape": shape,
            "keys": keys,
            "type": g.get("type", "KEY_COMBO"),
            "target": keys,
            "enabled": bool(g.get("enabled", True)),
            "label": g.get("label", shape),
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
    """Save profiles.json to %APPDATA%\\RightWheel."""
    config_root = get_config_root()
    config_root.mkdir(parents=True, exist_ok=True)
    profiles_path = config_root / "profiles.json"
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)


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
