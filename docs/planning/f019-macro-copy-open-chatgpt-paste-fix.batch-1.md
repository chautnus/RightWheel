# Batch 1: f019-macro-copy-open-chatgpt-paste-fix

## Tasks
- T-109: Delegate `SequenceItem` execution in `src/features/shortcut_panel/logic/panel_logic.py` to `src.features.action_dispatcher.sequence_executor.execute_steps_async(item.steps)`.
- T-110: Refactor `src/features/shortcut_panel/services/shortcut_executor.py:execute_sequence` to forward to `src.features.action_dispatcher.sequence_executor.execute_steps(steps)`.
- T-111: Configure default ChatGPT macro preset in `src/core/config_service.py` (`DEFAULT_COMMANDS`) and `src/features/shortcut_panel/services/config_service.py` (`_DEFAULT`).
- T-112: Add sequence integration tests in `tests/test_sequence_integration.py`.
- T-113: Recompile PyInstaller standalone executable `dist/RightWheel.exe` and test binary launch.
