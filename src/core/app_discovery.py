"""Application discovery service: enumerate installed and running Windows applications."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
from pathlib import Path
from typing import Any

kernel32 = ctypes.windll.kernel32
TH32CS_SNAPPROCESS = 0x00000002


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]


SYSTEM_EXES = {
    "system", "system idle process", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "svchost.exe", "fontdrvhost.exe", "dwm.exe", "conhost.exe",
    "sihost.exe", "taskhostw.exe", "explorer.exe", "shellexperiencehost.exe", "searchhost.exe",
    "startmenuexperiencehost.exe", "lockapp.exe", "ctfmon.exe", "wudfhost.exe", "dllhost.exe",
}


def get_installed_apps() -> list[dict[str, str]]:
    """Scan Start Menu for installed applications and resolve target exe.

    Returns:
        List of dicts: [{"name": str, "exe": str, "path": str}, ...]
    """
    apps: list[dict[str, str]] = []
    seen_exes: set[str] = set()

    start_dirs = [
        Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    ]

    shell: Any = None
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
    except Exception:
        pass

    for sdir in start_dirs:
        if not sdir.exists():
            continue
        for lnk in sdir.rglob("*.lnk"):
            name = lnk.stem
            # Filter out uninstallers, helpers, and documentation
            lower_name = name.lower()
            if any(w in lower_name for w in ("uninstall", "gỡ cài đặt", "help", "readme", "documentation")):
                continue

            exe = ""
            target_path = ""
            if shell:
                try:
                    sc = shell.CreateShortcut(str(lnk))
                    target_path = sc.TargetPath
                    if target_path and target_path.lower().endswith(".exe"):
                        exe = os.path.basename(target_path)
                except Exception:
                    pass

            if not exe and " " not in name and lower_name not in ("desktop",):
                exe = f"{name}.exe"

            if exe and exe.lower() not in seen_exes:
                seen_exes.add(exe.lower())
                apps.append({
                    "name": name,
                    "exe": exe,
                    "path": target_path,
                })

    apps.sort(key=lambda x: x["name"].lower())
    return apps


def get_running_apps() -> list[dict[str, str]]:
    """Enumerate running non-system processes with .exe filenames.

    Returns:
        List of dicts: [{"name": str, "exe": str}, ...]
    """
    apps: list[dict[str, str]] = []
    seen_exes: set[str] = set()

    h_snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if not h_snap:
        return apps

    pe = PROCESSENTRY32()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32)

    try:
        if kernel32.Process32First(h_snap, ctypes.byref(pe)):
            while True:
                raw_exe = pe.szExeFile.decode("ansi", errors="ignore").strip()
                lower = raw_exe.lower()
                if lower and lower.endswith(".exe") and lower not in SYSTEM_EXES and lower not in seen_exes:
                    seen_exes.add(lower)
                    # Friendly name from exe stem
                    display_name = raw_exe[:-4].replace("_", " ").capitalize()
                    apps.append({
                        "name": display_name,
                        "exe": raw_exe,
                    })
                if not kernel32.Process32Next(h_snap, ctypes.byref(pe)):
                    break
    finally:
        kernel32.CloseHandle(h_snap)

    apps.sort(key=lambda x: x["name"].lower())
    return apps
