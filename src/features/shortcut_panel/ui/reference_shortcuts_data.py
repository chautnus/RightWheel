"""Default shortcut reference data for ReferenceTab."""
from __future__ import annotations

_DEFAULT_SHORTCUTS: list[tuple[str, str, str]] = [
    # RightWheel Built-in
    ("RightWheel", "RMB + Scroll Up", "Open Shortcut Panel"),
    ("RightWheel", "RMB + Scroll Down", "Switch app (Alt+Tab)"),
    ("RightWheel", "RMB + Drag", "Draw gesture to run custom shortcut"),

    # Windows System
    ("Windows System", "Win + D", "Show/hide desktop"),
    ("Windows System", "Win + E", "Open File Explorer"),
    ("Windows System", "Win + L", "Lock PC"),
    ("Windows System", "Win + R", "Open Run dialog"),
    ("Windows System", "Win + Tab", "Task view"),
    ("Windows System", "Win + Shift + S", "Snip & Sketch screenshot"),
    ("Windows System", "Win + I", "Open Settings"),
    ("Windows System", "Win + V", "Clipboard history"),
    ("Windows System", "Win + .", "Open emoji picker"),
    ("Windows System", "Win + Pause/Break", "Open System properties"),
    ("Windows System", "Win + Ctrl + Shift + B", "Restart graphics driver"),
    ("Windows System", "Win + P", "Project to second screen"),
    ("Windows System", "Win + K", "Connect to wireless display"),
    ("Windows System", "Win + G", "Open Xbox Game Bar"),
    ("Windows System", "Win + A", "Open Quick Settings (Wi-Fi/Bluetooth/Volume)"),
    ("Windows System", "Win + N", "Open Notification Center"),
    ("Windows System", "Win + X", "Open Quick Link menu (Power User menu)"),
    ("Windows System", "Win + Number", "Launch/switch to pinned taskbar app N"),
    ("Windows System", "Win + Ctrl + D", "Create new virtual desktop"),
    ("Windows System", "Win + Ctrl + F4", "Close current virtual desktop"),
    ("Windows System", "Win + Ctrl + Left/Right", "Switch virtual desktop"),

    # Windows (Advanced)
    ("Windows (Advanced)", "Win + Shift + M", "Restore all minimized windows"),
    ("Windows (Advanced)", "Win + Home", "Minimize all windows except active window"),
    ("Windows (Advanced)", "Win + Shift + Left/Right", "Move active window to next monitor"),
    ("Windows (Advanced)", "Win + Alt + R", "Record screen with Xbox Game Bar"),
    ("Windows (Advanced)", "Win + H", "Launch voice typing / dictation"),
    ("Windows (Advanced)", "Win + W", "Open Windows Widgets board"),
    ("Windows (Advanced)", "Win + Z", "Open Snap layouts menu (Windows 11)"),
    ("Windows (Advanced)", "Win + Space", "Switch input language and keyboard layout"),
    ("Windows (Advanced)", "Win + Ctrl + Enter", "Turn on Narrator"),
    ("Windows (Advanced)", "Win + + / Win + -", "Zoom in / Zoom out with Magnifier"),
    ("Windows (Advanced)", "Win + Esc", "Close Magnifier"),
    ("Windows (Advanced)", "Win + Shift + C", "Open Copilot / Cortana"),
    ("Windows (Advanced)", "Win + T", "Cycle through apps on the taskbar"),
    ("Windows (Advanced)", "Win + B", "Set focus to the notification area / system tray"),
    ("Windows (Advanced)", "Ctrl + Shift + Win + Alt", "Open Microsoft 365 app"),
    ("Windows (Advanced)", "Win + Alt + D", "Show / hide date and time on taskbar"),
    ("Windows (Advanced)", "Win + Alt + Up/Down", "Snap window to top/bottom half"),
    ("Windows (Advanced)", "Win + /", "Start Copilot rewrite / actions"),

    # Window Management
    ("Window Management", "Win + Left/Right", "Snap window half screen"),
    ("Window Management", "Win + Up/Down", "Maximize/minimize window"),
    ("Window Management", "Alt + Tab", "Switch windows"),
    ("Window Management", "Alt + F4", "Close window"),
    ("Window Management", "Alt + Space", "Open window title bar system menu"),
    ("Window Management", "Alt + Esc", "Directly cycle windows in order opened"),

    # Browser
    ("Browser", "Ctrl + T", "New tab"),
    ("Browser", "Ctrl + W", "Close tab"),
    ("Browser", "Ctrl + Tab", "Next tab"),
    ("Browser", "Ctrl + Shift + Tab", "Previous tab"),
    ("Browser", "Ctrl + Shift + Esc", "Task Manager"),
    ("Browser", "Ctrl + R", "Reload page"),
    ("Browser", "Ctrl + Shift + R", "Hard reload page (ignore cache)"),
    ("Browser", "Ctrl + Shift + T", "Reopen last closed tab"),
    ("Browser", "Ctrl + L", "Focus address bar"),
    ("Browser", "Ctrl + N", "New window"),
    ("Browser", "Ctrl + Shift + N", "New incognito/private window"),
    ("Browser", "Ctrl + D", "Bookmark current page"),
    ("Browser", "Ctrl + H", "Open browsing history"),
    ("Browser", "Ctrl + J", "Open downloads history"),

    # File Explorer
    ("File Explorer", "Ctrl + N", "Open new Explorer window"),
    ("File Explorer", "Ctrl + Shift + N", "Create new folder"),
    ("File Explorer", "F2", "Rename selected item"),
    ("File Explorer", "Alt + Enter", "Open properties dialog"),
    ("File Explorer", "Ctrl + C / Ctrl + X / Ctrl + V", "Copy / Cut / Paste"),
    ("File Explorer", "Shift + Delete", "Permanently delete (skip Recycle Bin)"),
    ("File Explorer", "Alt + Up", "Go to parent folder"),
    ("File Explorer", "Alt + Left/Right", "Navigate back/forward"),
    ("File Explorer", "Ctrl + Shift + E", "Expand folder tree to current path"),
    ("File Explorer", "Ctrl + Scroll", "Change icon size"),
    ("File Explorer", "Alt + P", "Toggle preview pane"),
    ("File Explorer", "Alt + Shift + P", "Toggle details pane"),

    # General Editing
    ("General Editing", "Ctrl + Z / Ctrl + Y", "Undo / Redo"),
    ("General Editing", "Ctrl + A", "Select all"),
    ("General Editing", "Ctrl + F", "Find"),
    ("General Editing", "Ctrl + H", "Find and Replace"),
    ("General Editing", "Ctrl + S", "Save"),
    ("General Editing", "Ctrl + Shift + V", "Paste without formatting"),

    # Media & System
    ("Media & System", "Volume Up/Down/Mute keys", "Adjust system volume"),
    ("Media & System", "Print Screen", "Copy full screenshot to clipboard"),
    ("Media & System", "Alt + Print Screen", "Copy active window screenshot to clipboard"),
    ("Media & System", "Win + Shift + S", "Open Snip & Sketch region capture"),
    ("Media & System", "Ctrl + Alt + Delete", "Open security/lock/Task Manager screen"),
    ("Media & System", "Ctrl + Shift + Esc", "Open Task Manager directly"),

    # Office General
    ("Office General", "Ctrl + N", "Create new blank document / workbook"),
    ("Office General", "Ctrl + O", "Open an existing document / file"),
    ("Office General", "Ctrl + P", "Print document or preview"),
    ("Office General", "Ctrl + B", "Toggle bold text"),
    ("Office General", "Ctrl + I", "Toggle italic text"),
    ("Office General", "Ctrl + U", "Toggle underline text"),
    ("Office General", "Ctrl + Home", "Move cursor to beginning of document"),
    ("Office General", "Ctrl + End", "Move cursor to end of document"),
    ("Office General", "F12", "Save As dialog"),
    ("Office General", "Ctrl + Shift + F", "Open Font dialog"),

    # Word
    ("Word", "Ctrl + Enter", "Insert page break"),
    ("Word", "Ctrl + ]", "Increase font size by 1 point"),
    ("Word", "Ctrl + [", "Decrease font size by 1 point"),
    ("Word", "Alt + Shift + D", "Insert current date field"),
    ("Word", "Ctrl + Shift + C", "Copy formatting (Format Painter)"),
    ("Word", "Ctrl + Shift + V", "Apply copied formatting"),
    ("Word", "Ctrl + K", "Insert hyperlink"),
    ("Word", "Ctrl + E", "Center align text"),
    ("Word", "Ctrl + L", "Left align text"),
    ("Word", "Ctrl + R", "Right align text"),
    ("Word", "Ctrl + J", "Justify text"),

    # Excel
    ("Excel", "F2", "Edit active cell"),
    ("Excel", "F4", "Repeat last action or cycle cell reference types ($A$1)"),
    ("Excel", "Ctrl + ;", "Insert current date"),
    ("Excel", "Ctrl + Shift + ;", "Insert current time"),
    ("Excel", "Alt + =", "AutoSum selected cells"),
    ("Excel", "Ctrl + Arrow keys", "Jump to edge of data region"),
    ("Excel", "Ctrl + Shift + Arrow keys", "Extend selection to edge of data region"),
    ("Excel", "Ctrl + Space", "Select entire column"),
    ("Excel", "Shift + Space", "Select entire row"),
    ("Excel", "Ctrl + 1", "Open Format Cells dialog"),
    ("Excel", "F9", "Recalculate all formulas in all open workbooks"),
    ("Excel", "Ctrl + `", "Toggle displaying formulas vs formula results"),
    ("Excel", "Alt + Enter", "Start a new line in the same cell"),
    ("Excel", "Ctrl + Shift + L", "Toggle AutoFilter"),

    # PowerPoint
    ("PowerPoint", "F5", "Start slide show from beginning"),
    ("PowerPoint", "Shift + F5", "Start slide show from current slide"),
    ("PowerPoint", "Ctrl + M", "Insert a new slide"),
    ("PowerPoint", "Ctrl + D", "Duplicate selected slide or object"),
    ("PowerPoint", "B / W during show", "Black out or White out the slide show screen"),
]

SHORTCUTS = _DEFAULT_SHORTCUTS

