"""License state types for RightWheel."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LicenseState(Enum):
    TRIAL_ACTIVE    = "trial_active"     # within 30-day trial
    TRIAL_EXPIRED   = "trial_expired"    # trial over, not activated
    ACTIVE          = "active"           # valid license, within update year
    UPDATES_EXPIRED = "updates_expired"  # license valid; update year ended
    INVALID         = "invalid"          # bad / revoked key


# Badge colors per state (labels come from i18n via t())
_STATE_COLOR: dict[LicenseState, str] = {
    LicenseState.TRIAL_ACTIVE:    "#b8860b",
    LicenseState.TRIAL_EXPIRED:   "#c0392b",
    LicenseState.ACTIVE:          "#16825d",
    LicenseState.UPDATES_EXPIRED: "#0078d4",
    LicenseState.INVALID:         "#c0392b",
}


def state_label(s: LicenseState) -> str:
    from features.i18n import t
    return t(f"lic.state.{s.value}")


def state_color(s: LicenseState) -> str:
    return _STATE_COLOR[s]


@dataclass
class LicenseInfo:
    state:          LicenseState = LicenseState.TRIAL_ACTIVE
    key:            str = ""
    instance_id:    str = ""
    email:          str = ""
    expires_at:     str = ""   # ISO date — end of update period (empty = perpetual)
    first_run:      str = ""   # ISO date — when trial started
    days_remaining: int = 30   # trial days left (only meaningful in TRIAL_ACTIVE)
    last_validated: str = ""   # ISO datetime of last successful API validation
