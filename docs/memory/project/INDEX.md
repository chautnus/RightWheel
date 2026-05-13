# Project Memory Index

| id | summary | tags | status | file |
|----|---------|------|--------|------|
| proj_architecture_20260430 | Core architectural decisions for ctypes hook, state machine, and UI threading | architecture, ctypes, hook | active | [architecture.md](architecture.md) |
| proj_bug_fixes_20260430 | Root causes and fixes for all critical bugs found during v1→v2 development | bugs, ctypes, alt-tab | active | [bug_fixes.md](bug_fixes.md) |
| proj_key_recorder_build_fix_20260506 | Added key recorder dialog for capturing shortcuts; fixed tkinter missing from PyInstaller build | settings, tkinter, pyinstaller | active | [key_recorder_and_build_fix.md](key_recorder_and_build_fix.md) |
| proj_focus_restore_fix_20260507 | SetForegroundWindow must be called before hide() while process is still foreground — shortcut fire fix | focus, SendInput, overrideredirect | active | [bug_fixes.md](bug_fixes.md) |
| proj_context_aware_profiles_20260507 | Schema v2 + window detection + profile CRUD UI — different shortcut sets per active application | profiles, config-v2, window-detection, ui | active | [context_aware_profiles.md](context_aware_profiles.md) |
| proj_ui_v2_5_redesign_20260507 | Welcome/onboarding screen, Windows startup toggle, Settings UI redesign với ttk.Notebook và folder editor dialog | ui, welcome, startup, settings, tkinter | active | [ui_v2_5_redesign.md](ui_v2_5_redesign.md) |
| proj_i18n_rename_rightwheel_20260508 | Full i18n system (9 languages) + rename MouseHotkey→RightWheel + license UI localized + language selector in settings + build RightWheel.exe v2.9.0 | i18n, rename, rightwheel, localization, license | active | [i18n_rename_rightwheel_v2_9_0.md](i18n_rename_rightwheel_v2_9_0.md) |
| proj_panel_scroll_behavior_20260513 | Confirmed correct scroll+panel interaction flow locked at v2.10.7. Do not change without explicit user approval. | panel, scroll, state-machine, ux, locked | active | [panel_scroll_behavior.md](panel_scroll_behavior.md) |
