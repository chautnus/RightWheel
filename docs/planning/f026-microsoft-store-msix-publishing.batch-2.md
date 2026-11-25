# Batch 2 — f026-microsoft-store-msix-publishing (MSIX Manifest, Assets, Builder, Privacy & Tests)

- **Tasks:** T-0144, T-0145, T-0146, T-0147
- **Target Files:**
  - `packaging/msix/AppxManifest.xml`
  - `packaging/msix/Assets/*` (5 PNG files)
  - `scripts/build_msix.py`
  - `docs/privacy.html`
  - `tests/test_v3_feature_parity.py`

## Instructions
1. **T-0144 (`packaging/msix/`):**
   - Create `packaging/msix/AppxManifest.xml` with `Name="ChauTran.RightWheel"`, `Publisher="CN=9AAD203F-B008-4B7B-83DF-4D8364080D65"`, `Version="1.0.0.0"`, `ProcessorArchitecture="x64"`, `DisplayName="RightWheel"`, `Executable="RightWheel.exe"`, `<Resource Language="en-us" />`, `<rescap:Capability Name="runFullTrust" />`.
   - Generate `StoreLogo.png` (50x50), `Square44x44Logo.png` (44x44), `Square150x150Logo.png` (150x150), `Wide310x150Logo.png` (310x150), and `Addon_300x300.png` (300x300) cleanly composited on `#0b1326` dark slate background from `assets/icon.png`.
2. **T-0145 (`scripts/build_msix.py`):**
   - Create `scripts/build_msix.py` supporting `--source` (defaults to `dist/RightWheel_Protected.exe` if present, else `dist/RightWheel.exe`), staging `RightWheel.exe`, `AppxManifest.xml`, and `Assets/`, auto-locating `makeappx.exe` in Windows Kits 10, and generating `dist/RightWheel_1.0.0.0_x64.msix`.
3. **T-0146 (`docs/privacy.html`):**
   - Create English Privacy Policy HTML page for RightWheel explaining `runFullTrust` / `WH_MOUSE_LL` local-only processing and zero data collection.
4. **T-0147 (Tests, MSIX Build & Push):**
   - Add unit tests in `tests/test_v3_feature_parity.py` for `verify_store_license()` (mocked WinRT response), `purchase_pro()` (mocked WinRT response), and `log_debug()` writable path.
   - Run `python -m pytest tests/ -q` (all pass).
   - Run `python scripts/build_msix.py` and verify `dist/RightWheel_1.0.0.0_x64.msix` is created cleanly.
   - Commit & push to `origin/main`.

## Done Definition & Verify
- `pytest tests/ -q` passes 100%.
- `python scripts/build_msix.py` exits 0 and creates `dist/RightWheel_1.0.0.0_x64.msix`.
