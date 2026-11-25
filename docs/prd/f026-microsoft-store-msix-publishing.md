# PRD — f026-microsoft-store-msix-publishing

## 1. Objective
Prepare and package RightWheel for Microsoft Store submission using the exact architecture proven in Touchpad Gesture: Free download + 30-day full-feature trial + Pro Durable Add-on IAP via WinRT `StoreContext`, Windows 10/11 MSIX packaging (`AppxManifest.xml` + `makeappx.exe`), MSIX sandbox-safe logging paths, and a Store-compliant Privacy Policy page.

---

## 2. User Stories
- **US-071**: As a developer, I want `scripts/build_msix.py` to generate Store visual assets from `assets/icon.png`, stage `RightWheel.exe` and `AppxManifest.xml`, and build `dist/RightWheel_1.0.0.0_x64.msix` via Windows SDK `makeappx.exe` in one command.
- **US-072**: As a Microsoft Store user, I want RightWheel to verify my Microsoft Store Add-on license (`verify_store_license`) and open the native Windows Store checkout dialog (`purchase_pro`) when upgrading to Pro.
- **US-073**: As a Microsoft Store user running RightWheel from read-only `C:\Program Files\WindowsApps`, I want debug logs and runtime data to write cleanly to `%LOCALAPPDATA%\RightWheel\data\` without permission errors.
- **US-074**: As a Store reviewer, I want an English Privacy Policy page (`docs/privacy.html`) clearly explaining `runFullTrust` mouse hook usage and zero data collection.

---

## 3. Acceptance Criteria
1. `src/core/app_paths.py`: `log_debug()` resolves writable log folder via `%LOCALAPPDATA%\RightWheel\data` when frozen/MSIX (`has_msix_package_identity()` or `WindowsApps` in `sys.executable`), avoiding `PermissionError` in `Program Files\WindowsApps`.
2. `src/core/store_license_service.py`: Implements `_query_winrt_addon_license()`, `verify_store_license()`, `purchase_pro(addon_id=None)`, and `open_store_purchase_page(product_id=None)` matching Touchpad Gesture's exact interface, already wired to `bridge_api.py` (`check_license`, `buy_license`).
3. `packaging/msix/AppxManifest.xml`: Valid Windows.Desktop `runFullTrust` manifest with Publisher `CN=9AAD203F-B008-4B7B-83DF-4D8364080D65`, Identity `ChauTran.RightWheel`, Resource `en-us`, Executable `RightWheel.exe`.
4. `packaging/msix/Assets/`: Contains `StoreLogo.png` (50x50), `Square44x44Logo.png` (44x44), `Square150x150Logo.png` (150x150), `Wide310x150Logo.png` (310x150), `Addon_300x300.png` (300x300).
5. `scripts/build_msix.py`: Produces a valid `.msix` package in `dist/` using `makeappx.exe` and supports `--source <exe_path>`.
6. `docs/privacy.html`: Clean English Privacy Policy for RightWheel covering `WH_MOUSE_LL` / `runFullTrust` and offline-first zero telemetry.
7. All pytest unit tests pass (existing + new WinRT/MSIX tests).
