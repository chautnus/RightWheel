# Batch 2: UI Studio & Modern V3 WebView2 Frontend Port

## Context
Build the dedicated RightWheel V3 React 19 + Tailwind CSS frontend in `C:\dev\ui-studio\src\projects\rightwheel-v3`, configure the Vite build mode `rightwheel-v3`, and establish the build sync pipeline to `Mousehotkey/src/ui_dist`.

## Tasks
- [ ] **T-81: Setup RightWheel V3 project in UI Studio** (`RightWheelApp.tsx`, `bridge/*`, `views/WelcomeView.tsx`)
- [ ] **T-82: Implement Settings workspace & modal editors** (`views/SettingsView.tsx`, `components/*`)
- [ ] **T-83: Implement hardware KeyRecorderModal** (`components/KeyRecorderModal.tsx`)
- [ ] **T-84: Configure Vite build & UI sync script** (`vite.config.ts`, `package.json`, `scripts/build_v3_ui.ps1`)

## Expected Changes
- `C:\dev\ui-studio\src\projects\rightwheel-v3/`: Complete React 19 app tailored for RightWheel with Bento landing page (Mouse Shortcuts, Mouse Gestures, App Profiles), Settings view, KeyRecorderModal, and Mock bridge.
- `C:\dev\ui-studio\vite.config.ts` and `package.json`: Target `dist-rightwheel-v3`.
- `Mousehotkey/scripts/build_v3_ui.ps1`: Automated build and sync script.
- `Mousehotkey/src/ui_dist/`: Production static build (HTML, CSS, JS bundles).

## Verification
- `npm run build:rightwheel-v3` in `C:\dev\ui-studio` passes with 0 TypeScript/Vite errors.
- `scripts/build_v3_ui.ps1` successfully syncs `dist-rightwheel-v3` into `src/ui_dist`.
- `index.html` and bundled assets exist and validate in `src/ui_dist/`.
