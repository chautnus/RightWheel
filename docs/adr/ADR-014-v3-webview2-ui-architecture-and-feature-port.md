# ADR-014: Modern V3 WebView2 UI Architecture and Feature Parity Port

## Status
Accepted

## Date
2026-11-22

## Context
RightWheel has operated with a legacy Tkinter-based settings interface that was monolithic and difficult to maintain across high-DPI displays and modern design paradigms. Concurrently, Touchpad Gesture V3 developed a modern 2-tier architecture using React 19, Tailwind CSS, Lucide Icons, and Edge WebView2 embedded via an isolated subprocess. Touchpad Gesture also refined core infrastructure modules: unified profiles (Schema v4), an 8-action dispatcher with robust browser launching and clipboard retry, active memory compaction reducing idle RAM to ~40MB, and a 30-day trial licensing daemon.

RightWheel needs these capabilities to provide a desktop experience on par with Touchpad Gesture while strictly safeguarding its core mouse-hook state machine and locked behaviors.

## Decisions

### 1. 2-Tier Modular UI Architecture
- UI Studio in `c:\dev\ui-studio` maintains the design system and React frontend for both applications.
- A dedicated Vite mode `rightwheel-v3` builds static assets to `dist-rightwheel-v3`, synced to `src/ui_dist`.
- PyWebView spawns an isolated Edge Chromium host process (`--webview-host --view <view>`), leaving the main application process lightweight and avoiding loading WebView2 libraries into background daemon memory.

### 2. Dual-Engine Fallback Strategy
- The application defaults to WebView2 for modern, fluid interactions.
- If WebView2 runtime is absent or if the user explicitly configures `ui_engine: "tkinter"` in General settings, `WebViewLauncher` falls back cleanly to the existing Tkinter UI windows without breaking app functionality.

### 3. Unified Profile Schema v4 & Foreground App Tracking
- Profiles are unified into a single schema: `id`, `name`, `is_default`, `match` (rules by `exe`, `title_contains`, or `class_name`), `commands`, and `gestures`.
- Win32 `GetForegroundWindow` checks match rules; unmatched bindings automatically inherit from the Global Profile.

### 4. Robust 8-Action Dispatcher
- Unified dispatcher handles: `KEY_COMBO`, `RUN_APP`, `OPEN_URL`, `RUN_SHELL`, `FOLDER`, `SEQUENCE`, `TYPE_TEXT`, and `WEB_CLIP`.
- Eliminates Explorer COM/DDE hangs on URL opens by launching the default browser executable directly or using `rundll32 url.dll,FileProtocolHandler`.
- Fixes PrintScreen double-capture by zeroing out `wScan` for `VK_SNAPSHOT` (`0x2C`) to suppress the hardware `0x54 SysRq` scan code.
- Sequence macros execute with 2-tier foreground restoration and clipboard polling retries.

### 5. Active Memory Management
- A background workerCompaction thread triggers `gc.collect(2)` and calls `SetProcessWorkingSetSize(-1, -1)` + `EmptyWorkingSet()` periodically (every 300s or after 30s of inactivity), keeping memory usage around ~40MB RAM.

### 6. Preservation of Mousehotkey Locked Behaviors
- The low-level mouse hook (`MouseHookService`), hook watchdog recovery (`WM_APP_REHOOK`), and mouse mapper state machine (`_on_right_down`, `_on_move`, `_on_scroll`, `_on_right_up`) remain untouched and authoritative.

## Consequences
- **Positive**: State-of-the-art UI, high-DPI crispness, rich macro/WebClip capabilities, contextual app profiles, rock-solid memory stability, and seamless Tkinter fallback.
- **Trade-off**: Requires Node/Vite build step when altering UI components in `ui-studio`, and adds `pywebview` as an optional dependency for the rich UI.
