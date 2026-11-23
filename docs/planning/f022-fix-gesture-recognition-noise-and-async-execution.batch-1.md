# Batch 1: f022-fix-gesture-recognition-noise-and-async-execution

Tasks: T-126, T-127, T-128, T-129

## Target Files
1. `src/features/mouse_mapper/logic/gesture_recognizer.py`
2. `src/features/mouse_mapper/logic/mouse_mapper_logic.py`
3. `tests/test_v3_feature_parity.py`

## Instructions
1. Implement `normalize_directions` in `gesture_recognizer.py` to filter start/end diagonal noise and sandwiched wobbles, plus net displacement fallback.
2. In `mouse_mapper_logic.py`, move gesture action execution to a `threading.Timer(0.06, _do_execute).start()` background thread, and log stroke recognition details via `log_debug`.
3. Add unit tests in `tests/test_v3_feature_parity.py` covering noisy gesture paths and verify.
4. Run PyInstaller to build `dist/RightWheel.exe`.
