"""Design tokens and unified Zinc theme palette for RightWheel UI.

Following modern product design standards (WCAG AA compliant, Zinc dark scale).
"""
from __future__ import annotations

# ── Surface & Background Tokens ──────────────────────────────────────────
BG_WINDOW      = "#09090b"  # Zinc 950: Main outer window / root background
BG_SIDEBAR     = "#121214"  # Zinc 925: Navigation sidebar background
BG_CONTENT     = "#18181b"  # Zinc 900: Content frames and panel body
BG_CARD        = "#1e1e24"  # Zinc 875: Cards, sub-panels, list containers
BG_CARD_HOVER  = "#27272a"  # Zinc 800: Hovered / selected item background
BG_ACTIVE      = "#27272a"  # Zinc 800: Active navigation tab

# ── Border & Divider Tokens ──────────────────────────────────────────────
BORDER_SUBTLE  = "#27272a"  # Zinc 800: Subtle 1px dividers and card borders
BORDER_INPUT   = "#3f3f46"  # Zinc 700: Input field and control borders
BORDER_FOCUS   = "#0078d4"  # Accent ring for focused elements

# ── Typography & Foreground Tokens ───────────────────────────────────────
FG_PRIMARY     = "#fafafa"  # Zinc 50: Headings, active labels, primary text
FG_SECONDARY   = "#d4d4d8"  # Zinc 300: Regular body text and item titles
FG_MUTED       = "#a1a1aa"  # Zinc 400: Subtitles, metadata (WCAG AA 4.5:1+)
FG_DISABLED    = "#71717a"  # Zinc 500: Disabled controls and placeholders

# ── Accent & Semantic Action Tokens ──────────────────────────────────────
ACCENT_BLUE    = "#0078d4"  # Windows blue accent / Primary action button
COLOR_DANGER   = "#ef4444"  # Red 500: Destructive actions and error messages
COLOR_SUCCESS  = "#16825d"  # Green 700: Save feedback and active indicators
COLOR_WARNING  = "#f59e0b"  # Amber 500: Warning alerts and restart hints

# ── Kbd Badge Tokens (Raycast-Style Shortcuts) ───────────────────────────
KBD_BG         = "#1e1e24"  # Kbd badge background
KBD_BG_SEL     = "#383842"  # Selected kbd badge background
KBD_BORDER     = "#3f3f46"  # Kbd badge border
KBD_BORDER_SEL = "#6366f1"  # Selected kbd badge accent border
KBD_FG         = "#a1a1aa"  # Kbd badge text
KBD_FG_SEL     = "#ffffff"  # Selected kbd badge text
