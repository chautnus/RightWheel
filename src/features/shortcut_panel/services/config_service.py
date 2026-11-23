import json
import os
from pathlib import Path

from ..types.panel_types import (
    ActionItem, AppItem, CommandItem, FolderItem, MenuItem, SequenceItem, ShortcutItem, UrlItem,
)

CONFIG_DIR  = Path(os.environ.get("APPDATA", ".")) / "RightWheel"
CONFIG_PATH = CONFIG_DIR / "shortcuts.json"

_DEFAULT: dict = {
    "version": 3,
    "default": [
        {"type": "shortcut", "label": "Desktop",             "keys": "win+d"},
        {"type": "shortcut", "label": "Search",              "keys": "win+s"},
        {"type": "shortcut", "label": "Screenshot",          "keys": "win+shift+s"},
        {"type": "shortcut", "label": "Clipboard History",   "keys": "win+v"},
        {"type": "shortcut", "label": "Align Left",          "keys": "win+left"},
        {"type": "shortcut", "label": "Align Right",         "keys": "win+right"},
        {"type": "folder",   "label": "System",               "children": [
            {"type": "shortcut", "label": "Run",              "keys": "win+r"},
            {"type": "shortcut", "label": "Settings Windows", "keys": "win+i"},
            {"type": "shortcut", "label": "Task Manager",     "keys": "ctrl+shift+esc"},
        ]},
        {"type": "folder",   "label": "App",                  "children": [
            {"type": "action", "label": "App Settings",       "action": "open_settings"},
            {"type": "action", "label": "Pause RightWheel",   "action": "toggle_pause"},
        ]},
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
    ],
    "profiles": [],
    "gestures": [
        {"directions": ["D", "R"], "keys": "ctrl+w", "enabled": True},
    ],
}


# ── migration ─────────────────────────────────────────────────────────────────

def _migrate_v1(data: dict) -> dict:
    return {"version": 2, "default": data.get("shortcuts", []), "profiles": []}


def migrate_to_v3(data: dict) -> dict:
    if not isinstance(data, dict):
        return {
            "ok": False,
            "error": {
                "code": "INVALID_DATA",
                "file": __file__,
                "line": 48,
                "helper": "Data must be a dictionary",
            },
        }
    new_data = dict(data)
    new_data["version"] = 3
    if "default" not in new_data:
        new_data["default"] = data.get("shortcuts", [])
    if "profiles" not in new_data:
        new_data["profiles"] = []
    if "gestures" not in new_data:
        new_data["gestures"] = [dict(g) for g in _DEFAULT.get("gestures", [])]
    return {"ok": True, "data": new_data}


def _get_config_dir() -> Path:
    try:
        from src.core.app_paths import get_config_root
        return get_config_root()
    except Exception:
        return Path(os.environ.get("APPDATA", ".")) / "RightWheel"


def load() -> dict:
    config_dir = _get_config_dir()
    profiles_path = config_dir / "profiles.json"
    shortcuts_path = config_dir / "shortcuts.json"
    if profiles_path.exists():
        try:
            from src.core.config_service import load_unified_profiles
            v4_doc = load_unified_profiles()
            profiles = v4_doc.get("profiles", [])
            global_prof = next((p for p in profiles if p.get("is_default") or p.get("id") == "global"), None)
            if global_prof is None and profiles:
                global_prof = profiles[0]

            global_commands = list(global_prof.get("commands", [])) if global_prof else []
            global_gestures = list(global_prof.get("gestures", [])) if global_prof else []

            data = {
                "version": 4,
                "default": global_commands,
                "shortcuts": global_commands,
                "gestures": global_gestures,
                "profiles": [
                    {
                        **p,
                        "name": p.get("name", p.get("id", "Profile")),
                        "shortcuts": p.get("commands", p.get("shortcuts", [])),
                        "commands": p.get("commands", p.get("shortcuts", [])),
                    }
                    for p in profiles
                ],
            }
            for g in data.get("gestures", []):
                if isinstance(g, dict) and g.get("directions") == ["D", "R"] and g.get("enabled") is False:
                    g["enabled"] = True
            return data
        except Exception:
            pass

    if not shortcuts_path.exists():
        data = _DEFAULT.copy()
    else:
        try:
            data = json.loads(shortcuts_path.read_text(encoding="utf-8"))
            if data.get("version", 1) == 1:
                data = _migrate_v1(data)
                save(data)
            if data.get("version") == 2:
                res = migrate_to_v3(data)
                if res.get("ok"):
                    data = res["data"]
                    save(data)
        except Exception:
            data = _DEFAULT.copy()

    for g in data.get("gestures", []):
        if isinstance(g, dict) and g.get("directions") == ["D", "R"] and g.get("enabled") is False:
            g["enabled"] = True
    return data


