# Tasks: f019-macro-copy-open-chatgpt-paste-fix

## Task Summary
- **Total Tasks**: 5
- **Batches**: 1 batch (`.batch-1.md`)

## Task List
- **T-109**: Update `src/features/shortcut_panel/logic/panel_logic.py` to route `SequenceItem` execution to `src.features.action_dispatcher.sequence_executor.execute_steps_async(item.steps)`.
- **T-110**: Update `src/features/shortcut_panel/services/shortcut_executor.py:execute_sequence` to delegate to `src.features.action_dispatcher.sequence_executor.execute_steps(steps)`.
- **T-111**: Add built-in ChatGPT macro preset (`ChatGPT: Paste Clipboard`) to `DEFAULT_COMMANDS` in `src/core/config_service.py` and `_DEFAULT["default"]` in `src/features/shortcut_panel/services/config_service.py`.
- **T-112**: Add regression and unit test cases in `tests/test_sequence_integration.py` verifying macro execution steps, browser focusing triggers, and panel delegation.
- **T-113**: Rebuild standalone binary `dist/RightWheel.exe` with PyInstaller and verify executable status.
