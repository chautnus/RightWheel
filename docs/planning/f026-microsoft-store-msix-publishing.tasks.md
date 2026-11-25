# Tasks — f026-microsoft-store-msix-publishing

## Epic: [F-026] Microsoft Store MSIX Packaging, WinRT IAP & Submission Prep
- **US-071**: Automated MSIX packaging pipeline & Store visual assets
- **US-072**: WinRT StoreContext license verification & Pro IAP purchase
- **US-073**: MSIX-safe writable logging path (`%LOCALAPPDATA%\RightWheel\data`)
- **US-074**: Store-compliant Privacy Policy page (`docs/privacy.html`)

| ID     | Task | Story  | Estimate | Priority | Deps   | Status |
|--------|------|--------|----------|----------|--------|--------|
| T-0142 | Update `src/core/app_paths.py` so `log_debug()` writes to `%LOCALAPPDATA%\RightWheel\data` when running inside read-only MSIX (`WindowsApps`) | US-073 | 0.5h | P0 | - | todo |
| T-0143 | Port WinRT `StoreContext` (`_query_winrt_addon_license`, `verify_store_license`, `purchase_pro`, `open_store_purchase_page`) into `src/core/store_license_service.py` | US-072 | 1.5h | P0 | T-0142 | todo |
| T-0144 | Create `packaging/msix/AppxManifest.xml` (`ChauTran.RightWheel`, `runFullTrust`, `en-us`) and generate 5 Store PNG assets from `assets/icon.png` into `packaging/msix/Assets/` | US-071 | 1h | P0 | - | todo |
| T-0145 | Create `scripts/build_msix.py` supporting `--source`, asset fallback, and `makeappx.exe` packing into `dist/RightWheel_1.0.0.0_x64.msix` | US-071 | 1h | P0 | T-0144 | todo |
| T-0146 | Create `docs/privacy.html` (English Privacy Policy for RightWheel `runFullTrust` & offline-first zero telemetry) | US-074 | 0.5h | P0 | - | todo |
| T-0147 | Add unit tests in `tests/test_v3_feature_parity.py`, run `pytest`, run `scripts/build_msix.py` to produce `.msix`, verify contents, and push Git | US-071, US-072, US-073 | 1.5h | P0 | T-0143, T-0145 | todo |
