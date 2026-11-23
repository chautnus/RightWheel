# Architecture: Multi-Step Macro Execution Engine & ChatGPT Integration (f019)

## 1. Overview & Context
- **Purpose**: Reliably execute multi-step automation sequences (e.g., `Copy -> Open ChatGPT -> Paste -> Submit` or clipboard web transforms) triggered from the Shortcut Panel or mouse gestures without dropping steps, misfiring keystrokes into wrong windows, or freezing the UI.
- **Root Cause Solved**:
  - Legacy `PanelLogic` previously called `shortcut_executor.execute_sequence`, which dropped `text` steps, used naive `webbrowser.open(url)`, lacked browser foreground activation, and did not wait for browser tab readiness.
  - As a result, subsequent keystrokes (`ctrl+v`, text) were injected before the browser gained focus, pasting clipboard contents into whatever previous window had foreground.
- **Reference Model**: Unified with the proven architecture in `Touchpad gesture` (ADR-008 & ADR-020).

## 2. Key Architectural Decisions
1. **Async Threaded Execution (`SequenceExecutorWorker`)**:
   - `PanelLogic.select_current()` delegates `SequenceItem` via `src.features.action_dispatcher.sequence_executor.execute_steps_async(item.steps)`.
   - Runs on a dedicated daemon background worker thread to ensure the UI immediately hides and never blocks on sleep delays or web requests.
2. **Browser Foreground Activation & Tab Readiness Gate**:
   - In `sequence_executor.execute_steps`:
     ```python
     if stype in _URL_STEP_TYPES and idx + 1 < len(steps):
         next_type = str(steps[idx + 1].get("type", "")).upper()
         if next_type in _KEYSTROKE_STEP_TYPES:
             focused = clipboard_web_actions.focus_default_browser_window()
             ready = clipboard_web_actions.wait_until_browser_tab_ready(timeout_s=5.0)
     ```
   - Automatically queries Windows default browser executable (`get_default_browser_path` / `get_default_browser_exe`), activates the window (`focus_default_browser_window`), and polls until the tab title is no longer 'Untitled'/'New Tab' before injecting keystrokes.
3. **Hardware Scan Codes & Unicode Key Injection**:
   - Keys use Win32 `SendInput` with scan codes and micro-delays between down/up.
   - Text steps type full Unicode strings via `KEYEVENTF_UNICODE` (`_send_text`).
4. **Mandatory Modifier Key Cleanup**:
   - `finally: release_modifier_keys()` explicitly sends `KEYEVENTF_KEYUP` for Ctrl, Alt, Shift, and Win to ensure no keyboard modifiers ever remain stuck after an error or macro completion.
5. **Built-in Presets**:
   - `Search Copied Text`: `ctrl+c` (150ms) -> `https://www.google.com/search?q={text}` (10ms).
   - `ChatGPT: Paste Clipboard`: `ctrl+c` (200ms) -> `https://chatgpt.com` (3000ms) -> `ctrl+v` (800ms) -> `enter` (10ms).
   - `chatgpt_paste` template in `BUILTIN_WEBCLIP_TEMPLATES` with `mode: "paste_submit"`.
