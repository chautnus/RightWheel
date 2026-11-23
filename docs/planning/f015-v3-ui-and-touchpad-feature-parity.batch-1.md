# Batch 1: Core Systems, Action Dispatcher & Licensing Port

## Context
Port foundational system kernel, memory compaction manager, trial licensing daemon, multi-language i18n, Schema v4 unified profiles, and 8-action dispatcher from Touchpad Gesture into RightWheel (`src/core/` and `src/features/action_dispatcher/`).

## Tasks
- [ ] **T-76: Port core infrastructure services** (`app_paths.py`, `single_instance.py`, `crash_reporter.py`)
- [ ] **T-77: Port memory manager & store trial licensing daemon** (`memory_manager.py`, `store_license_service.py`)
- [ ] **T-78: Port multi-language i18n system & locale dictionaries** (`i18n.py`, `locales/*.json`)
- [ ] **T-79: Port Unified Profile Schema v4 & foreground application discovery** (`config_service.py`, `profile_service.py`, `app_discovery.py`)
- [ ] **T-80: Port 8-Action Dispatcher & Macro Execution Engine** (`action_dispatcher/*`)

## Expected Changes
- `src/core/app_paths.py`: config root `%APPDATA%/RightWheel`, logging utilities.
- `src/core/single_instance.py`: Mutex single instance guard with window summon.
- `src/core/crash_reporter.py`: Global exception hooks.
- `src/core/memory_manager.py`: Compaction thread calling `EmptyWorkingSet` and `gc.collect(2)`.
- `src/core/store_license_service.py`: 30-day trial countdown and background daemon.
- `src/core/i18n.py` and `src/core/locales/`: 7 language files (`en.json`, `vi.json`, `fr.json`, `es.json`, `it.json`, `pt.json`, `id.json`).
- `src/core/config_service.py` and `profile_service.py`: Schema v4 profiles and foreground matching.
- `src/features/action_dispatcher/`: 8 action types, direct browser launch, PrintScreen SysRq fix.

## Verification
- Unit test imports of all core modules.
- Memory manager compaction smoke test.
- License service trial countdown assertion.
- Action dispatcher type evaluation test.
