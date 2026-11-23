# BATCH 3/3: UI Build, Standalone Packaging & Verification

## Task T-102: Build UI Studio & Sync Bundle
- **Commands**:
  - `npm --prefix "C:\dev\ui-studio" run build:rightwheel-v3`
  - `powershell.exe -ExecutionPolicy Bypass -File .\scripts\build_v3_ui.ps1`
- **Goal**: Produce latest production HTML, CSS, JS bundle in `src/ui_dist/`.
- **Verify**: Files exist in `src/ui_dist/assets/`.

## Task T-103: Pytest, PyInstaller Standalone Build & Remote Push
- **Commands**:
  - `pytest` (verify 16 passed)
  - `Stop-Process -Name RightWheel -Force -ErrorAction SilentlyContinue`
  - `python -m PyInstaller RightWheel.spec --noconfirm`
  - Smoke test `dist/RightWheel.exe` startup without `--background`.
  - `git add -A; git commit -m "feat(f017): redesign welcome screen for mouse & draw gestures with action descriptions"; git push origin main`
- **Verify**: `dist/RightWheel.exe` starts without errors, remote git hash matches.
