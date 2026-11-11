"""Send keyboard shortcuts, launch apps, and open URLs."""
import ctypes
import ctypes.wintypes as wt
import logging
import os
import subprocess
import webbrowser

_log = logging.getLogger("mousehotkey")

INPUT_KEYBOARD    = 1
KEYEVENTF_KEYUP   = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

# Virtual key map
_VK: dict[str, int] = {
    "ctrl": 0x11, "control": 0x11,
    "alt":  0x12,
    "shift":0x10,
    "win":  0x5B, "windows": 0x5B, "win_l": 0x5B, "win_r": 0x5C,
    "tab":  0x09, "enter": 0x0D, "return": 0x0D,
    "esc":  0x1B, "escape": 0x1B,
    "space":0x20, "backspace": 0x08,
    "del":  0x2E, "delete": 0x2E, "ins": 0x2D, "insert": 0x2D,
    "home": 0x24, "end":  0x23,
    "pgup": 0x21, "pageup":   0x21,
    "pgdn": 0x22, "pagedown": 0x22,
    "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
    **{f"f{i}": 0x6F + i for i in range(1, 13)},
    **{str(i): 0x30 + i for i in range(10)},
    **{chr(65 + i).lower(): 0x41 + i for i in range(26)},
}

_EXTENDED = {0x25, 0x26, 0x27, 0x28, 0x2E, 0x2D,
             0x21, 0x22, 0x24, 0x23, 0x5B, 0x5C}


# ── Windows INPUT structures (must match 64-bit ABI exactly) ──────────────────
#
# sizeof(INPUT) on 64-bit Windows = 40 bytes:
#   DWORD type        → 4 bytes  (offset 0)
#   4-byte pad        →           (offset 4)  ← union needs 8-byte alignment
#   union (MOUSEINPUT is largest at 32 bytes)  (offset 8)
#
# MOUSEINPUT (32 bytes):  dx(4) dy(4) mouseData(4) dwFlags(4) time(4) [pad4] dwExtraInfo(8)
# KEYBDINPUT (24 bytes):  wVk(2) wScan(2) dwFlags(4) time(4) [pad4] dwExtraInfo(8)
#
# Without MOUSEINPUT in the union the size would be 32 → SendInput returns 0.

class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx",          wt.LONG),
        ("dy",          wt.LONG),
        ("mouseData",   wt.DWORD),
        ("dwFlags",     wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]

class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk",         wt.WORD),
        ("wScan",       wt.WORD),
        ("dwFlags",     wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]

class _HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg",    wt.DWORD),
        ("wParamL", wt.WORD),
        ("wParamH", wt.WORD),
    ]

class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", _MOUSEINPUT),
        ("ki", _KEYBDINPUT),
        ("hi", _HARDWAREINPUT),
    ]

class _INPUT(ctypes.Structure):
    _anonymous_ = ("_u",)
    _fields_    = [("type", wt.DWORD), ("_u", _INPUT_UNION)]

_SZ = ctypes.sizeof(_INPUT)


def execute(keys: str) -> None:
    """Execute a hotkey string like 'ctrl+shift+v'."""
    if not keys.strip():
        return
    parts = [p.strip().lower() for p in keys.split("+")]
    vks   = [_VK[p] for p in parts if p in _VK]
    unknown = [p for p in parts if p not in _VK]
    _log.debug(
        f"execute()  raw={keys!r}  parts={parts}  "
        f"vks={[hex(v) for v in vks]}  unknown={unknown}  cbSize={_SZ}"
    )
    if not vks:
        _log.warning(f"execute() no valid VKs for {keys!r} — nothing sent")
        return

    n   = len(vks) * 2
    arr = (_INPUT * n)()

    for i, vk in enumerate(vks):
        flags = KEYEVENTF_EXTENDEDKEY if vk in _EXTENDED else 0
        arr[i].type    = INPUT_KEYBOARD
        arr[i].ki.wVk  = vk
        arr[i].ki.dwFlags = flags

    for i, vk in enumerate(reversed(vks)):
        flags = (KEYEVENTF_EXTENDEDKEY if vk in _EXTENDED else 0) | KEYEVENTF_KEYUP
        arr[len(vks) + i].type       = INPUT_KEYBOARD
        arr[len(vks) + i].ki.wVk    = vk
        arr[len(vks) + i].ki.dwFlags = flags

    n_sent = ctypes.windll.user32.SendInput(n, arr, _SZ)
    _log.debug(f"SendInput({n} events, cbSize={_SZ}) → sent {n_sent}")


def execute_app(path: str, args: str = "") -> None:
    """Launch an application by path. Silently no-op if path is missing."""
    if not path:
        return
    try:
        cmd = [path] + (args.split() if args.strip() else [])
        subprocess.Popen(cmd, cwd=os.path.dirname(path) or None)
        _log.debug(f"execute_app()  path={path!r}")
    except Exception as exc:
        _log.warning(f"execute_app() failed: {exc}")


def execute_command(cmd: str, cwd: str = "") -> None:
    """Run a shell command (cmd /c). Silently no-op if cmd is empty."""
    if not cmd.strip():
        return
    try:
        subprocess.Popen(
            ["cmd.exe", "/c", cmd],
            cwd=cwd if cwd.strip() else None,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        _log.debug(f"execute_command()  cmd={cmd!r}  cwd={cwd!r}")
    except Exception as exc:
        _log.warning(f"execute_command() failed: {exc}")


def execute_url(url: str) -> None:
    """Open a URL in the default browser."""
    if not url:
        return
    try:
        webbrowser.open(url)
        _log.debug(f"execute_url()  url={url!r}")
    except Exception as exc:
        _log.warning(f"execute_url() failed: {exc}")
