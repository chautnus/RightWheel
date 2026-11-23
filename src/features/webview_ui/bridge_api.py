"""JS <-> Python Bridge API for RightWheel V3 WebView2 UI."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from src.core.app_discovery import get_installed_apps
from src.core.app_paths import get_config_root
from src.core.config_service import (
    DEFAULT_UNIFIED_CONFIG,
    load_unified_profiles,
    save_unified_profiles,
    sort_gestures,
)
from src.core.i18n import SUPPORTED_LANGUAGES, _TRANSLATIONS, get_language, set_language, t
from src.core.store_license_service import get_license_service
from src.core.webclip_templates import search_webclip_templates
from src.features.shortcut_panel.ui.reference_shortcuts_data import get_localized_shortcuts
from src.features.webview_ui.key_recorder_bridge import capture_next_key_combo


def _ok(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data}


def _err(code: str, helper: str, message: str, field: str | None = None) -> dict[str, Any]:
    err: dict[str, Any] = {
        "code": code,
        "file": "src/features/webview_ui/bridge_api.py",
        "helper": helper,
        "message": message,
    }
    if field:
        err["field"] = field
    return {"ok": False, "error": err}


def binding_key_for(entry: dict[str, Any]) -> str:
    """Return canonical lookup key for gesture/wheel action."""
    kind = str(entry.get("kind", "draw")).lower()
    if kind == "wheel":
        return f"wheel_{str(entry.get('direction', '')).lower()}"
    return str(entry.get("shape") or "_".join(entry.get("directions", [])) or entry.get("keys") or "")


def _gesture_label(g: dict[str, Any]) -> str:
    kind = str(g.get("kind", "draw")).lower()
    if kind == "wheel":
        return f"Wheel {g.get('direction', '')}".strip()
    shape = str(g.get("shape") or "_".join(g.get("directions", [])))
    return f"Gesture {shape}".strip()


def _normalize_match_rule(r: Any) -> dict[str, Any]:
    if not isinstance(r, dict):
        return {}
    exe = str(r.get("exe") or (r.get("value") if r.get("by") == "exe" else "") or "").strip()
    title = str(r.get("title_contains") or (r.get("value") if r.get("by") == "title_contains" else "") or "").strip()
    class_name = str(r.get("class_name") or (r.get("value") if r.get("by") == "class_name" else "") or "").strip()

    res = dict(r)
    if exe:
        res["by"] = "exe"
        res["value"] = exe
        res["exe"] = exe
    elif title:
        res["by"] = "title_contains"
        res["value"] = title
        res["title_contains"] = title
    elif class_name:
        res["by"] = "class_name"
        res["value"] = class_name
        res["class_name"] = class_name
    return res


def _normalize_profile_v4(raw: dict[str, Any]) -> dict[str, Any]:
    pid = str(raw.get("id") or "global")
    is_default = bool(raw.get("is_default") or raw.get("is_global") or pid == "global")
    match = raw.get("match")
    if not isinstance(match, list):
        pnames = raw.get("process_names") or []
        match = [{"by": "exe", "value": str(exe), "exe": str(exe)} for exe in pnames if str(exe).strip()]
    else:
        match = [_normalize_match_rule(r) for r in match if isinstance(r, dict) and _normalize_match_rule(r)]
    commands = raw.get("commands")
    if not isinstance(commands, list):
        items = raw.get("items") or raw.get("shortcuts")
        commands = list(items) if isinstance(items, list) else []
    gestures = raw.get("gestures")
    if not isinstance(gestures, list):
        gestures = []
    return {
        "id": pid,
        "name": str(raw.get("name") or ("Global" if is_default else pid)),
        "is_default": is_default,
        "match": match,
        "commands": commands,
        "gestures": sort_gestures(gestures),
    }


class WebViewBridgeAPI:
    """Exposed as window.pywebview.api inside WebView2."""

    def __init__(
        self,
        config_dir: Path | None = None,
        window_ref: Any = None,
        default_view: str = "settings",
    ) -> None:
        self._config_dir = config_dir or get_config_root()
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._settings_path = self._config_dir / "app_settings.json"
        self._profiles_path = self._config_dir / "profiles.json"
        self._window = window_ref
        self._default_view = default_view if default_view in ("settings", "welcome", "wizard") else "settings"

    def set_window(self, window_ref: Any) -> None:
        self._window = window_ref

    def _load_raw_settings(self) -> dict[str, Any]:
        if not self._settings_path.exists():
            return {}
        try:
            data = json.loads(self._settings_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _load_app_settings(self) -> dict[str, Any]:
        defaults: dict[str, Any] = {
            "language": get_language(),
            "autostart": True,
            "ui_engine": "webview",
            "show_welcome": True,
            "gesture_trail": True,
            "macro_delay_ms": 40,
        }
        raw = self._load_raw_settings()
        defaults.update(raw)
        defaults["available_languages"] = [code for code, _ in SUPPORTED_LANGUAGES]
        defaults["language_options"] = [{"code": code, "name": name} for code, name in SUPPORTED_LANGUAGES]
        return defaults

    def _save_app_settings(self, data: dict[str, Any]) -> None:
        persisted = {
            k: v for k, v in data.items()
            if k not in ("available_languages", "language_options", "translations", "reference_shortcuts")
        }
        self._settings_path.write_text(json.dumps(persisted, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_profiles_doc(self) -> dict[str, Any]:
        doc = load_unified_profiles()
        doc["profiles"] = [_normalize_profile_v4(p) for p in doc.get("profiles", [])]
        return doc

    def _save_profiles_doc(self, doc: dict[str, Any]) -> list[dict[str, Any]]:
        normalized = [_normalize_profile_v4(p) for p in doc.get("profiles", [])]
        payload = {"version": 4, "profiles": normalized}
        save_unified_profiles(payload)
        return normalized

    def _build_license_info(self) -> dict[str, Any]:
        lic_svc = get_license_service()
        st = lic_svc.get_status() if hasattr(lic_svc, "get_status") else {}
        is_pro = bool(st.get("is_pro", False))
        is_trial = bool(st.get("is_trial", True))
        days = int(st.get("days_remaining", 30))
        secs = int(st.get("seconds_remaining", days * 86400))
        fmt_left = str(st.get("formatted_time_left", f"{days}d"))
        if is_pro:
            label = t("status_pro", "● Pro License Activated")
        elif is_trial:
            if days >= 1:
                label = t("status_trial", "○ Trial: {days} days remaining").replace("{days}", str(days))
            else:
                label = t("status_trial_countdown", "○ Trial: {time} remaining").replace("{time}", fmt_left)
        else:
            label = t("status_expired", "▲ Trial Expired")
        return {
            "is_pro": is_pro,
            "is_trial": is_trial,
            "trial_days_left": days,
            "seconds_remaining": secs,
            "formatted_time_left": fmt_left,
            "status_label": label,
            "trial_total_days": int(st.get("trial_total_days", 30)),
        }

    def _build_i18n_payload(self, lang: str) -> tuple[dict[str, str], list[dict[str, str]]]:
        translations = dict(_TRANSLATIONS.get(lang, _TRANSLATIONS.get("vi", {})))
        shortcuts = [
            {"category": cat, "keys": keys, "description": desc}
            for cat, keys, desc in get_localized_shortcuts(lang)
        ]
        return translations, shortcuts

    def get_initial_state(self, view: str = "") -> dict[str, Any]:
        resolved_view = view if view in ("settings", "welcome", "wizard") else self._default_view
        settings = self._load_app_settings()
        lang = str(settings.get("language") or "vi")
        set_language(lang)
        translations, ref_shortcuts = self._build_i18n_payload(lang)

        doc = self._load_profiles_doc()
        profiles = [_normalize_profile_v4(p) for p in doc.get("profiles", [])]
        global_prof = next((p for p in profiles if p.get("is_default") or p.get("id") == "global"), None)
        gestures = [
            {
                "key": binding_key_for(g),
                "label": _gesture_label(g),
                "action_type": g.get("type", "KEY_COMBO"),
                "target": g.get("target", ""),
                "enabled": g.get("enabled", True),
                "raw": g,
            }
            for g in (global_prof.get("gestures", []) if global_prof else [])
        ]

        return _ok({
            "version": "3.0.0",
            "view": resolved_view,
            "ptp_detected": True,
            "translations": translations,
            "general": settings,
            "license": self._build_license_info(),
            "profiles": profiles,
            "gestures": gestures,
            "reference_shortcuts": ref_shortcuts,
        })

    def save_general_settings(self, patch: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(patch, dict):
            return _err("INVALID_PAYLOAD", "save_general_settings", "patch must be an object", "patch")
        engine = patch.get("ui_engine")
        if engine is not None and engine not in ("webview", "tkinter"):
            return _err("INVALID_UI_ENGINE", "save_general_settings", "ui_engine must be webview or tkinter", "ui_engine")

        current = self._load_app_settings()
        current.update(patch)

        if "language" in patch:
            set_language(str(patch["language"]))

        self._save_app_settings(current)
        lang = str(current.get("language") or "vi")
        translations, ref_shortcuts = self._build_i18n_payload(lang)
        return _ok({
            **current,
            "available_languages": [code for code, _ in SUPPORTED_LANGUAGES],
            "language_options": [{"code": code, "name": name} for code, name in SUPPORTED_LANGUAGES],
            "translations": translations,
            "reference_shortcuts": ref_shortcuts,
            "license": self._build_license_info(),
        })

    def save_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(profile, dict) or not str(profile.get("id") or "").strip():
            return _err("INVALID_PROFILE", "save_profile", "profile.id is required", "id")
        doc = self._load_profiles_doc()
        profiles = doc.get("profiles", [])
        norm = _normalize_profile_v4(profile)
        idx = next((i for i, p in enumerate(profiles) if p.get("id") == norm["id"]), -1)
        if idx >= 0:
            profiles[idx] = norm
        else:
            profiles.append(norm)
        doc["profiles"] = profiles
        return _ok(self._save_profiles_doc(doc))

    def delete_profile(self, profile_id: str) -> dict[str, Any]:
        if not profile_id or profile_id == "global":
            return _err("CANNOT_DELETE_GLOBAL", "delete_profile", "Global profile cannot be deleted", "profile_id")
        doc = self._load_profiles_doc()
        doc["profiles"] = [p for p in doc.get("profiles", []) if p.get("id") != profile_id]
        return _ok(self._save_profiles_doc(doc))

    def save_profile_gestures(self, profile_id: str, gestures: list[dict[str, Any]]) -> dict[str, Any]:
        if not profile_id or not isinstance(gestures, list):
            return _err("INVALID_GESTURES", "save_profile_gestures", "profile_id and gestures list required")
        doc = self._load_profiles_doc()
        profiles = doc.get("profiles", [])
        target = next((p for p in profiles if p.get("id") == profile_id), None)
        if target is None:
            return _err("PROFILE_NOT_FOUND", "save_profile_gestures", f"Profile '{profile_id}' not found")
        target["gestures"] = sort_gestures(gestures)
        return _ok(self._save_profiles_doc(doc))

    def save_profile_commands(self, profile_id: str, commands: list[dict[str, Any]]) -> dict[str, Any]:
        if not profile_id or not isinstance(commands, list):
            return _err("INVALID_COMMANDS", "save_profile_commands", "profile_id and commands list required")
        doc = self._load_profiles_doc()
        profiles = doc.get("profiles", [])
        target = next((p for p in profiles if p.get("id") == profile_id), None)
        if target is None:
            return _err("PROFILE_NOT_FOUND", "save_profile_commands", f"Profile '{profile_id}' not found")
        target["commands"] = list(commands)
        return _ok(self._save_profiles_doc(doc))

    def capture_key_combo(self, timeout_sec: float = 6.0) -> dict[str, Any]:
        return capture_next_key_combo(timeout_sec=timeout_sec)

    def get_installed_applications(self) -> dict[str, Any]:
        try:
            return _ok(get_installed_apps())
        except Exception as exc:
            return _err("APP_DISCOVERY_FAILED", "get_installed_applications", str(exc))

    def search_webclips(self, query: str = "") -> dict[str, Any]:
        try:
            return _ok(search_webclip_templates(query))
        except Exception as exc:
            return _err("WEBCLIP_SEARCH_FAILED", "search_webclips", str(exc))

    def simulate_license(self, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        svc = get_license_service()
        payload = payload or {}
        if action == "expire":
            return _ok(svc.simulate_expire_trial())
        elif action == "reset":
            return _ok(svc.reset_trial())
        elif action == "activate_dev_pro":
            svc.activate_dev_pro()
            return _ok(svc.get_status())
        elif action == "set_remaining":
            return _ok(svc.simulate_set_remaining(
                hours=int(payload.get("hours", 0)),
                minutes=int(payload.get("minutes", 0)),
                seconds=int(payload.get("seconds", 0)),
            ))
        return _err("INVALID_SIMULATION_ACTION", "simulate_license", f"Unknown action: {action}")

    def discover_apps(self) -> dict[str, Any]:
        return self.get_installed_applications()

    def record_key_combo(self, timeout_sec: float = 6.0) -> dict[str, Any]:
        return self.capture_key_combo(timeout_sec=timeout_sec)

    def get_webclip_templates(self, query: str = "") -> dict[str, Any]:
        return self.search_webclips(query=query)

    def search_intents(self, query: str = "", lang: str | None = None) -> dict[str, Any]:
        try:
            from src.features.shortcut_panel.services.intent_service import IntentService
            resolved_lang = lang or get_language()
            items = IntentService().search(query, limit=15)
            return _ok([
                {
                    "intent_id": item.intent_id,
                    "title": item.get_title(resolved_lang),
                    "keys": item.keys,
                    "category": item.category,
                    "description": item.description,
                }
                for item in items
            ])
        except Exception as exc:
            return _err("SEARCH_INTENTS_FAILED", "search_intents", str(exc))

    def save_gesture_binding(self, binding: dict[str, Any], profile_id: str = "global") -> dict[str, Any]:
        doc = self._load_profiles_doc()
        profiles = doc.get("profiles", [])
        prof = next((p for p in profiles if p.get("id") == profile_id), None)
        if prof is None:
            return _err("PROFILE_NOT_FOUND", "save_gesture_binding", f"Profile '{profile_id}' not found")
        entries = prof.get("gestures", [])
        bk = binding_key_for(binding)
        entries = [g for g in entries if binding_key_for(g) != bk]
        entries.append(binding)
        prof["gestures"] = sort_gestures(entries)
        doc["profiles"] = profiles
        self._save_profiles_doc(doc)
        return _ok(prof["gestures"])

    def run_system_action(self, action: str, payload: Any = None) -> dict[str, Any]:
        if action == "copy_diagnostics":
            from src.core.crash_reporter import copy_diagnostic_to_clipboard
            return _ok({"copied": bool(copy_diagnostic_to_clipboard())})
        if action == "open_logs":
            from src.core.crash_reporter import open_crash_logs_folder
            return _ok({"opened": bool(open_crash_logs_folder())})
        if action == "restart_app":
            import os, subprocess
            env = os.environ.copy()
            for k in list(env.keys()):
                if k == "_MEIPASS2" or k.startswith("_PYI_"):
                    env.pop(k, None)
            env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
            args_str = " ".join(f'"{a}"' for a in sys.argv[1:])
            cmd = f'ping 127.0.0.1 -n 2 > nul & "{sys.executable}" {args_str}'.strip()
            subprocess.Popen(
                cmd,
                shell=True,
                env=env,
                creationflags=0x00000008 | 0x00000200,
                close_fds=True,
            )
            if self._window is not None:
                try:
                    self._window.destroy()
                except Exception:
                    pass
            sys.exit(0)
        if action == "check_license":
            get_license_service().verify_store_license()
            return _ok(self._build_license_info())
        if action == "buy_license":
            purchased = bool(get_license_service().purchase_pro())
            return _ok({"purchased": purchased, "license": self._build_license_info()})
        if action == "simulate_expire_trial":
            get_license_service().simulate_expire_trial()
            return _ok(self._build_license_info())
        if action == "reset_trial":
            get_license_service().reset_trial()
            return _ok(self._build_license_info())
        if action == "simulate_countdown":
            p = payload if isinstance(payload, dict) else {}
            h = int(p.get("hours", 0))
            m = int(p.get("minutes", 1))
            s = int(p.get("seconds", 0))
            get_license_service().simulate_set_remaining(hours=h, minutes=m, seconds=s)
            return _ok(self._build_license_info())
        if action == "get_license_countdown":
            return _ok(self._build_license_info())
        return _err("UNKNOWN_SYSTEM_ACTION", "run_system_action", f"Unsupported action: {action}", "action")

    def complete_onboarding(self) -> dict[str, Any]:
        current = self._load_app_settings()
        current["onboarding_completed"] = True
        current["show_welcome"] = False
        self._save_app_settings(current)
        return _ok({"completed": True})

    def open_view(self, view: str) -> dict[str, Any]:
        if view not in ("settings", "welcome", "wizard"):
            return _err("INVALID_VIEW", "open_view", f"Unsupported view: {view}", "view")
        if self._window is not None:
            bundle = _resolve_ui_index_url(view)
            if bundle:
                try:
                    self._window.load_url(bundle)
                except Exception:
                    pass
        return _ok({"view": view})

    def close_window(self) -> dict[str, Any]:
        if self._window is not None:
            try:
                self._window.destroy()
            except Exception:
                pass
        return _ok({"closed": True})


def resolve_ui_index_path() -> Path | None:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)) / "ui_dist"
    else:
        base = Path(__file__).resolve().parents[2] / "ui_dist"
    index_file = base / "index.html"
    return index_file if index_file.exists() else None


def _resolve_ui_index_url(view: str) -> str | None:
    index_file = resolve_ui_index_path()
    if index_file is None:
        return None
    return f"{index_file.as_uri()}?view={view}"
