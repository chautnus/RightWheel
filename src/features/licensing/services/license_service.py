"""LemonSqueezy license activation, validation, and local cache."""
from __future__ import annotations

import getpass
import json
import os
import socket
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..types.license_types import LicenseInfo, LicenseState

# ── Configuration — replace with your LemonSqueezy values ─────────────────────
STORE_BUY_URL  = "https://imagesnap.lemonsqueezy.com/checkout/buy/121b3bd5-3464-4e73-9ead-70b0034ec124"
_LS_API        = "https://api.lemonsqueezy.com/v1/licenses"
TRIAL_DAYS     = 30
_CACHE_DAYS    = 7      # re-validate online every N days

_CONFIG_DIR    = Path(os.environ.get("APPDATA", ".")) / "RightWheel"
_LICENSE_PATH  = _CONFIG_DIR / "license.json"
_INSTANCE_NAME = f"{socket.gethostname()}-{getpass.getuser()}"


# ── local persistence ──────────────────────────────────────────────────────────

def _load() -> dict:
    try:
        return json.loads(_LICENSE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _LICENSE_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── API helpers ────────────────────────────────────────────────────────────────

def _post(endpoint: str, body: dict) -> dict:
    """POST to LemonSqueezy license API. Raises urllib.error.URLError on failure."""
    data = json.dumps(body).encode()
    req  = urllib.request.Request(
        f"{_LS_API}/{endpoint}", data=data, method="POST",
        headers={"Accept": "application/json",
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


# ── public API ─────────────────────────────────────────────────────────────────

def get_info() -> LicenseInfo:
    """Return current license state. Never raises — falls back to trial/invalid."""
    data = _load()

    # ── no license key ─────────────────────────────────────────────────────────
    if not data.get("license_key"):
        first_run = data.get("first_run", _now_iso())
        if not data.get("first_run"):
            data["first_run"] = first_run
            _save(data)
        elapsed = (datetime.now(timezone.utc)
                   - datetime.fromisoformat(first_run)).days
        remaining = max(0, TRIAL_DAYS - elapsed)
        state = (LicenseState.TRIAL_ACTIVE
                 if remaining > 0 else LicenseState.TRIAL_EXPIRED)
        return LicenseInfo(state=state, first_run=first_run,
                           days_remaining=remaining)

    # ── has license key — use cache if fresh ───────────────────────────────────
    last_val = data.get("last_validated", "")
    cache_ok = False
    if last_val:
        age = (datetime.now(timezone.utc)
               - datetime.fromisoformat(last_val)).days
        cache_ok = age < _CACHE_DAYS

    if cache_ok:
        return _build_info(data)

    # ── re-validate online ─────────────────────────────────────────────────────
    try:
        resp = _post("validate", {
            "license_key": data["license_key"],
            "instance_id": data.get("instance_id", ""),
        })
        if resp.get("valid"):
            data.update(_extract_meta(resp))
            data["last_validated"] = _now_iso()
            data["validated_state"] = "active"
            _save(data)
        else:
            data["validated_state"] = "invalid"
            _save(data)
    except Exception:
        pass   # offline — use stale cache

    return _build_info(data)


def activate(key: str) -> tuple[bool, str]:
    """Activate a license key. Returns (success, message)."""
    key = key.strip().upper()
    if not key:
        return False, "no_key"
    try:
        resp = _post("activate", {
            "license_key": key,
            "instance_name": _INSTANCE_NAME,
        })
    except urllib.error.HTTPError as e:
        body = json.loads(e.read()) if e.fp else {}
        msg = body.get("error", f"HTTP {e.code}")
        return False, f"connect_failed:{msg}"
    except Exception as exc:
        return False, f"connect_failed:{exc}"

    if not resp.get("activated"):
        return False, resp.get("error", "failed")

    data = _load()
    data["license_key"]    = key
    data["instance_id"]    = resp.get("instance", {}).get("id", "")
    data["last_validated"] = _now_iso()
    data["validated_state"] = "active"
    data.update(_extract_meta(resp))
    _save(data)
    return True, "success"


def deactivate() -> tuple[bool, str]:
    """Deactivate this machine's license."""
    data = _load()
    key  = data.get("license_key", "")
    iid  = data.get("instance_id", "")
    if not key:
        return False, "no_license"
    try:
        _post("deactivate", {"license_key": key, "instance_id": iid})
    except Exception:
        pass   # best-effort
    for k in ("license_key", "instance_id", "email", "expires_at",
              "last_validated", "validated_state"):
        data.pop(k, None)
    _save(data)
    return True, "deactivated"


# ── helpers ────────────────────────────────────────────────────────────────────

def _extract_meta(resp: dict) -> dict:
    lk = resp.get("license_key", {})
    return {
        "email":      resp.get("meta", {}).get("customer_email", ""),
        "expires_at": lk.get("expires_at", "") or "",
    }


def _build_info(data: dict) -> LicenseInfo:
    exp   = data.get("expires_at", "")
    state_str = data.get("validated_state", "active")
    if state_str == "invalid":
        state = LicenseState.INVALID
    elif exp:
        expired = datetime.now(timezone.utc) > datetime.fromisoformat(exp)
        state = LicenseState.UPDATES_EXPIRED if expired else LicenseState.ACTIVE
    else:
        state = LicenseState.ACTIVE
    return LicenseInfo(
        state=state,
        key=data.get("license_key", ""),
        instance_id=data.get("instance_id", ""),
        email=data.get("email", ""),
        expires_at=exp,
        first_run=data.get("first_run", ""),
        last_validated=data.get("last_validated", ""),
    )
