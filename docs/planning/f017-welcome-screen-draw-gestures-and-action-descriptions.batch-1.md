# BATCH 1/3: Multilingual i18n Dictionary & Core Schema

## Task T-97: Clean 3/4-finger Touchpad Text across all 7 Locales in `src/core/i18n.py`
- **File**: `src/core/i18n.py`
- **Goal**: In dictionaries `vi`, `en`, `fr`, `es`, `it`, `pt`, `id`:
  - `welcome_step1-4`: Replace 3/4-finger swipe instructions with RMB + Scroll UP (Shortcut Panel), RMB + Scroll DOWN (Task Switcher), and RMB + Draw (Mouse Gestures).
  - `welcome_bento_1_title`, `welcome_bento_2_title`, `welcome_bento_3_title`: Update to "Bảng phím tắt chuột / Mouse Shortcut Panel", "Cử chỉ vẽ chuột / Mouse Draw Gestures & Trail", "Hồ sơ theo ứng dụng / Per-App Profiles".
  - Remove all leftover references to Windows Precision Touchpad or finger gestures.
- **Verify**: `pytest` passes and grep for `3 ngón` / `4 ngón` in welcome keys returns 0.

## Task T-98: Add Function Descriptions to `DEFAULT_MOUSE_GESTURES` & Bridge API
- **File**: `src/core/config_service.py`, `src/features/webview_ui/bridge_api.py`
- **Goal**:
  - In `DEFAULT_MOUSE_GESTURES`: Add `"description"` or human-readable `"label"`:
    - `D_R` (`ctrl+w`) -> label: "Đóng tab", description: "Đóng tab trình duyệt hiện tại (Close Tab)"
    - `U_R` (`ctrl+t`) -> label: "Mở tab mới", description: "Mở tab mới (New Tab)"
    - `L` (`alt+left`) -> label: "Quay lại", description: "Quay lại trang trước (Back)"
    - `R` (`alt+right`) -> label: "Tiếp theo", description: "Đi tới trang kế (Forward)"
    - `UP` (`COMMAND_PALETTE`) -> label: "Bảng phím tắt", description: "Mở bảng phím tắt nhanh (Shortcut Panel)"
    - `DOWN` (`ALT_TAB`) -> label: "Chuyển ứng dụng", description: "Chuyển đổi ứng dụng (Task Switcher)"
  - In `bridge_api.py`: Ensure `description` and `label` are passed in `get_initial_state()` gestures list.
- **Verify**: `python -c "from src.features.webview_ui.bridge_api import WebViewBridgeAPI; print(WebViewBridgeAPI().get_initial_state('')['data']['gestures'][0])"` contains `description`.
