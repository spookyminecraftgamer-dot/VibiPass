# VibiPass — Desktop App Build Guide

A secure, local-first password manager. All encryption happens in-browser using
**AES-256-GCM + PBKDF2 (100k iterations)**. Data never leaves your device.

## Project Structure

```
VibiPass/
├── main.py                  ← PyWebView entry point + localStorage bridge
├── requirements.txt
├── vibipass.spec            ← PyInstaller spec (all platforms)
├── build_linux.sh           ← Linux build script
├── build_windows.bat        ← Windows build script
├── build_macos.sh           ← macOS build script
├── vibipass_installer.iss   ← Inno Setup script (Windows .exe installer)
├── html/
│   ├── landing.html
│   ├── signup.html
│   ├── auth.html
│   ├── cred.html
│   └── setting.html
└── assets/
    └── theme/               ← Theme backgrounds and icons
```

## How It Works

`main.py` wraps the HTML UI in a native desktop window via **pywebview**.
A Python `StorageBridge` class is exposed to JavaScript as `window.pywebview.api`,
and a localStorage shim is injected into every page so the existing HTML/JS code
works **without any changes** — it still calls `localStorage.getItem/setItem`, but
those calls are now routed to a local `vibipass_data/store.json` file on disk.

---

## 🐧 Linux (Mint, Ubuntu, Debian, Fedora, Arch…)

### Prerequisites
```bash
# Debian/Ubuntu/Mint
sudo apt update
sudo apt install python3 python3-pip python3-gi gir1.2-webkit2-4.0 libgtk-3-0

# Fedora
sudo dnf install python3 python3-pip webkit2gtk4.0

# Arch
sudo pacman -S python python-pip webkit2gtk
```

### Build
```bash
chmod +x build_linux.sh
./build_linux.sh
```

### Output
| File | Description |
|------|-------------|
| `dist/VibiPass_linux.tar.gz` | Portable – extract and run anywhere |
| `dist/vibipass_1.0_amd64.deb` | Installer for Debian/Ubuntu/Mint |

### Install .deb
```bash
sudo dpkg -i dist/vibipass_1.0_amd64.deb
# Then launch from app menu or run: vibipass
```

### Run portable
```bash
tar -xzf dist/VibiPass_linux.tar.gz
./VibiPass/VibiPass
```

---

## 🪟 Windows (10 / 11)

### Prerequisites
```bat
pip install pywebview pyinstaller pythonnet
```

Optional: Install [Inno Setup 6](https://jrsoftware.org/isdl.php) for a proper `.exe` installer.

### Build
```bat
build_windows.bat
```

### Output
| File | Description |
|------|-------------|
| `dist\VibiPass_windows.zip` | Portable ZIP – extract and run |
| `dist\VibiPass_Setup_1.0.exe` | Windows installer (requires Inno Setup) |

---

## 🍎 macOS (10.13+)

### Prerequisites
```bash
pip install pywebview pyinstaller
xcode-select --install   # if not already installed
```

### Build
```bash
chmod +x build_macos.sh
./build_macos.sh
```

### Output
| File | Description |
|------|-------------|
| `dist/VibiPass.app` | macOS app bundle |
| `dist/VibiPass_1.0.dmg` | Drag-to-install disk image |

**Note:** macOS may show a Gatekeeper warning since the app isn't code-signed.
To bypass: right-click → Open, or run:
```bash
xattr -rd com.apple.quarantine dist/VibiPass.app
```

---

## Run Without Building (Development)

```bash
pip install -r requirements.txt
python main.py
```

---

## User Data Location

Data is stored in `vibipass_data/store.json` **next to the executable**.
All values are already encrypted by the browser-side WebCrypto API before
being written to disk (AES-256-GCM). The Python layer never sees plaintext.

To back up your vault: copy `vibipass_data/store.json`.
To reset: delete `vibipass_data/store.json`.

---

## Security Notes

- Encryption: AES-256-GCM (WebCrypto API)
- Key derivation: PBKDF2-SHA256, 100,000 iterations, random 16-byte salt
- Passwords are hashed before storage; vault is encrypted with your master password
- No network calls — fully offline
- No telemetry, no analytics, no ads
