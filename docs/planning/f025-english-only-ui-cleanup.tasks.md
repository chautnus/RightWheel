# Tasks — f025-english-only-ui-cleanup

## Epic: [F-025] English-Only Runtime & Hardcoded Vietnamese UI Cleanup
- **US-068**: Consistent English-only UI across all windows & overlays
- **US-069**: Hide non-English language selectors
- **US-070**: Migrate legacy default Vietnamese gesture descriptions to English

| ID     | Task | Story  | Estimate | Priority | Deps   | Status |
|--------|------|--------|----------|----------|--------|--------|
| T-0136 | Lock i18n runtime (`src/core/i18n.py`, `src/features/i18n/__init__.py`) and `bridge_api.py` to English (`"en"`) and expose only English in `SUPPORTED_LANGUAGES` / `available()` | US-069 | 1h | P0 | - | todo |
| T-0137 | Translate `GESTURE_DESCRIPTIONS`, `DEFAULT_MOUSE_GESTURES`, `DEFAULT_COMMANDS` in `src/core/config_service.py` and normalize legacy default Vietnamese descriptions on load | US-070 | 1h | P0 | T-0136 | todo |
| T-0138 | Clean up hardcoded Vietnamese in `src/main.py` (`GestureGuideOverlay`), `tray_ui.py`, `single_instance.py`, and Tkinter UI (`general_tab.py`, `gestures_tab.py`, `intent_picker_dialog.py`, `reference_tab.py`) | US-068, US-069 | 1h | P0 | T-0136 | todo |
| T-0139 | Hide language selectors & translate Welcome/Wizard/Settings views (`WelcomeView.tsx`, `WizardView.tsx`, `SettingsView.tsx`, `GeneralTab.tsx`, `mock.ts`) | US-068, US-069 | 1h | P0 | T-0136 | todo |
| T-0140 | Replace all remaining Vietnamese fallbacks/presets/labels in React modals & helpers (`actionDescriber.ts`, `GestureEditorModal.tsx`, `CommandEditorModal.tsx`, `CommandsTab.tsx`, `GesturesTab.tsx`, `FolderEditorModal.tsx`, `KeyRecorderModal.tsx`, `MacroBuilderSection.tsx`, `ProfileRulesModal.tsx`, `ProfileWorkspace.tsx`, `ReferenceTab.tsx`, `TouchpadVisualizer.tsx`) | US-068 | 1.5h | P0 | T-0139 | todo |
| T-0141 | Update unit tests in `tests/test_v3_feature_parity.py`, run `build_v3_ui.ps1`, run `pytest`, compile `dist/RightWheel.exe`, and push | US-068, US-069, US-070 | 0.5h | P0 | T-0137, T-0138, T-0140 | todo |
