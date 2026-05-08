import json
import os
from pathlib import Path

from ..types.panel_types import (
    ActionItem, AppItem, FolderItem, MenuItem, ShortcutItem, UrlItem,
)

CONFIG_DIR  = Path(os.environ.get("APPDATA", ".")) / "RightWheel"
CONFIG_PATH = CONFIG_DIR / "shortcuts.json"

_DEFAULT: dict = {
    "version": 2,
    "default": [
        {"type": "shortcut", "label": "🖥 Desktop",           "keys": "win+d"},
        {"type": "shortcut", "label": "🔍 Search",              "keys": "win+s"},
        {"type": "shortcut", "label": "📸 Screenshot",         "keys": "win+shift+s"},
        {"type": "shortcut", "label": "📋 Clipboard History",  "keys": "win+v"},
        {"type": "shortcut", "label": "◧ Align Left",         "keys": "win+left"},
        {"type": "shortcut", "label": "◨ Align Right",        "keys": "win+right"},
        {"type": "folder",   "label": "📁 System",             "children": [
            {"type": "shortcut", "label": "▶ Run",             "keys": "win+r"},
            {"type": "shortcut", "label": "⚙ Settings Windows","keys": "win+i"},
            {"type": "shortcut", "label": "📊 Task Manager",   "keys": "ctrl+shift+esc"},
        ]},
        {"type": "folder",   "label": "📁 App",                "children": [
            {"type": "action", "label": "⚙ App Settings",      "action": "open_settings"},
            {"type": "action", "label": "⏸ Pause RightWheel", "action": "toggle_pause"},
        ]},
    ],
    "profiles": [],
}


# ── migration ─────────────────────────────────────────────────────────────────

def _migrate_v1(data: dict) -> dict:
    return {"version": 2, "default": data.get("shortcuts", []), "profiles": []}


def load() -> dict:
    if not CONFIG_PATH.exists():
        return _DEFAULT.copy()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if data.get("version", 1) == 1:
            data = _migrate_v1(data)
            save(data)
        return data
    except Exception:
        return _DEFAULT.copy()


def save(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


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
            return p["name"], p.get("shortcuts", [])
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
        else:
            out.append({"type": "shortcut", "label": item.label,
                        "keys": item.keys})
    return out
