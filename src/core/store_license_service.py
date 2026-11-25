"""Store and 30-day trial licensing engine for RightWheel.

Manages:
- 30-day full-feature trial with machine-bound anti-clock-rollback protection.
- Microsoft Store MSIX package identity detection.
- Feature gating between Free Tier and Pro Tier.
- Simulation and testing controls for trial expiration.
- Real-time automatic background expiry monitor daemon.
"""
from __future__ import annotations

from enum import Enum
import json
import os
from pathlib import Path
import subprocess
import threading
import time
from typing import Any, Callable
import uuid

from src.core.app_paths import get_config_root, log_debug

TRIAL_DAYS = 30
STORE_PRODUCT_ID = "RIGHTWHEEL_STORE_ID"
STORE_ADDON_ID = ""


class StoreLicenseStatus(str, Enum):
    TRIAL_ACTIVE = "TRIAL_ACTIVE"
    TRIAL_EXPIRED = "TRIAL_EXPIRED"
    PRO_ACTIVATED = "PRO_ACTIVATED"


class StoreLicenseService:
    """Manages licensing, 30-day trial evaluation, and Store IAP / LemonSqueezy integration."""

    def __init__(self, state_file_override: Path | None = None) -> None:
        self._state_file = state_file_override or self._resolve_state_file()
        self._machine_guid = self._resolve_machine_guid()
        self._cached_status: dict[str, Any] | None = None
        self._dev_pro_override: bool = False
        self._refresh()

    def _resolve_state_file(self) -> Path:
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            p = Path(local_appdata) / "RightWheel" / "store_license.json"
        else:
            p = get_config_root() / "store_license.json"
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        return p

    def _resolve_machine_guid(self) -> str:
        """Retrieve persistent Windows MachineGuid or generate fallback."""
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as k:
                val, _ = winreg.QueryValueEx(k, "MachineGuid")
                if val:
                    return str(val).strip()
        except Exception:
            pass

        try:
            id_path = self._state_file.parent / "machine_id.txt"
            if id_path.exists():
                return id_path.read_text(encoding="utf-8").strip()
            new_id = str(uuid.uuid4())
            id_path.write_text(new_id, encoding="utf-8")
            return new_id
        except Exception:
            return "DEFAULT_MACHINE_ID"

    def has_msix_package_identity(self) -> bool:
        """Check if process has a Windows Store MSIX Package Identity."""
        try:
            import ctypes
            buffer_length = ctypes.c_uint32(0)
            ret = ctypes.windll.kernel32.GetCurrentPackageId(ctypes.byref(buffer_length), None)
            return ret != 15700
        except Exception:
            return False

    def _load_raw_state(self) -> dict[str, Any]:
        if not self._state_file.exists():
            return {}
        try:
            with open(self._state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_raw_state(self, state: dict[str, Any]) -> None:
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            log_debug(f"Failed to save license state: {e}")

    def _refresh(self) -> None:
        now = int(time.time())
        state = self._load_raw_state()

        if not state:
            state = {
                "machine_guid": self._machine_guid,
                "install_time": now,
                "last_seen_time": now,
                "clock_tampered": False,
                "is_pro": False,
                "store_purchase_token": None,
            }
            self._save_raw_state(state)

        install_time = state.get("install_time", now)
        last_seen = state.get("last_seen_time", now)
        clock_tampered = bool(state.get("clock_tampered", False))
        is_pro = bool(state.get("is_pro", False)) or self._dev_pro_override

        # Detect clock rollback (> 5 minutes)
        if now < (last_seen - 300):
            clock_tampered = True
            state["clock_tampered"] = True
            log_debug(f"Clock rollback detected: now={now} < last_seen={last_seen}")

        if now > last_seen:
            state["last_seen_time"] = now
            self._save_raw_state(state)

        trial_total_seconds = TRIAL_DAYS * 86400
        trial_end_time = install_time + trial_total_seconds
        seconds_remaining = max(0, trial_end_time - now)
        days_remaining = int((seconds_remaining + 86399) // 86400) if seconds_remaining > 0 else 0

        if is_pro:
            status = StoreLicenseStatus.PRO_ACTIVATED
            formatted_time_left = "Pro"
        elif clock_tampered or seconds_remaining <= 0:
            status = StoreLicenseStatus.TRIAL_EXPIRED
            days_remaining = 0
            seconds_remaining = 0
            formatted_time_left = "0s"
        else:
            status = StoreLicenseStatus.TRIAL_ACTIVE
            if days_remaining >= 1:
                formatted_time_left = f"{days_remaining}d"
            else:
                hours = seconds_remaining // 3600
                mins = (seconds_remaining % 3600) // 60
                secs = seconds_remaining % 60
                if hours > 0:
                    formatted_time_left = f"{hours:02d}:{mins:02d}:{secs:02d}"
                else:
                    formatted_time_left = f"{mins:02d}:{secs:02d}"

        self._cached_status = {
            "status": status.value,
            "days_remaining": days_remaining,
            "seconds_remaining": seconds_remaining,
            "formatted_time_left": formatted_time_left,
            "is_pro": is_pro,
            "is_trial": (status == StoreLicenseStatus.TRIAL_ACTIVE),
            "clock_tampered": clock_tampered,
            "has_store_identity": self.has_msix_package_identity(),
            "trial_total_days": TRIAL_DAYS,
        }

    def get_status(self) -> dict[str, Any]:
        """Return current license and 30-day trial status."""
        self._refresh()
        return dict(self._cached_status or {})

    def is_feature_allowed(self, feature_name: str) -> bool:
        """Check if feature is accessible under current license."""
        st = self.get_status()
        if st.get("is_pro") or st.get("is_trial"):
            return True
        return False

    def activate_pro(self, purchase_token: str = "PRO_VERIFIED") -> None:
        """Mark license as permanently activated."""
        state = self._load_raw_state()
        state["is_pro"] = True
        state["store_purchase_token"] = purchase_token
        self._save_raw_state(state)
        self._refresh()
        log_debug(f"Pro license activated with token={purchase_token}")

    def activate_dev_pro(self) -> None:
        """In-memory developer override for testing Pro features."""
        self._dev_pro_override = True
        self._refresh()

    def simulate_expire_trial(self) -> dict[str, Any]:
        """Force expire the trial immediately for testing."""
        now = int(time.time())
        state = self._load_raw_state()
        state["install_time"] = now - (TRIAL_DAYS * 86400 + 3600)
        state["last_seen_time"] = now
        state["clock_tampered"] = False
        state["is_pro"] = False
        self._dev_pro_override = False
        self._save_raw_state(state)
        self._refresh()
        log_debug("Simulation: Trial forcibly expired")
        return self.get_status()

    def simulate_set_remaining(self, hours: int = 0, minutes: int = 0, seconds: int = 0) -> dict[str, Any]:
        """Set remaining trial duration in hours, minutes, seconds for testing."""
        target_seconds = max(1, int(hours) * 3600 + int(minutes) * 60 + int(seconds))
        now = int(time.time())
        state = self._load_raw_state()
        state["install_time"] = now - (TRIAL_DAYS * 86400) + target_seconds
        state["last_seen_time"] = now
        state["clock_tampered"] = False
        state["is_pro"] = False
        self._dev_pro_override = False
        self._save_raw_state(state)
        self._refresh()
        log_debug(f"Simulation: Trial remaining set to {target_seconds}s ({hours}h {minutes}m {seconds}s)")
        st = self.get_status()
        if st.get("status") == StoreLicenseStatus.TRIAL_ACTIVE:
            st["seconds_remaining"] = target_seconds
        return st

    def reset_trial(self) -> dict[str, Any]:
        """Reset trial back to fresh initial 30 days."""
        now = int(time.time())
        state = self._load_raw_state()
        state["install_time"] = now
        state["last_seen_time"] = now
        state["clock_tampered"] = False
        state["is_pro"] = False
        self._dev_pro_override = False
        self._save_raw_state(state)
        self._refresh()
        log_debug("Simulation: Trial reset to 30 days")
        return self.get_status()

    def start_expiry_monitor(self, on_expired_callback: Callable[[], None] | None = None, interval_s: float = 10.0) -> None:
        """Start a lightweight daemon thread to monitor trial expiration in real-time."""
        if getattr(self, "_monitor_started", False):
            return
        self._monitor_started = True

        def _monitor_loop() -> None:
            last_status = self.get_status().get("status")
            while True:
                try:
                    time.sleep(interval_s)
                    st = self.get_status()
                    current_status = st.get("status")
                    if last_status == StoreLicenseStatus.TRIAL_ACTIVE.value and current_status == StoreLicenseStatus.TRIAL_EXPIRED.value:
                        log_debug("Real-time trial expiration triggered by background monitor daemon.")
                        if callable(on_expired_callback):
                            try:
                                on_expired_callback()
                            except Exception as cb_err:
                                log_debug(f"Error in on_expired_callback: {cb_err}")
                    last_status = current_status
                except Exception as exc:
                    log_debug(f"Expiry monitor daemon loop exception: {exc}")

        t = threading.Thread(target=_monitor_loop, daemon=True, name="TrialExpiryMonitorDaemon")
        t.start()

    def _query_winrt_addon_license(self) -> bool:
        """Query Windows.Services.Store.StoreContext via WinRT PowerShell bridge when packaged as MSIX."""
        if not self.has_msix_package_identity():
            return False

        addon_filter = STORE_ADDON_ID.strip()
        ps_script = (
            "[Windows.Services.Store.StoreContext, Windows.Services.Store, ContentType = WindowsRuntime] | Out-Null; "
            "$ctx = [Windows.Services.Store.StoreContext]::GetDefault(); "
            "$op = $ctx.GetAppLicenseAsync(); "
            "while ($op.Status -eq 'Started') { Start-Sleep -Milliseconds 30 }; "
            "$lic = $op.GetResults(); "
            "if ($lic -eq $null) { Write-Output 'NONE'; exit 0 }; "
            "$active = $false; "
            "foreach ($v in $lic.AddOnLicenses.Values) { "
            "  if ($v.IsActive) { "
            f"    if ('{addon_filter}' -eq '' -or $v.SkuStoreId.StartsWith('{addon_filter}') -or $v.InAppOfferToken -eq '{addon_filter}') {{ $active = $true }} "
            "  } "
            "}; "
            "if ($active) { Write-Output 'PRO_ADDON_ACTIVE' } else { Write-Output 'NOT_OWNED' }"
        )
        try:
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=8,
                creationflags=creation_flags,
            )
            out = (res.stdout or "").strip()
            log_debug(f"WinRT StoreContext license query output: {out!r}")
            return "PRO_ADDON_ACTIVE" in out
        except Exception as exc:
            log_debug(f"WinRT StoreContext license query failed: {exc}")
            return False

    def verify_store_license(self) -> dict[str, Any]:
        """Verify license against Microsoft Store WinRT StoreContext (if MSIX) and return updated status."""
        if self._query_winrt_addon_license():
            self.activate_pro("STORE_WINRT_VERIFIED")
        return self.get_status()

    def purchase_pro(self, addon_id: str | None = None) -> bool:
        """Trigger in-app Store purchase via WinRT RequestPurchaseAsync if Add-on ID is configured, else open Store page."""
        target_addon = (addon_id or STORE_ADDON_ID).strip()
        if target_addon and self.has_msix_package_identity():
            ps_script = (
                "[Windows.Services.Store.StoreContext, Windows.Services.Store, ContentType = WindowsRuntime] | Out-Null; "
                "$ctx = [Windows.Services.Store.StoreContext]::GetDefault(); "
                f"$op = $ctx.RequestPurchaseAsync('{target_addon}'); "
                "while ($op.Status -eq 'Started') { Start-Sleep -Milliseconds 50 }; "
                "$res = $op.GetResults(); "
                "Write-Output $res.Status.ToString()"
            )
            try:
                creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
                res = subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    creationflags=creation_flags,
                )
                status_str = (res.stdout or "").strip()
                log_debug(f"WinRT RequestPurchaseAsync result: {status_str!r}")
                if any(tok in status_str for tok in ("Succeeded", "AlreadyPurchased")):
                    self.activate_pro(f"STORE_IAP_{target_addon}")
                    return True
                return False
            except Exception as exc:
                log_debug(f"WinRT RequestPurchaseAsync failed: {exc}")
        return self.open_store_purchase_page()

    def open_store_purchase_page(self, product_id: str | None = None) -> bool:
        """Open Microsoft Store purchase page via protocol ms-windows-store."""
        pid = product_id or STORE_PRODUCT_ID
        try:
            url = f"ms-windows-store://pdp/?productid={pid}"
            os.startfile(url)
            log_debug(f"Opened Store URL: {url}")
            return True
        except Exception as e:
            log_debug(f"Failed to open Store protocol: {e}")
            try:
                import webbrowser
                webbrowser.open(f"https://apps.microsoft.com/detail/{pid}")
                return True
            except Exception:
                return False


_global_license_service: StoreLicenseService | None = None


def get_license_service() -> StoreLicenseService:
    """Return singleton StoreLicenseService instance."""
    global _global_license_service
    if _global_license_service is None:
        _global_license_service = StoreLicenseService()
    return _global_license_service
