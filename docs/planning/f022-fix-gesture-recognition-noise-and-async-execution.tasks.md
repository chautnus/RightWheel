# Tasks: f022-fix-gesture-recognition-noise-and-async-execution

- [ ] **T-126**: Implement noise-tolerant stroke normalization and net displacement fallback in `src/features/mouse_mapper/logic/gesture_recognizer.py`
  - Collapse sandwiched wobbles between identical or opposite cardinal directions
  - Strip leading and trailing diagonal jitter
  - Add net displacement calculation fallback from `_points`
- [ ] **T-127**: Implement asynchronous deferred action execution and diagnostics in `src/features/mouse_mapper/logic/mouse_mapper_logic.py`
  - Wrap gesture finish execution in `threading.Timer(0.06, _do_execute).start()`
  - Immediate `_on_right_up` return to cleanly release hook lock
  - Add diagnostic `log_debug` for raw stroke, normalized directions, and execution outcome
- [ ] **T-128**: Unit tests for gesture noise normalization, net displacement fallback, and deferred execution in `tests/test_v3_feature_parity.py`
  - Test all 16 gesture patterns with realistic human wobbles
  - Verify `prtsc` and keyboard combos
- [ ] **T-129**: Recompile standalone executable `dist/RightWheel.exe` and verify end-to-end