def save(data: dict) -> None:
    config_dir = _get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    shortcuts_path = config_dir / "shortcuts.json"
    shortcuts_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    # Also sync to profiles.json (Schema v4)
    try:
        from src.core.config_service import migrate_to_v4, save_unified_profiles
        if data.get("version") == 4 and "profiles" in data:
            save_unified_profiles(data)
        else:
            v4_doc = migrate_to_v4(data)
            save_unified_profiles(v4_doc)
    except Exception:
        pass


# ── profile resolution ────────────────────────────────────────────────────────

def _matches(rules: list, exe: str, title: str, class_name: str) -> bool:
    if not rules:
        return False
    for rule in rules:
        by, value = rule.get("by", ""), rule.get("value", "")
        if by == "exe":
            if exe.lower() != value.lower():
                return False
        elif by == "title_contains":
            if value.lower() not in title.lower():
                return False
        elif by == "class_name":
            if class_name != value:
                return False
        else:
            return False
    return True


def resolve_profile(exe: str, title: str, class_name: str,
                    data: dict) -> tuple[str, list]:
    for p in data.get("profiles", []):
        if _matches(p.get("match", []), exe, title, class_name):
            cmds = p.get("commands") or p.get("shortcuts") or []
            return p.get("name", "Profile"), cmds
    default_raw = data.get("default", data.get("shortcuts", []))
    return "Default", default_raw


# ── item serialization ────────────────────────────────────────────────────────

def parse_items(raw: list) -> list[MenuItem]:
    result: list[MenuItem] = []
    for entry in raw[:30]:
        if not isinstance(entry, dict):
            continue
        t = entry.get("type", "shortcut")
        if t == "folder":
            result.append(FolderItem(
                label=entry.get("label", "Folder"),
                children=parse_items(entry.get("children", [])),
            ))
        elif t == "app":
            result.append(AppItem(
                label=entry.get("label", "App"),
                path=entry.get("path", ""),
                args=entry.get("args", ""),
            ))
        elif t == "url":
            result.append(UrlItem(
                label=entry.get("label", "URL"),
                url=entry.get("url", ""),
            ))
        elif t == "action":
            result.append(ActionItem(
                label=entry.get("label", "Action"),
                action=entry.get("action", ""),
            ))
        elif t == "command":
            result.append(CommandItem(
                label=entry.get("label", "Command"),
                cmd=entry.get("cmd", ""),
                cwd=entry.get("cwd", ""),
            ))
        elif t == "sequence":
            result.append(SequenceItem(
                label=entry.get("label", "Sequence"),
                steps=entry.get("steps", []),
            ))
        else:
            result.append(ShortcutItem(
                label=entry.get("label", "Item"),
                keys=entry.get("keys", ""),
            ))
    return result


def items_to_raw(items: list[MenuItem]) -> list[dict]:
    out = []
    for item in items:
        if item.type == "folder":
            out.append({"type": "folder", "label": item.label,
                        "children": items_to_raw(item.children)})
        elif item.type == "app":
            out.append({"type": "app",  "label": item.label,
                        "path": item.path, "args": getattr(item, "args", "")})
        elif item.type == "url":
            out.append({"type": "url",  "label": item.label, "url": item.url})
        elif item.type == "action":
            out.append({"type": "action", "label": item.label,
                        "action": item.action})
        elif item.type == "command":
            out.append({"type": "command", "label": item.label,
                        "cmd": item.cmd, "cwd": getattr(item, "cwd", "")})
        elif item.type == "sequence":
            out.append({"type": "sequence", "label": item.label,
                        "steps": getattr(item, "steps", [])})
        else:
            out.append({"type": "shortcut", "label": item.label,
                        "keys": item.keys})
    return out



