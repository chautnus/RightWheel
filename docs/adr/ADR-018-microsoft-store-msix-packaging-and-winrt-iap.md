# ADR-018: Microsoft Store MSIX Packaging & WinRT StoreContext IAP

- **Status:** Accepted
- **Date:** 2026-11-25
- **Feature:** F-026 (`f026-microsoft-store-msix-publishing`)

## Context
RightWheel is currently distributed as a standalone PyInstaller executable (`dist/RightWheel.exe`). To publish on Microsoft Store (matching `Touchpad gesture`), the app must be packaged as an MSIX with `runFullTrust` capability, support native Store IAP / Add-on verification, and comply with WindowsApps read-only installation directory restrictions.

## Decision
1. **MSIX Packaging Pipeline (`scripts/build_msix.py`):** Use Windows 11 SDK `makeappx.exe` (`10.0.26100.0` / auto-detected) to package `dist/RightWheel.exe` (or a future `--source` Nuitka Protected binary) with `packaging/msix/AppxManifest.xml` and high-DPI PNG assets generated from `assets/icon.png` into `dist/RightWheel_<version>_x64.msix`.
2. **WinRT StoreContext via PowerShell Bridge (`store_license_service.py`):** Query `Windows.Services.Store.StoreContext` (`GetAppLicenseAsync` and `RequestPurchaseAsync`) via `powershell -NoProfile -NonInteractive` with `CREATE_NO_WINDOW` when `has_msix_package_identity()` is True, matching Touchpad Gesture's proven zero-C++-extension approach.
3. **MSIX Read-Only Install Dir Safety (`app_paths.py`):** When running from `WindowsApps` or with MSIX package identity, route `log_debug()` to `%LOCALAPPDATA%\RightWheel\data` instead of `sys.executable.parent / data` (which is read-only inside `C:\Program Files\WindowsApps`).
4. **Submission Compliance (`docs/privacy.html`):** Provide a static HTML Privacy Policy hosted via GitHub Pages explaining `runFullTrust` and local-only `WH_MOUSE_LL` mouse hook processing.

## Consequences
- **Positive:** Zero extra Python C-extension dependencies (no `winrt` pip packages needed); immediate parity with Touchpad Gesture's Store-approved architecture; seamless upgrade path to Nuitka Protected EXE via `--source`.
- **Negative:** Requires Partner Center `Publisher` CN, `ProductId`, and `AddonId` to be filled in once the app reservation is created in Microsoft Partner Center.
