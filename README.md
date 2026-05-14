# RightWheel — Mouse Shortcut Launcher for Windows

> Hold right-click + scroll to instantly launch apps, run commands, trigger shortcuts, and open URLs — without touching the keyboard.

[![Release](https://img.shields.io/github/v/release/chautnus/RightWheel?label=version&color=0078d4)](https://github.com/chautnus/RightWheel/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-informational)](https://github.com/chautnus/RightWheel/releases/latest)
[![Download](https://img.shields.io/github/downloads/chautnus/RightWheel/total?color=16825d&label=downloads)](https://github.com/chautnus/RightWheel/releases/latest)

**🌐 Website & download:** [chautnus.github.io/RightWheel](https://chautnus.github.io/RightWheel/)

![RightWheel demo](https://chautnus.github.io/RightWheel/og-image.png)

---

## What is RightWheel?

RightWheel is a **portable Windows utility** that turns your mouse into a shortcut panel.  
Hold the right mouse button, scroll up or down, and a radial menu appears — pick an item to launch it instantly.

No installation needed. One `.exe` file. Runs in the system tray.

---

## Features

- 🖱️ **Mouse-first UX** — hold right-click + scroll to open the panel; hover folders to auto-expand
- ⌨️ **Keyboard shortcuts** — trigger any key combo (`ctrl+shift+v`, `win+d`, etc.)
- 🚀 **App launcher** — open any `.exe` with optional arguments
- 🌐 **URL shortcuts** — open links in your default browser
- ▶ **Shell commands** — run any `cmd.exe` command directly
- 📁 **Folders** — group shortcuts into submenus; hover to open in 400 ms
- ⬇ **Import templates** — load pre-built shortcut sets from JSON files
- 🌍 **9 languages** — English, Vietnamese, Chinese, Japanese, Korean, French, German, Spanish, Portuguese
- 🔒 **License system** — 30-day free trial via LemonSqueezy
- ⚡ **Portable** — single `.exe`, no installer, no admin rights needed

---

## Installation

1. Go to [**Releases**](https://github.com/chautnus/RightWheel/releases/latest)
2. Download `RightWheel.exe`
3. Double-click to run — it appears in your system tray

> **Windows SmartScreen warning?** Click "More info" → "Run anyway". The app is unsigned but safe.  
> If you prefer not to do this, compile from source (see below).

---

## How It Works

| Action | Result |
|---|---|
| Hold right-click + scroll up/down | Open panel, navigate items |
| Release right-click | Select highlighted item |
| Hold right-click + scroll to folder | Hover 400 ms → auto-open subfolder |
| `Escape` or click away | Close panel |
| Number keys `0–9` | Jump to item directly |

---

## Adding Shortcuts

Right-click the tray icon → **Settings** to manage your shortcuts:

- **Shortcut** — any key combo (`ctrl+c`, `win+shift+s`, `f5`, …)
- **App** — browse to any `.exe`
- **URL** — any `https://` link
- **Command** — any shell command (`git pull`, `npm run dev`, …)
- **Folder** — group items into a submenu

You can also **import a template** (`.json`) to populate a full set of shortcuts at once. See [`templates/`](templates/) for examples.

---

## Build from Source

```bash
git clone https://github.com/chautnus/RightWheel.git
cd RightWheel
pip install -r requirements.txt
python src/main.py
```

To build the `.exe`:

```bash
python -m PyInstaller RightWheel.spec --noconfirm
# Output: dist/RightWheel.exe
```

---

## Pricing

| Plan | Price |
|---|---|
| Free trial | 30 days, full features |
| License | $5.99 one-time |

Purchase at [rightwheel.lemonsqueezy.com](https://rightwheel.lemonsqueezy.com) — enter your key in **Settings → License**.

---

## License

Source code: [MIT](LICENSE)  
Binary release: commercial — free 30-day trial, $5.99 for a perpetual license.
