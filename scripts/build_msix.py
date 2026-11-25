"""Build MSIX package for Microsoft Store submission using Windows 10/11 SDK makeappx.exe."""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_SRC = ROOT_DIR / "packaging" / "msix" / "AppxManifest.xml"
DEFAULT_PROTECTED_EXE = ROOT_DIR / "dist" / "RightWheel_Protected.exe"
DEFAULT_DEV_EXE = ROOT_DIR / "dist" / "RightWheel.exe"
STAGING_DIR = ROOT_DIR / "build_msix" / "msix_staging"
OUTPUT_MSIX = ROOT_DIR / "dist" / "RightWheel_1.0.1.0_x64.msix"
ICON_SRC = ROOT_DIR / "assets" / "icon.png"


def _find_makeappx() -> Path | None:
    """Locate Windows SDK makeappx.exe (preferring newest installed x64 SDK)."""
    kits_bin = Path(r"C:\Program Files (x86)\Windows Kits\10\bin")
    if kits_bin.exists():
        candidates = sorted(kits_bin.glob("*/x64/makeappx.exe"), reverse=True)
        if candidates:
            return candidates[0]
    found = shutil.which("makeappx.exe")
    return Path(found) if found else None


def generate_store_logo(width: int, height: int, out_path: Path, bg_rgb: tuple[int, int, int] = (11, 19, 38)) -> None:
    """Render clean high-DPI Store PNG logo from assets/icon.png centered on dark slate canvas."""
    canvas = Image.new("RGBA", (width, height), (*bg_rgb, 255))
    if ICON_SRC.exists():
        icon = Image.open(ICON_SRC).convert("RGBA")
        target_side = max(16, int(min(width, height) * 0.72))
        icon_resized = icon.resize((target_side, target_side), Image.Resampling.LANCZOS)
        ox = (width - target_side) // 2
        oy = (height - target_side) // 2
        canvas.paste(icon_resized, (ox, oy), icon_resized)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG")


def ensure_msix_assets(assets_dir: Path) -> None:
    """Ensure all 5 required Microsoft Store visual assets exist in assets_dir."""
    specs = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square150x150Logo.png": (150, 150),
        "Wide310x150Logo.png": (310, 150),
        "Addon_300x300.png": (300, 300),
    }
    for fname, (w, h) in specs.items():
        p = assets_dir / fname
        if not p.exists():
            generate_store_logo(w, h, p)


def build_msix(source_path: str | None = None) -> int:
    exe_src: Path | None = None
    if source_path:
        candidate = Path(source_path).resolve()
        if not candidate.exists():
            print(f"ERROR: Specified source executable not found: {candidate}")
            return 1
        exe_src = candidate
    elif DEFAULT_PROTECTED_EXE.exists():
        exe_src = DEFAULT_PROTECTED_EXE
        print(f"[INFO] Auto-selected Protected Binary: {exe_src}")
    elif DEFAULT_DEV_EXE.exists():
        exe_src = DEFAULT_DEV_EXE
        print(f"[INFO] Auto-selected Binary: {exe_src}")
    else:
        print(f"ERROR: Neither {DEFAULT_PROTECTED_EXE} nor {DEFAULT_DEV_EXE} found.")
        return 1

    if not MANIFEST_SRC.exists():
        print(f"ERROR: AppxManifest.xml not found at {MANIFEST_SRC}")
        return 1

    makeappx = _find_makeappx()
    if makeappx is None or not makeappx.exists():
        print("ERROR: makeappx.exe not found in Windows Kits 10.")
        return 1

    if STAGING_DIR.exists():
        def _handle_remove_readonly(func, path, exc):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass
        shutil.rmtree(STAGING_DIR, onexc=_handle_remove_readonly)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[PACK] Staging executable: {exe_src} -> {STAGING_DIR / 'RightWheel.exe'}")
    shutil.copy2(exe_src, STAGING_DIR / "RightWheel.exe")
    shutil.copy2(MANIFEST_SRC, STAGING_DIR / "AppxManifest.xml")

    assets_dir = STAGING_DIR / "Assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    pkg_assets = ROOT_DIR / "packaging" / "msix" / "Assets"
    if pkg_assets.exists():
        shutil.copytree(pkg_assets, assets_dir, dirs_exist_ok=True)
    ensure_msix_assets(assets_dir)

    if OUTPUT_MSIX.exists():
        OUTPUT_MSIX.unlink()

    cmd = [
        str(makeappx),
        "pack",
        "/d", str(STAGING_DIR),
        "/p", str(OUTPUT_MSIX),
        "/o",
    ]
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("STDERR:", res.stderr)
        return res.returncode

    size_mb = OUTPUT_MSIX.stat().st_size / (1024 * 1024)
    print(f"SUCCESS: MSIX generated at {OUTPUT_MSIX} ({size_mb:.2f} MB)")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build RightWheel MSIX package for Microsoft Store submission.")
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Path to source executable. Default: auto-selects RightWheel_Protected.exe if available, else RightWheel.exe",
    )
    args = parser.parse_args()
    sys.exit(build_msix(source_path=args.source))
