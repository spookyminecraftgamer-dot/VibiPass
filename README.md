# 🔐 VibiPass

**A cross-platform secure password manager** with layered encryption, built with HTML, CSS, JavaScript, and PyWebView. All encryption happens locally on your device—your data never leaves your computer.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20Android-blue.svg)](https://github.com/spookyminecraftgamer-dot/VibiPass)
[![Security](https://img.shields.io/badge/Security-AES--256--GCM-green.svg)](https://github.com/spookyminecraftgamer-dot/VibiPass)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🔒 Layered Password Protection** | Multi-layer security with master password + PIN authentication |
| **🤖 CAPTCHA Verification** | Built-in CAPTCHA to prevent unauthorized access attempts |
| **🎨 Customizable Themes** | Multiple theme options to personalize your experience |
| **🔐 Local Encryption** | AES-256-GCM encryption with random salts—no cloud storage |
| **⚡ High-Iteration Hashing** | PBKDF2-SHA256 with 100,000+ iterations for maximum security |
| **💾 Offline-First** | Works completely offline—no internet connection required |
| **📱 Cross-Platform** | Windows (.exe), macOS (.dmg), Linux (.deb), and Android (.apk) |
| **🎯 Zero Telemetry** | No tracking, no analytics, no ads—complete privacy |
| **⚙️ Password Generator** | Create strong, random passwords with customizable options |
| **🔄 Sync-Ready** | Architecture supports future encrypted sync capabilities |

---

## 🛠️ Tech Stack

### Frontend
- **HTML5** - Semantic markup and structure
- **CSS3** - Responsive design with custom themes
- **JavaScript (ES6+)** - Core application logic and encryption

### Backend & Runtime
- **PyWebView** - Cross-platform desktop application wrapper
- **Python 3.8+** - Backend services and file management
- **PyInstaller** - Executable packaging for all platforms

### Security & Encryption
- **Web Crypto API** - AES-256-GCM encryption
- **PBKDF2-SHA256** - Key derivation with high iteration count
- **Random Salt Generation** - Unique salts for each encryption operation

### Build & Distribution
- **PyInstaller** - Bundle Python + HTML/CSS/JS into executables
- **Inno Setup** - Windows installer (.exe)
- **Linux Packaging** - DEB/RPM support
- **APK Tooling** - Android package generation

---

## 🔒 Security Architecture

### Encryption Pipeline

```
User Master Password
         ↓
   [PBKDF2-SHA256]
   (100,000+ iterations)
         ↓
   Derived Key (256-bit)
         ↓
   [AES-256-GCM Encryption]
         ↓
   Encrypted Vault (Local Storage)
   └─ Never transmitted over network
   └─ Only stored locally on device
```

### Security Features

**🔐 Master Password Protection**
- Password hashed using PBKDF2-SHA256 with 100,000+ iterations
- Random 16-byte salt generated for each password
- Salt stored alongside encrypted data

**🤖 Multi-Factor Verification**
- Primary authentication via master password
- Secondary verification through CAPTCHA challenge
- Optional PIN code protection layer

**💾 Local-First Encryption**
- All encryption/decryption happens in the browser using Web Crypto API
- Python backend never sees plaintext passwords
- Encrypted data stored in `vibipass_data/store.json` on your device

**🔄 Random Salt Implementation**
- Unique random salt generated for each credential entry
- Prevents rainbow table attacks
- Salt securely stored with encrypted credentials

**⚡ High-Entropy Key Derivation**
- PBKDF2 with 100,000+ iterations to slow down brute-force attacks
- Configurable iteration count for future security updates
- SHA-256 hash function for maximum security

**🛡️ Zero-Knowledge Architecture**
- No server-side processing of passwords
- No transmission of sensitive data
- Complete offline capability

---

## 📦 Installation

### Windows (.exe)

**Option 1: Installer (Recommended)**
1. Download `VibiPass_Setup_1.0.exe` from [Releases](https://github.com/spookyminecraftgamer-dot/VibiPass/releases)
2. Run the installer
3. Follow the setup wizard
4. Launch VibiPass from your Start Menu

**Option 2: Portable**
1. Download `VibiPass_windows.zip`
2. Extract to your desired location
3. Run `VibiPass.exe`

### macOS (.dmg)

1. Download `VibiPass_1.0.dmg` from [Releases](https://github.com/spookyminecraftgamer-dot/VibiPass/releases)
2. Open the `.dmg` file
3. Drag **VibiPass.app** to Applications folder
4. Launch from Applications or Spotlight search

*Note: If you see a Gatekeeper warning, right-click the app and select "Open"*

### Linux (.deb)

**Ubuntu, Debian, Linux Mint:**
```bash
sudo dpkg -i vibipass_1.0_amd64.deb
vibipass
```

**Fedora/RHEL/CentOS:**
```bash
sudo rpm -i vibipass_1.0_x86_64.rpm
vibipass
```

**Portable (Any Distribution):**
```bash
tar -xzf VibiPass_linux.tar.gz
./VibiPass/VibiPass
```

### Android (.apk)

1. Enable "Unknown Sources" in Settings → Security
2. Download `VibiPass_1.0.apk` from [Releases](https://github.com/spookyminecraftgamer-dot/VibiPass/releases)
3. Tap the APK file to install
4. Launch from your app drawer

---

## 📸 Screenshots

### Authentication Screen
![VibiPass Login](https://via.placeholder.com/400x300?text=VibiPass+Login+Screen)

### Password Manager Dashboard
![VibiPass Dashboard](https://via.placeholder.com/400x300?text=VibiPass+Dashboard)

### Settings & Themes
![VibiPass Settings](https://via.placeholder.com/400x300?text=VibiPass+Settings)

---

## 🚀 Getting Started (Development)

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Clone & Setup

```bash
git clone https://github.com/spookyminecraftgamer-dot/VibiPass.git
cd VibiPass
pip install -r requirements.txt
```

### Run Development Version

```bash
python main.py
```

### Build for Your Platform

**Linux:**
```bash
chmod +x build_linux.sh
./build_linux.sh
```

**Windows:**
```batch
build_windows.bat
```

**macOS:**
```bash
chmod +x build_macos.sh
./build_macos.sh
```

---

## 📁 Project Structure

```
VibiPass/
├── main.py                      # PyWebView entry point
├── requirements.txt             # Python dependencies
├── build_linux.sh              # Linux build script
├── build_windows.bat           # Windows build script
├── build_macos.sh              # macOS build script
├── vibipass.spec               # PyInstaller configuration
├── vibipass_installer.iss      # Windows installer config
├── html/                       # Frontend application
│   ├── landing.html
│   ├── signup.html
│   ├── auth.html
│   ├── cred.html
│   └── settings.html
├── assets/                     # UI assets
│   ├── theme/                  # Theme files
│   └── icons/                  # Application icons
└── vibipass_data/              # User data storage (auto-created)
    └── store.json              # Encrypted vault
```

---

## 🗺️ Roadmap

### Version 1.1 (Current)
- ✅ Core password management
- ✅ AES-256-GCM encryption
- ✅ Layered authentication
- ✅ CAPTCHA verification
- 🚧 Theme customization
- 🚧 Android app optimization

### Version 1.2 (Q3 2026)
- Password strength indicator
- Import/Export functionality
- Auto-fill browser integration
- Biometric authentication (fingerprint/face)
- Dark mode improvements

### Version 1.5 (Q4 2026)
- End-to-end encrypted cloud sync (optional)
- Mobile app refinements
- Advanced search & filtering
- Multi-vault support
- Duplicate password detection

### Version 2.0 (2027)
- Cross-device sync with end-to-end encryption
- Team vault sharing (enterprise)
- Advanced audit logging
- API for third-party integrations
- Hardware security key support

---

## 🤝 Contributing

We welcome contributions! Whether it's bug fixes, feature requests, or documentation improvements:

1. **Fork** this repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use consistent naming conventions
- Add comments for complex logic
- Test on multiple platforms before submitting

---

## 🐛 Bug Reports & Support

Found an issue? We'd love to hear about it!

- **Report a Bug**: [GitHub Issues](https://github.com/spookyminecraftgamer-dot/VibiPass/issues)
- **Feature Request**: [GitHub Discussions](https://github.com/spookyminecraftgamer-dot/VibiPass/discussions)
- **Email**: [security concerns only]

### Security Concerns
If you discover a security vulnerability, please email us privately instead of using the issue tracker.

---

## 📝 License

VibiPass is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 spookyminecraftgamer-dot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🎯 Why VibiPass?

- **Privacy First** - Your passwords stay on your device
- **Military-Grade Encryption** - AES-256-GCM security
- **Completely Free** - Open source with no premium features locked behind paywalls
- **Works Offline** - No internet required
- **Multiple Platforms** - Seamless experience across Windows, macOS, Linux, and Android
- **Active Development** - Regular updates and security improvements

---

## 📞 Community & Support

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community discussions
- **Star the Repo**: Show your support by starring ⭐

---

## 🙏 Acknowledgments

Built with ❤️ using:
- [PyWebView](https://pywebview.kivy.org/) for desktop integration
- [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API) for encryption
- The open-source community for inspiration and support

---

**Stay secure. Stay private. Use VibiPass. 🔐**

