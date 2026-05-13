"""Import service — validate and apply shortcut templates from JSON files."""
from __future__ import annotations

import json
from pathlib import Path

from . import config_service

_VALID_TYPES = {"shortcut", "app", "url", "folder", "action"}


# ── validation ────────────────────────────────────────────────────────────────

def _valid_item(item: dict) -> bool:
    if not isinstance(item, dict):
        return False
    itype = item.get("type", "")
    if itype not in _VALID_TYPES:
        return False
    if not item.get("label"):
        return False
    if itype == "shortcut" and not item.get("keys"):
        return False
    if itype == "app" and not item.get("path"):
        return False
    if itype == "url" and not item.get("url"):
        return False
    return True


def _clean(item: dict) -> dict:
    itype = item["type"]
    out: dict = {"type": itype, "label": item["label"]}
    if itype == "shortcut":
        out["keys"] = item["keys"]
    elif itype == "app":
        out["path"] = item["path"]
        out["args"] = item.get("args", "")
    elif itype == "url":
        out["url"] = item["url"]
    elif itype == "folder":
        out["children"] = [
            _clean(c) for c in item.get("children", []) if _valid_item(c)
        ]
    elif itype == "action":
        out["action"] = item.get("action", "")
    return out


# ── public API ────────────────────────────────────────────────────────────────

def load_template(path: str) -> tuple[str, str, list[dict], str | None]:
    """
    Parse and validate a template JSON file.
    Returns (name, description, items, error).
    error is None on success.
    """
    try:
        raw  = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        return "", "", [], f"Cannot read file: {exc}"

    if not isinstance(data, dict):
        return "", "", [], "Template must be a JSON object."

    shortcuts = data.get("shortcuts")
    if not isinstance(shortcuts, list):
        return "", "", [], 'Template must have a "shortcuts" array.'

    items = [_clean(i) for i in shortcuts if _valid_item(i)]
    if not items:
        return "", "", [], "No valid shortcuts found in template."

    name = data.get("name", Path(path).stem)
    desc = data.get("description", "")
    return name, desc, items, None


def apply(items: list[dict], mode: str) -> int:
    """
    mode: 'append' | 'replace'
    Returns number of items imported.
    """
    data = config_service.load()
    if mode == "replace":
        data["default"] = list(items)
    else:
        data.setdefault("default", []).extend(items)
    config_service.save(data)
    return len(items)
