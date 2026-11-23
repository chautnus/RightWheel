# Context — f020-welcome-screen-copy-command-palette-and-settings-language

## User Request
1. Sửa 3 ý chính ở màn hình chào mừng:
   - 1. Hold Right mouse, Draw gestures, Get task done.
   - 2. Unlimited quick command, adapt by application
   - 3. A series of action in one click
   Viết lại cho phù hợp.
2. Bổ sung cấu hình command palette ở phần chào mừng, ở step 1/2.
3. Ở màn hình settings cần có lựa chọn ngôn ngữ.

## Analysis & Current State
1. **Welcome Screen (`WelcomeView.tsx` & `src/core/i18n.py`)**:
   - Currently, 3 Bento cards feature "Right Click + Scroll UP", "Right Click & Draw Gesture", and "Right Click + Scroll DOWN".
   - Need to reformulate into 3 core value propositions across all 7 languages:
     - Card 1: Draw Gestures — "Giữ chuột phải & Vẽ cử chỉ" / "Hold Right Mouse & Draw Gestures" (Hold Right mouse, Draw gestures, Get task done).
     - Card 2: Quick Command Palette & Per-App Adaptation — "Lệnh nhanh không giới hạn" / "Unlimited Quick Commands & App Adaptation" (Unlimited quick command, adapt by application).
     - Card 3: Sequential Multi-Action Macros — "Chuỗi tác vụ 1 cú nhấp" / "A Series of Actions in One Click" (A series of action in one click).
2. **Step 1/2 Setup Wizard (`WizardView.tsx`)**:
   - Currently, Step 1/2 (`step === 0`) only shows mouse/hook status and the `globalGestures` list.
   - Users cannot configure or preview the Command Palette (`globalProfile.commands`) during the onboarding wizard.
   - Add a segmented toggle / sub-tabs inside Step 1/2:
     - Tab A: `🖱️ Cử chỉ vẽ & Con lăn (Mouse Gestures)`
     - Tab B: `⚡ Bảng lệnh nhanh (Command Palette)`
     - When Tab B is selected, render the command items with type badges, labels, action summaries, and descriptions.
     - Allow editing via `CommandEditorModal`, adding new commands, and reordering/deleting with immediate persistence via `bridgeClient.saveProfileCommands`.
3. **Settings Screen Language Selector (`SettingsView.tsx`)**:
   - Currently, language selection is only available in `GeneralTab.tsx`. Since `SettingsView` defaults to `profiles` tab, the language selector is hidden from view upon opening settings.
   - Add a persistent Language selector with `<Globe />` icon directly in the `SettingsView` sidebar (under branding/status badges) so users can change language at any time from any tab.
