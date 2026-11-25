## Elicitation — 2026-11-25

Problem: RightWheel currently only builds a portable PyInstaller EXE (`dist/RightWheel.exe`), lacks MSIX packaging (`AppxManifest.xml`, `makeappx.exe` pipeline, Store PNG visual assets), lacks WinRT `StoreContext` IAP/license verification in `store_license_service.py`, writes debug logs under read-only `Program Files\WindowsApps` when packaged as MSIX, and has no Privacy Policy page for Store submission.
Goal: Replicate Touchpad Gesture's proven Microsoft Store architecture for RightWheel (Free + 30-day Trial + Pro Add-on IAP, MSIX packaging via Windows SDK `makeappx.exe` with `--source` flag, MSIX-safe logging paths, and Privacy Policy / Landing HTML).
Scope IN:
- `src/core/app_paths.py`: Route `log_debug()` to `%LOCALAPPDATA%\RightWheel\data\` when running inside read-only MSIX (`WindowsApps`).
- `src/core/store_license_service.py`: Port WinRT `StoreContext` (`_query_winrt_addon_license`, `verify_store_license`, `purchase_pro`, `open_store_purchase_page`) with placeholder `STORE_PRODUCT_ID` / `STORE_ADDON_ID` ready for Partner Center IDs.
- `packaging/msix/AppxManifest.xml` & `packaging/msix/Assets/`: Manifest with `ChauTran.RightWheel`, `CN=9AAD203F-B008-4B7B-83DF-4D8364080D65`, `runFullTrust`, English (`en-us`), plus 5 Store visual assets generated from `assets/icon.png`.
- `scripts/build_msix.py`: Automated MSIX builder supporting `--source` (PyInstaller EXE default, future Nuitka Protected EXE ready) and `makeappx.exe` auto-discovery.
- `docs/privacy.html`: Offline-first Privacy Policy page disclosing `runFullTrust` mouse hook usage and zero telemetry, ready for GitHub Pages.
- Unit tests in `tests/test_v3_feature_parity.py` verifying WinRT IAP/license verification mocks and MSIX log path safety.
Scope OUT:
- Nuitka obfuscated protected build pipeline (kept compatible via `--source` flag for future phase).
- Submitting directly to Partner Center web portal (manual step with clear checklist provided to user).

---

## PRD — 2026-11-25

Path: docs/prd/f026-microsoft-store-msix-publishing.md
Version: 1.0
Summary: Package RightWheel as a Microsoft Store-ready MSIX bundle with 30-day trial + WinRT IAP, MSIX-safe writable paths, and Store compliance assets.

---

## Architecture — 2026-11-25

Pattern: Isolated Store MSIX Staging + WinRT StoreContext PowerShell Bridge
ADR-018: Microsoft Store MSIX Packaging & WinRT StoreContext IAP → docs/adr/ADR-018-microsoft-store-msix-packaging-and-winrt-iap.md

---

## Tasks — 2026-11-25

Total: 6 tasks (T-0142..T-0147), 6h estimate
Batches: 2 (batch-1: Core WinRT IAP & MSIX-safe paths; batch-2: MSIX Manifest, Assets, build_msix.py, Privacy Policy, Tests & Verification)
