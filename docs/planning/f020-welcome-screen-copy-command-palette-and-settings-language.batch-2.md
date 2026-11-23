# BATCH 2/2: Step 1/2 Command Palette Configuration, Build & Verification

## Task T-117: Integrate Command Palette Configuration in `WizardView.tsx` Step 1/2
- **File**: `C:\dev\ui-studio\src\projects\rightwheel-v3\views\WizardView.tsx`
- **Goal**:
  - In `step === 0` ("Bước 1 / 2"), provide segmented pills:
    - `[ 🖱️ Cử chỉ vẽ & Con lăn ]`
    - `[ ⚡ Bảng lệnh nhanh (Command Palette) ]`
  - Under `Bảng lệnh nhanh`:
    - List commands from `globalProfile.commands` with label, type badge, target, and action description.
    - Add `CommandEditorModal` support to create and edit commands directly.
    - Provide "+ Thêm lệnh nhanh" button.
    - Reorder and delete actions.
    - Save changes using `bridgeClient.saveProfileCommands(globalProfile.id, nextCommands)`.
- **Verify**: Commands can be inspected, created, edited, and saved in Step 1/2.

## Task T-118: Compile UI & Sync to `src/ui_dist/`
- **Commands**:
  - `npm --prefix "C:\dev\ui-studio" run build:rightwheel-v3`
  - `powershell.exe -ExecutionPolicy Bypass -File .\scripts\build_v3_ui.ps1`
- **Goal**: Bundle production HTML/CSS/JS and copy into `src/ui_dist/`.
- **Verify**: Files in `src/ui_dist/` update with new timestamp and build hash.

## Task T-119: Pytest & Verification
- **Commands**:
  - `pytest`
- **Verify**: All automated tests pass cleanly.
