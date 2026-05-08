"""License tab UI — status badge, activation form, buy link."""
from __future__ import annotations

import threading
import tkinter as tk
import webbrowser

from ..services import license_service as svc
from ..types.license_types import LicenseState, state_color, state_label
from features.i18n import t, ui_font

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_SAV = "#16825d"
_RED = "#c0392b"


def _btn(p, text, cmd, bg=_ACC, w=18):
    return tk.Button(p, text=text, command=cmd, bg=bg, fg="white",
                     font=(ui_font(), 10), relief="flat",
                     padx=10, pady=5, cursor="hand2",
                     activebackground=bg, width=w)


class LicenseFrame(tk.Frame):
    """Embeddable frame — drop into any parent (notebook tab, Toplevel, etc.)."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=_BG)
        self._info = None
        self._build()
        self.refresh()

    # ── layout ────────────────────────────────────────────────────────────

    def _build(self) -> None:
        font = ui_font()

        # Status badge row
        sf = tk.Frame(self, bg=_BG2)
        sf.pack(fill="x", padx=20, pady=(20, 8))
        self._badge = tk.Label(sf, text="", bg=_BG2,
                               font=(font, 13, "bold"), pady=10)
        self._badge.pack(side="left", padx=16)
        self._sub   = tk.Label(sf, text="", bg=_BG2, fg="#888",
                               font=(font, 9))
        self._sub.pack(side="left", padx=4)

        # Key input + activate
        kf = tk.Frame(self, bg=_BG)
        kf.pack(fill="x", padx=20, pady=4)
        tk.Label(kf, text=t("lic.key_label"), bg=_BG, fg=_FG,
                 font=(font, 10)).pack(anchor="w")
        self._key_var = tk.StringVar()
        self._key_entry = tk.Entry(
            kf, textvariable=self._key_var,
            bg=_BG2, fg="#fff", insertbackground="#fff",
            font=(font, 12), relief="flat", bd=6, width=36,
        )
        self._key_entry.pack(fill="x", pady=(4, 0))
        self._key_entry.bind("<Return>", lambda _: self._do_activate())

        # Action buttons
        bf = tk.Frame(self, bg=_BG)
        bf.pack(fill="x", padx=20, pady=10)
        self._act_btn = _btn(bf, t("lic.activate"), self._do_activate, bg=_SAV)
        self._act_btn.pack(side="left", padx=(0, 8))
        _btn(bf, t("lic.buy_now"), self._do_buy, bg=_ACC).pack(side="left")
        self._deact_btn = _btn(bf, t("lic.deactivate"), self._do_deactivate,
                                bg="#555", w=14)
        self._deact_btn.pack(side="right")

        # Message label
        self._msg = tk.Label(self, text="", bg=_BG, fg=_FG,
                             font=(font, 10))
        self._msg.pack(pady=(0, 4))

        # Pricing note
        tk.Frame(self, bg="#333", height=1).pack(fill="x", padx=20, pady=8)
        tk.Label(self, text=t("lic.pricing"),
                 bg=_BG, fg="#555", font=(font, 9)).pack()

    # ── state refresh ──────────────────────────────────────────────────────

    def refresh(self) -> None:
        """Reload license state (blocking — call from tkinter thread only)."""
        self._msg.config(text=t("lic.checking"), fg="#888")
        self.update_idletasks()
        threading.Thread(target=self._load_async, daemon=True).start()

    def _load_async(self) -> None:
        info = svc.get_info()
        self.after(0, lambda: self._apply(info))

    def _apply(self, info) -> None:
        self._info = info
        color = state_color(info.state)
        self._badge.config(text=state_label(info.state), fg=color)

        # Sub-label
        if info.state == LicenseState.TRIAL_ACTIVE:
            self._sub.config(text=t("lic.days_remaining", n=info.days_remaining))
        elif info.state == LicenseState.ACTIVE:
            exp = info.expires_at[:10] if info.expires_at else t("lic.perpetual")
            self._sub.config(text=t("lic.active_sub", email=info.email, date=exp))
        elif info.state == LicenseState.UPDATES_EXPIRED:
            self._sub.config(text=t("lic.updates_sub", email=info.email))
        else:
            self._sub.config(text="")

        # Toggle controls
        activated = info.state in (LicenseState.ACTIVE, LicenseState.UPDATES_EXPIRED)
        self._key_entry.config(state="disabled" if activated else "normal")
        self._key_var.set(info.key if activated else "")
        self._act_btn.config(state="disabled" if activated else "normal")
        self._deact_btn.config(state="normal" if activated else "disabled",
                               bg=_RED if activated else "#555")
        self._msg.config(text="")

    # ── actions ────────────────────────────────────────────────────────────

    def _do_activate(self) -> None:
        key = self._key_var.get().strip()
        if not key:
            self._msg.config(text=t("lic.no_key"), fg=_RED)
            return
        self._msg.config(text=t("lic.activating"), fg="#888")
        self._act_btn.config(state="disabled")
        self.update_idletasks()

        def _run():
            ok, code = svc.activate(key)
            self.after(0, lambda: self._after_action(ok, code))

        threading.Thread(target=_run, daemon=True).start()

    def _do_deactivate(self) -> None:
        ok, code = svc.deactivate()
        msg = t(f"lic.{code}") if ok else t("lic.failed")
        self._msg.config(text=msg, fg=_SAV if ok else _RED)
        if ok:
            self.refresh()

    def _do_buy(self) -> None:
        webbrowser.open(svc.STORE_BUY_URL)

    def _after_action(self, ok: bool, code: str) -> None:
        if ok:
            msg = t("lic.success")
        elif code.startswith("connect_failed:"):
            msg = t("lic.connect_failed", msg=code.split(":", 1)[1])
        elif code == "no_key":
            msg = t("lic.no_key")
        else:
            msg = t("lic.failed")
        self._msg.config(text=msg, fg=_SAV if ok else _RED)
        if ok:
            self.refresh()
        else:
            self._act_btn.config(state="normal")
