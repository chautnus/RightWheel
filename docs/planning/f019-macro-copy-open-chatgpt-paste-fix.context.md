# Context: f019-macro-copy-open-chatgpt-paste-fix

## 1. Problem Description
- User requested a reliable macro sequence: `Copy (Ctrl+C) -> Open ChatGPT (https://chatgpt.com) -> Paste (Ctrl+V) -> Submit (Enter)` (or typing prompt then Enter).
- In the reference project `C:\dev\Touchpad gesture`, this macro is named "ChatGPT: Text This Image" / "ChatGPT: Paste Clipboard" and works reliably:
  1. Copies selection.
  2. Launches default browser out-of-process via `rundll32 url.dll,FileProtocolHandler` / browser executable path (without opening Windows Documents folder).
  3. Activates and brings the browser window to foreground (`focus_default_browser_window`).
  4. Waits for tab readiness (`wait_until_browser_tab_ready`).
  5. Pastes clipboard (`ctrl+v`), types unicode text (`KEYEVENTF_UNICODE`), and submits via `enter`.
  6. Releases all modifier keys cleanly in `finally: release_modifier_keys()`.
- In `c:\dev\Mousehotkey` (RightWheel):
  1. `PanelLogic` in `src/features/shortcut_panel/logic/panel_logic.py:144` delegates `SequenceItem` to `shortcut_executor.execute_sequence`.
  2. `shortcut_executor.execute_sequence` is an incomplete legacy implementation:
     - Unrecognized step types like `text` are dropped with a warning.
     - Uses naive `webbrowser.open(url)` which does not ensure the browser takes foreground focus.
     - Has NO post-URL browser focus or tab readiness wait, firing `ctrl+v` into whatever previous application was focused.
     - Does not guarantee modifier key release on error.
  3. `DEFAULT_COMMANDS` in `src/core/config_service.py` lacks the ChatGPT macro preset.

## 2. Solution Architecture
- Unify execution engine: Connect `panel_logic.py` and `shortcut_executor.execute_sequence` to `src.features.action_dispatcher.sequence_executor`:
  - `execute_steps_async` runs sequences on a dedicated background thread without freezing the UI.
  - Automatically activates default browser window and polls tab readiness after URL steps before sending keystrokes.
  - Supports `shortcut`, `url`, `text`, `command`, `app`, `url_clipboard`, `gemini`, etc.
  - Strict cleanup of modifier keys (`release_modifier_keys`) in `finally`.
- Add default ChatGPT sequence preset in `DEFAULT_COMMANDS` (`src/core/config_service.py`) and `_DEFAULT["default"]` (`src/features/shortcut_panel/services/config_service.py`).
- Add regression and integration tests in `tests/test_sequence_integration.py`.
- Rebuild PyInstaller binary `dist/RightWheel.exe` and verify.
