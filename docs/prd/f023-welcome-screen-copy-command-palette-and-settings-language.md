# PRD — f020-welcome-screen-copy-command-palette-and-settings-language

## 1. Objective
Refine the Welcome screen Bento highlights to align with the core product pillars, empower users to configure their Command Palette directly in the Step 1/2 onboarding wizard, and provide a persistent language selector on the Settings screen.

## 2. User Stories
- **US-059**: As a user opening RightWheel for the first time, I want the 3 main cards on the welcome screen to clearly articulate:
  1. Hold Right mouse, Draw gestures, Get task done.
  2. Unlimited quick command, adapt by application.
  3. A series of action in one click.
  Both in Vietnamese, English, and other supported locales.
- **US-060**: As a user walking through the Welcome setup wizard (Step 1/2), I want to view, customize, and add commands to my Quick Command Palette in addition to mouse gestures, so that my shortcut matrix is configured before I start using the app.
- **US-061**: As a user navigating the Settings screen, I want a prominent language selection dropdown available from any tab, so that I can easily switch to my preferred language without digging into sub-tabs.

## 3. Acceptance Criteria
1. Welcome screen Bento cards display the 3 rewritten pillars in professional phrasing across all 7 supported languages (`vi`, `en`, `fr`, `es`, `it`, `pt`, `id`).
2. Step 1/2 of `WizardView.tsx` provides a seamless tab switcher between "Cử chỉ vẽ & Con lăn" and "Bảng lệnh nhanh (Command Palette)", allowing users to inspect and edit commands using `CommandEditorModal`.
3. `SettingsView.tsx` sidebar contains a compact, elegant language selector with Globe icon, updating the entire UI and translations in real time.
4. UI builds cleanly with `npm --prefix "C:\dev\ui-studio" run build:rightwheel-v3` and syncs to `src/ui_dist/`.
5. All test suites pass.
