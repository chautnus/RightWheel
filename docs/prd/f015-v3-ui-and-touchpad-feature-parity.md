# PRD: f015-v3-ui-and-touchpad-feature-parity — V3 Modern WebView2 UI and Touchpad Gesture Feature Parity Port

## 1. Executive Summary
Port all state-of-the-art capabilities, architecture, and user experience developed in Touchpad Gesture V3 into RightWheel (Mousehotkey). This elevates RightWheel from a legacy Tkinter utility to a modern, high-performance desktop application featuring:
1. Modern Fluent UI V3 (React 19 + Tailwind CSS + Lucide Icons + Edge WebView2 Chromium runtime).
2. Bento Grid Landing Page (`WelcomeView.tsx`) with 7-language immediate switching and trial status.
3. Dual-Engine Architecture (Modern WebView2 UI with automatic & manual Tkinter Fallback).
4. Unified Profile Schema v4 with auto foreground window detection and global fallback inheritance.
5. 8-Action Dispatcher & Macro Execution Engine (KeyCombo with PrintScreen fix, App, URL with direct browser launch, Shell, Folder, Sequence Macro with clipboard retry, TypeText, WebClip AI).
6. Idle Memory Compaction Manager (~40 MB Working Set RAM, 0% CPU).
7. 30-Day Store Trial License Daemon with countdown and simulation testing mode.
8. Preservation of all RightWheel locked behaviors (mouse hook invariants, RMB dual-mode scroll, sleep recovery watchdog).

## 2. User Stories
- **US-44 (Modern UI)**: As a user, I want a modern Fluent Dark interface with smooth animations, clear typography, and a Bento-style landing page so that configuring mouse shortcuts feels premium.
- **US-45 (App-Specific Profiles)**: As a power user, I want custom shortcuts and mouse gestures tailored to each active application (e.g. VS Code, Chrome, Photoshop) with automatic fallback to global defaults.
- **US-46 (Advanced Action Types & Macros)**: As a user, I want to execute multi-step macros, WebClip AI prompts, synthetic text typing, and direct browser URLs reliably without system hangs.
- **US-47 (Hardware Key Recorder)**: As a user, I want a 1:1 hardware key recorder modal supporting modifier toggles (Ctrl/Shift/Alt/Win) and direct system buttons (PrintScreen, arrows, Tab, Home, End, PgUp/Dn) without double-capture bugs.
- **US-48 (Dual UI Engine)**: As a user with restricted environments or without WebView2, I want RightWheel to automatically fall back to Tkinter, or allow me to toggle my preferred engine in settings.
- **US-49 (System Health & Licensing)**: As a user, I want RightWheel to consume minimal RAM (~40MB), never leak memory after long running times, and provide a clear 30-day trial countdown.

## 3. Technical Requirements
- **Runtime**: Python 3.14 on Windows 10 & 11.
- **Frontend**: React 19, Tailwind CSS v4, Lucide Icons, Vite 6, pywebview Edge Chromium.
- **Memory Footprint**: Target < 50MB Working Set RAM at idle via `memory_manager.py`.
- **Latency**: Key combo and macro dispatch lag < 1ms.
- **Compatibility**: Preserve full backwards compatibility with existing user configuration and Tkinter fallback.

## 4. Verification Gates
- All existing unit tests pass.
- New tests for action dispatcher, profile resolution, license service, and bridge API pass.
- Vite build completes cleanly without TypeScript errors.
- Both WebView2 host mode and Tkinter fallback initialize properly.
