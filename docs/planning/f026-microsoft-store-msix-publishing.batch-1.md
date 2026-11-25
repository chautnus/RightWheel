# Batch 1 — f026-microsoft-store-msix-publishing (WinRT IAP & MSIX-Safe Paths)

- **Tasks:** T-0142, T-0143
- **Target Files:**
  - `src/core/app_paths.py`
  - `src/core/store_license_service.py`

## Instructions
1. **T-0142 (`src/core/app_paths.py`):**
   - Update `log_debug()` so when frozen inside MSIX (`"WindowsApps" in str(sys.executable)` or `os.environ.get("LOCALAPPDATA")`), logs prefer `%LOCALAPPDATA%\RightWheel\data\` when the app root is read-only (`WindowsApps`), falling back safely without raising exceptions.
2. **T-0143 (`src/core/store_license_service.py`):**
   - Port `_query_winrt_addon_license(self) -> bool`, `verify_store_license(self) -> dict[str, Any]`, `purchase_pro(self, addon_id: str | None = None) -> bool`, and `open_store_purchase_page(self, product_id: str | None = None) -> bool` from Touchpad Gesture.
   - Keep `TRIAL_DAYS = 30`, `STORE_PRODUCT_ID` / `STORE_ADDON_ID` clearly marked as Partner Center placeholders until reservation is completed.

## Done Definition & Verify
- `python -m py_compile src/core/app_paths.py src/core/store_license_service.py` passes.
- `bridge_api.py` `run_system_action("check_license")` and `run_system_action("buy_license")` resolve `verify_store_license()` and `purchase_pro()` cleanly without `AttributeError`.
