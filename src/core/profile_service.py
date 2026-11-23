"""Profile service: unified runtime resolver for Command Palette and Mouse Gestures.

Matches HWND info (exe, title, class_name) against profile rules (exe, title_contains, class_name).
Hierarchical fallback: App profile gestures override Global profile; unassigned gestures fall back to Global.
"""
from __future__ import annotations

from typing import Any

from src.core import config_service
from src.core.window_service import get_hwnd_info


def match_rule(rule: dict[str, Any], exe: str, title: str, class_name: str) -> bool:
    """Check if a single rule matches the window info."""
    by = (rule.get("by") or "").strip().lower()
    val = (rule.get("value") or "").strip()
    if by and val:
        if by == "exe":
            return exe.lower() == val.lower()
        elif by == "title_contains":
            return val.lower() in title.lower()
        elif by == "class_name":
            return class_name.lower() == val.lower()
        return False

    matched_any = False
    if "exe" in rule and rule["exe"]:
        matched_any = True
        if exe.lower() != str(rule["exe"]).strip().lower():
            return False
    if "title_contains" in rule and rule["title_contains"]:
        matched_any = True
        if str(rule["title_contains"]).strip().lower() not in title.lower():
            return False
    if "class_name" in rule and rule["class_name"]:
        matched_any = True
        if str(rule["class_name"]).strip().lower() != class_name.lower():
            return False

    return matched_any


def matches_profile(profile: dict[str, Any], exe: str, title: str, class_name: str) -> bool:
    """A profile matches if ALL its rules match (AND logic)."""
    rules = profile.get("match", [])
    if not rules:
        return False
    return all(match_rule(r, exe, title, class_name) for r in rules)


def resolve_active_profile_full(
    hwnd: int,
    config_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve active profile for given HWND with merged hierarchical inheritance (Schema v4)."""
    if config_data is None:
        try:
            config_data = config_service.load_unified_profiles()
        except Exception:
            config_data = dict(config_service.DEFAULT_UNIFIED_CONFIG)

    profiles: list[dict[str, Any]] = config_data.get("profiles", [])
    global_prof = next((p for p in profiles if p.get("is_default") or p.get("id") == "global"), None)
    if global_prof is None:
        global_prof = profiles[0] if profiles else dict(config_service.DEFAULT_UNIFIED_CONFIG["profiles"][0])

    matched_prof = global_prof
    is_global = True

    if hwnd and hwnd > 0:
        exe, title, class_name = get_hwnd_info(hwnd)
        for p in profiles:
            if p.get("is_default") or p.get("id") == "global":
                continue
            if matches_profile(p, exe, title, class_name):
                matched_prof = p
                is_global = False
                break

    # Merge commands & gestures with fallback inheritance
    commands = list(matched_prof.get("commands") or [])
    if not commands and not is_global:
        commands = list(global_prof.get("commands") or [])

    gestures = list(matched_prof.get("gestures") or [])
    effective_gestures = list(gestures)

    # If app profile, inherit gestures not explicitly overridden
    if not is_global:
        app_shapes = {str(g.get("shape") or "".join(g.get("directions", []))) for g in gestures}
        for g in global_prof.get("gestures") or []:
            shape = str(g.get("shape") or "".join(g.get("directions", [])))
            if shape not in app_shapes:
                effective_gestures.append(g)

    return {
        "ok": True,
        "data": {
            "profile_id": matched_prof.get("id", "global"),
            "profile_name": matched_prof.get("name", "Global Profile"),
            "display_name": matched_prof.get("name", "Global Profile"),
            "is_default": is_global,
            "match": matched_prof.get("match", []),
            "commands": commands,
            "gestures": gestures,
            "effective_gestures": config_service.sort_gestures(effective_gestures),
        },
    }
