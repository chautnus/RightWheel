# PRD: f019-macro-copy-open-chatgpt-paste-fix

## 1. Overview
Ensure multi-step macro sequences (specifically `Copy -> Open ChatGPT -> Paste -> Submit`) execute reliably from both the Shortcut Panel and mouse gestures in RightWheel, matching the proven architecture from the Touchpad Gesture project.

## 2. Requirements & User Stories
- **US-057**: As a user, when I trigger the ChatGPT macro sequence from the Shortcut Panel or mouse gesture, the app must copy my selection, launch ChatGPT in my default browser, wait for the browser window to gain foreground focus and become ready, paste the copied content, and optionally submit.
- **US-058**: As a user, if a macro sequence fails or encounters an exception, all keyboard modifier keys (Ctrl, Alt, Shift, Win) must be immediately released so my keyboard does not get stuck in a modified state.

## 3. Acceptance Criteria
1. `PanelLogic.select_current()` delegates `SequenceItem` to `src.features.action_dispatcher.sequence_executor.execute_steps_async(item.steps)`.
2. `shortcut_executor.execute_sequence(steps)` delegates to `src.features.action_dispatcher.sequence_executor.execute_steps(steps)`.
3. Multi-step sequence containing `shortcut` (`ctrl+c`), `url` (`https://chatgpt.com`), `shortcut` (`ctrl+v`), `text` (`text this`), and `shortcut` (`enter`) executes each step in order.
4. If a URL step is followed by a keystroke/text step, `sequence_executor` activates the browser window and waits for tab readiness.
5. `DEFAULT_COMMANDS` in `src/core/config_service.py` and `_DEFAULT["default"]` in `src/features/shortcut_panel/services/config_service.py` provide a built-in ChatGPT macro preset.
6. All automated pytest tests pass without regression.
7. Standalone `dist/RightWheel.exe` builds cleanly and executes.
