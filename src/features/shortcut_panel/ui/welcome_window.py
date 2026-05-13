"""Welcome / onboarding screen — shown on every launch."""
from __future__ import annotations

import tkinter as tk

from ..services import startup_service
from features.i18n import t, ui_font

_TOP = "#f5f5f5"
_BG  = "#141414"
_BG2 = "#1e1e1e"
_FG  = "#bbbbbb"
_ACC = "#0078d4"

# (icon, trigger-key, desc-key)
_FEATURE_KEYS = [
    ("🖱", "welcome.f1.trigger", "welcome.f1.desc"),
    ("⌨", "welcome.f2.trigger", "welcome.f2.desc"),
    ("🚀", "welcome.f3.trigger", "welcome.f3.desc"),
    ("🌐", "welcome.f4.trigger", "welcome.f4.desc"),
    ("📁", "welcome.f5.trigger", "welcome.f5.desc"),
    ("◈",  "welcome.f6.trigger", "welcome.f6.desc"),
    ("⚙",  "welcome.f7.trigger", "welcome.f7.desc"),
    ("▶",  "welcome.f8.trigger", "welcome.f8.desc"),
]


def show_welcome(root: tk.Tk) -> None:
    """Show welcome Toplevel and block until closed. Shows every launch."""
    font = ui_font()
    win = tk.Toplevel(root)
    win.title(t("welcome.title"))
    win.configure(bg=_BG)
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.grab_set()

    sv = tk.BooleanVar(win, value=False)

    # ── top section (light) ────────────────────────────────────────────────
    top = tk.Frame(win, bg=_TOP)
    top.pack(fill="x")
    tk.Label(top, text="🖱", bg=_TOP,
             font=("Segoe UI Emoji", 36)).pack(pady=(22, 4))
    tk.Label(top, text=t("app.name"), bg=_TOP, fg="#111111",
             font=(font, 20, "bold")).pack()
    tk.Label(top, text=t("app.tagline"),
             bg=_TOP, fg="#666", font=(font, 10)).pack(pady=(2, 6))
    tk.Label(top, text=t("app.subtitle"),
             bg=_TOP, fg="#555", font=(font, 9),
             justify="center").pack(pady=(0, 14))

    # divider
    tk.Frame(win, bg="#dddddd", height=1).pack(fill="x")

    # ── dark section (features) ────────────────────────────────────────────
    card = tk.Frame(win, bg=_BG2)
    card.pack(fill="x", padx=22, pady=12)
    for icon, trig_key, desc_key in _FEATURE_KEYS:
        row = tk.Frame(card, bg=_BG2)
        row.pack(fill="x", padx=14, pady=4)
        tk.Label(row, text=icon, bg=_BG2, fg="white",
                 font=("Segoe UI Emoji", 11), width=3).pack(side="left")
        tk.Label(row, text=t(trig_key), bg=_BG2, fg=_ACC,
                 font=(font, 10, "bold"), width=22,
                 anchor="w").pack(side="left")
        tk.Label(row, text=t(desc_key), bg=_BG2, fg=_FG,
                 font=(font, 10), anchor="w").pack(side="left")

    # startup checkbox
    tk.Checkbutton(win, text=f"  {t('welcome.run_on_startup')}",
                   variable=sv, bg=_BG, fg=_FG, activebackground=_BG,
                   selectcolor=_BG2, font=(font, 10),
                   cursor="hand2").pack(pady=(10, 2))

    # Get Started button
    def _close() -> None:
        (startup_service.enable if sv.get() else startup_service.disable)()
        win.destroy()

    tk.Button(win, text=f"   {t('welcome.get_started')}   ", command=_close,
              bg=_ACC, fg="white", font=(font, 12, "bold"),
              relief="flat", cursor="hand2",
              activebackground="#005fa3").pack(
              fill="x", padx=36, ipady=10, pady=(6, 20))

    # ── center & auto-size ─────────────────────────────────────────────────
    win.update_idletasks()
    w = max(win.winfo_reqwidth(), 480)
    h = max(win.winfo_reqheight(), 420)
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
    win.protocol("WM_DELETE_WINDOW", _close)
    root.wait_window(win)
