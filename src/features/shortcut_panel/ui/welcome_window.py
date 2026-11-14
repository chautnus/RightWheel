"""Welcome / onboarding screen — shown on launch with unified Zinc dark theme."""
from __future__ import annotations

import os
import sys
import tkinter as tk

from ..services import startup_service
from . import theme
from features.i18n import t, ui_font


def _asset_path(rel: str) -> str:
    """Resolve path to a bundled asset (works both frozen and from source)."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        # src/features/shortcut_panel/ui/ → project root is 4 levels up
        base = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    return os.path.normpath(os.path.join(base, rel))


_BG         = theme.BG_WINDOW
_HEADER_BG  = theme.BG_SIDEBAR
_CARD_BG    = theme.BG_CARD
_BORDER     = theme.BORDER_SUBTLE
_FG_PRIMARY = theme.FG_PRIMARY
_FG_MUTED   = theme.FG_MUTED
_ACC        = theme.ACCENT_BLUE

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
    """Show welcome Toplevel and block until closed. Shows on launch."""
    font = ui_font()
    win = tk.Toplevel(root)
    win.title(t("welcome.title"))
    win.configure(bg=_BG)
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.grab_set()

    sv = tk.BooleanVar(win, value=True)  # pre-checked: default startup enabled

    # ── Top header section (Sleek Zinc dark header) ─────────────────────────
    top = tk.Frame(win, bg=_HEADER_BG)
    top.pack(fill="x")

    # Mouse icon — PNG preferred; fallback text if PIL unavailable
    try:
        from PIL import Image, ImageTk
        img = Image.open(_asset_path("assets/icon.png")).convert("RGBA")
        img = img.resize((64, 64), Image.LANCZOS)
        _icon_img = ImageTk.PhotoImage(img)  # keep reference to avoid GC
        icon_lbl = tk.Label(top, image=_icon_img, bg=_HEADER_BG)
        icon_lbl._icon_img = _icon_img       # pin reference on widget
        icon_lbl.pack(pady=(18, 4))
    except Exception:
        tk.Label(top, text="RightWheel", bg=_HEADER_BG, fg=_FG_PRIMARY,
                 font=(font, 16, "bold")).pack(pady=(20, 4))

    tk.Label(top, text=t("app.name"), bg=_HEADER_BG, fg=_FG_PRIMARY,
             font=(font, 18, "bold")).pack()
    tk.Label(top, text=t("app.tagline"),
             bg=_HEADER_BG, fg=_FG_MUTED, font=(font, 10)).pack(pady=(2, 4))
    tk.Label(top, text=t("app.subtitle"),
             bg=_HEADER_BG, fg=_FG_MUTED, font=(font, 9),
             justify="center").pack(pady=(0, 16))

    # 1px Subtle divider
    tk.Frame(win, bg=_BORDER, height=1).pack(fill="x")

    # ── Features section (Refined Card container) ───────────────────────────
    card_wrap = tk.Frame(win, bg=_BORDER, padx=1, pady=1)
    card_wrap.pack(fill="x", padx=20, pady=14)

    card = tk.Frame(card_wrap, bg=_CARD_BG)
    card.pack(fill="x", padx=0, pady=0)

    for _, trig_key, desc_key in _FEATURE_KEYS:
        row = tk.Frame(card, bg=_CARD_BG)
        row.pack(fill="x", padx=12, pady=3)
        tk.Label(row, text="•", bg=_CARD_BG, fg=_ACC,
                 font=(font, 10, "bold"), width=2).pack(side="left")
        tk.Label(row, text=t(trig_key), bg=_CARD_BG, fg=_ACC,
                 font=(font, 10, "bold"), width=22,
                 anchor="w").pack(side="left")
        tk.Label(row, text=t(desc_key), bg=_CARD_BG, fg=theme.FG_SECONDARY,
                 font=(font, 9), anchor="w").pack(side="left")

    # Startup checkbox
    tk.Checkbutton(win, text=f"  {t('welcome.run_on_startup')}",
                   variable=sv, bg=_BG, fg=_FG_MUTED, activebackground=_BG,
                   activeforeground=_FG_PRIMARY, selectcolor=_CARD_BG,
                   font=(font, 9), cursor="hand2").pack(pady=(6, 4))

    # Single primary action: Get Started button
    def _close() -> None:
        (startup_service.enable if sv.get() else startup_service.disable)()
        win.destroy()

    tk.Button(win, text=f"  {t('welcome.get_started')}  ", command=_close,
              bg=_ACC, fg="white", font=(font, 11, "bold"),
              relief="flat", cursor="hand2",
              activebackground="#005fa3", activeforeground="white").pack(
              fill="x", padx=32, ipady=8, pady=(4, 18))

    # ── Center & auto-size ──────────────────────────────────────────────────
    win.update_idletasks()
    w = max(win.winfo_reqwidth(), 480)
    h = max(win.winfo_reqheight(), 440)
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
    win.protocol("WM_DELETE_WINDOW", _close)
    root.wait_window(win)
