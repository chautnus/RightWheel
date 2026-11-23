# Batch 3: Host Bridge, Main Integration, Packaging & Verification

## Context
Implement the Python WebView2 Host and Bridge API, connect `--webview-host` subprocess into `main.py`, preserve all mouse-hook locked invariants, update PyInstaller packaging spec, and verify all automated tests.

## Tasks
- [ ] **T-85: Implement WebView2 Host & Bridge API in RightWheel** (`src/features/webview_ui/*`)
- [ ] **T-86: Integrate into RightWheel `main.py` and System Tray** (`src/main.py`, `tray_ui.py`)
- [ ] **T-87: Safeguard mouse hook & state machine locked behaviors** (`mouse_mapper_logic.py`, `mouse_hook_service.py`)
- [ ] **T-88: Update build spec, run automated tests & verify** (`RightWheel.spec`, `tests/*`)

## Expected Changes
- `src/features/webview_ui/`: `bridge_api.py`, `host.py`, `launcher.py`, `key_recorder_bridge.py`.
- `src/main.py`: `--webview-host` STA dispatch, `SingleInstanceGuard`, `MemoryManager`, `StoreLicenseService`.
- `src/features/mouse_mapper/ui/tray_ui.py`: Modern settings & welcome launch via `WebViewLauncher`.
- `RightWheel.spec`: Add `ui_dist/` and `locales/` trees to PyInstaller data.

## Verification
- Run `pytest` with 100% pass rate.
- Launch `--webview-host --view settings` and `--webview-host --view welcome` verification.
- Test Tkinter fallback by setting `ui_engine: "tkinter"`.
- Test mouse hook and state machine invariants (RMB hold + scroll UP = panel, scroll DOWN = Alt+Tab).
