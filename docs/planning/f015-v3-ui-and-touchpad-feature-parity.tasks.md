# Tasks: f015-v3-ui-and-touchpad-feature-parity

## Summary
- Feature: V3 Modern WebView2 UI and Touchpad Gesture Feature Parity Port
- Total Tasks: 13
- Total Batches: 3

---

## Batch 1: Core Systems, Action Dispatcher & Licensing Port
Goal: Port foundational infrastructure, Schema v4 profile management, action dispatcher with 8 action types, active memory compaction, and store trial licensing daemon.

- [ ] **T-76: Port core infrastructure services**
  - Files: `src/core/app_paths.py`, `src/core/single_instance.py`, `src/core/crash_reporter.py`
  - Action: Adapt path resolution to `%APPDATA%/RightWheel`, implement robust Mutex single instance with window activate signal, and wire unhandled exception logging.
- [ ] **T-77: Port memory manager & store trial licensing daemon**
  - Files: `src/core/memory_manager.py`, `src/core/store_license_service.py`
  - Action: Implement periodic working set compaction (`SetProcessWorkingSetSize`, `EmptyWorkingSet`, `gc.collect`) maintaining ~40MB RAM; implement 30-day trial countdown with simulation mode and background auto-expiry daemon.
- [ ] **T-78: Port multi-language i18n system & locale dictionaries**
  - Files: `src/core/i18n.py`, `src/core/locales/` (`en.json`, `vi.json`, `fr.json`, `es.json`, `it.json`, `pt.json`, `id.json`)
  - Action: Provide dictionary-based i18n with 7 supported languages, parameter interpolation, and live language switch notifications.
- [ ] **T-79: Port Unified Profile Schema v4 & foreground application discovery**
  - Files: `src/core/config_service.py`, `src/core/profile_service.py`, `src/core/app_discovery.py`
  - Action: Support Global + per-app profiles (matching by `exe`, `title_contains`, `class_name`), global fallback inheritance, and scanning active/installed applications.
- [ ] **T-80: Port 8-Action Dispatcher & Macro Execution Engine**
  - Files: `src/features/action_dispatcher/` (`dispatcher.py`, `types.py`, `key_combo.py`, `macro_runner.py`, `web_clip.py`)
  - Action: Handle KEY_COMBO (with PrintScreen 0x54 SysRq fix), RUN_APP, OPEN_URL (direct browser executable launch), RUN_SHELL, FOLDER, SEQUENCE (with 2-tier foreground restoration and clipboard retry), TYPE_TEXT, WEB_CLIP.

---

## Batch 2: UI Studio & Modern V3 WebView2 Frontend Port
Goal: Build the dedicated RightWheel V3 React 19 + Tailwind CSS + Lucide Icons frontend in `ui-studio` and establish the static bundle sync pipeline.

- [ ] **T-81: Setup RightWheel V3 project in UI Studio**
  - Files: `C:\dev\ui-studio\src\projects\rightwheel-v3\RightWheelApp.tsx`, `bridge/` (`client.ts`, `mock.ts`, `types.ts`), `views/WelcomeView.tsx`
  - Action: Implement Bento Grid landing page (3 Bento highlights: Mouse Shortcuts & Wheel, Mouse Gestures Drawing, Per-App Profiles), header 7-language selector, trial badge, and view router.
- [ ] **T-82: Implement Settings workspace & modal editors**
  - Files: `C:\dev\ui-studio\src\projects\rightwheel-v3\views\SettingsView.tsx`, `components/` (`CommandsTab.tsx`, `CommandEditorModal.tsx`, `FolderEditorModal.tsx`, `GesturesTab.tsx`, `GestureEditorModal.tsx`, `GeneralTab.tsx`, `ReferenceTab.tsx`, `MacroBuilderSection.tsx`)
  - Action: Implement Profile Workspace (Global and App profiles), Command Editor (8 action types), Macro Builder, Mouse Gestures tab with visualizer, General tab with UI engine toggle and trial simulation, Reference tab with 1-click import.
- [ ] **T-83: Implement hardware KeyRecorderModal**
  - Files: `C:\dev\ui-studio\src\projects\rightwheel-v3\components\KeyRecorderModal.tsx`
  - Action: Port 1:1 hardware key capture with 4 modifier toggles (Ctrl, Shift, Alt, Win) and 10 direct system keys (arrows, Home, End, PgUp, PgDn, Tab, PrtSc) without double-trigger issues.
- [ ] **T-84: Configure Vite build & UI sync script**
  - Files: `C:\dev\ui-studio\vite.config.ts`, `C:\dev\ui-studio\package.json`, `scripts/build_v3_ui.ps1`
  - Action: Add `build:rightwheel-v3` npm script targeting `dist-rightwheel-v3`, and PowerShell sync script to copy into `Mousehotkey/src/ui_dist`.

---

## Batch 3: Host Bridge, Main Integration, Packaging & Verification
Goal: Connect WebView2 UI to RightWheel backend via IPC bridge, wire isolated host subprocess and Tkinter fallback into `main.py` and tray, update packaging spec, and verify all automated tests.

- [ ] **T-85: Implement WebView2 Host & Bridge API in RightWheel**
  - Files: `src/features/webview_ui/bridge_api.py`, `src/features/webview_ui/host.py`, `src/features/webview_ui/launcher.py`, `src/features/webview_ui/key_recorder_bridge.py`
  - Action: Expose Python IPC methods to window.pywebview.api, launch isolated Edge WebView2 child process on `--webview-host`, and manage automatic Tkinter fallback.
- [ ] **T-86: Integrate into RightWheel `main.py` and System Tray**
  - Files: `src/main.py`, `src/features/mouse_mapper/ui/tray_ui.py`
  - Action: Add early `--webview-host` branch, initialize `SingleInstanceGuard`, `install_crash_handlers`, `enable_high_dpi_awareness`, `MemoryManager`, and `StoreLicenseService`. Route tray Settings and Welcome clicks through `WebViewLauncher`.
- [ ] **T-87: Safeguard mouse hook & state machine locked behaviors**
  - Files: `src/features/mouse_mapper/logic/mouse_mapper_logic.py`, `src/features/mouse_mapper/services/mouse_hook_service.py`
  - Action: Verify and ensure all locked invariants from `CLAUDE.md` remain untouched (RMB hold + scroll UP = panel, scroll DOWN = Alt+Tab, mouse drag = gesture, right-up passthrough, watchdog auto-recovery).
- [ ] **T-88: Update build spec, run automated tests & verify**
  - Files: `RightWheel.spec`, `tests/`
  - Action: Update PyInstaller spec with `ui_dist/` and `locales/` data trees; run unit tests and smoke tests ensuring 100% pass rate.
