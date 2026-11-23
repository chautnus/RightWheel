# Context: f015-v3-ui-and-touchpad-feature-parity

## Elicitation — 2026-11-22

Problem: RightWheel (Mousehotkey) uses an older Tkinter UI with separate scattered dialogs, limited action types, legacy license logic, and lacks modern features (Fluent V3 2-tier architecture, Bento Landing Page, unified Schema v4 profiles with fallback inheritance, 8 action types including WebClip and direct browser launch, idle memory compaction, 30-day trial store daemon, and dual-engine WebView2/Tkinter switching) that were perfected in Touchpad Gesture.
Goal: Port all advanced backend services, action dispatcher types, unified profiles, memory management, trial licensing, i18n locales, and the modern React 19 + Tailwind CSS + WebView2 UI Studio V3 interface into RightWheel while strictly maintaining Mousehotkey's mouse hook and state machine locked invariants.
Scope IN:
- Port Core Infrastructure: `app_paths.py`, `single_instance.py`, `crash_reporter.py`, `memory_manager.py` (idle compaction ~40MB RAM), `store_license_service.py` (30-day trial daemon), `i18n.py` + 7 locale JSON files.
- Port Action Dispatcher: 8 action types (KEY_COMBO with SysRq fix, RUN_APP, OPEN_URL with direct browser launch, RUN_SHELL, FOLDER, SEQUENCE macro runner with clipboard retry, TYPE_TEXT, WEB_CLIP).
- Port Unified Profiles (Schema v4): Global + App profiles, active foreground app detection, app discovery.
- Port UI Studio V3 Frontend: New project `rightwheel-v3` in `C:\dev\ui-studio` with Bento Welcome landing page, Settings view with Profile workspace, Shortcuts/Commands tab, Mouse Gestures tab, General tab (with UI engine switch), Reference tab, KeyRecorderModal (1:1 hardware capture), and Vite build script.
- Port WebView2 Host & Bridge API: Isolated `--webview-host` STA process via `pywebview`, bidirectional IPC bridge, and launcher with seamless Tkinter fallback.
- Integrate into `main.py` and System Tray while preserving `mouse_mapper_logic.py` locked invariants.
Scope OUT:
- Touchpad-specific HID raw input captures (`python_rawinput_backend.py`) and touchpad registry guard (`registry_guard.py`) — RightWheel is mouse-based.
Users: Windows 10/11 desktop power users using mouse shortcut launching and gesture navigation.
Stories: US-44, US-45, US-46, US-47, US-48, US-49.
Constraints: Python 3.14+, Win32 API, WebView2 Chromium runtime with Tkinter fallback, 0% CPU at idle, ~40MB Working Set RAM.
NFR: Startup latency < 1.5s, 0ms input dispatch lag, 0 unhandled memory leaks.

---

## PRD — 2026-11-22

Path: docs/prd/f015-v3-ui-and-touchpad-feature-parity.md
Version: 1.0
Summary: Complete port of Touchpad Gesture V3 modern Fluent UI, Action Dispatcher, Unified Profiles Schema v4, Memory Manager, Trial Licensing, and WebView2/Tkinter Dual-Engine into RightWheel.

---

## Architecture — 2026-11-22

Pattern: 2-Tier Modular Desktop Architecture (Host Process + WebView2 Subprocess + Core Kernel Services + Tkinter Fallback Engine)
ADR-014: Modern V3 WebView2 UI Architecture and Touchpad Gesture Feature Parity Port → docs/adr/ADR-014-v3-webview2-ui-architecture-and-feature-port.md

---

## Tasks — 2026-11-22

Total: 13 tasks across 3 batches.
Batch 1: Core Systems, Action Dispatcher & Licensing Port (T-76 to T-80)
Batch 2: UI Studio & Modern V3 WebView2 Frontend Port (T-81 to T-84)
Batch 3: Host Bridge, Main Integration, Packaging & Verification (T-85 to T-88)
