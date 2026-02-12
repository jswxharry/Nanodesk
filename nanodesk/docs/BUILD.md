# Nanodesk Desktop Build Guide

This guide explains how to build the Nanodesk Desktop application with **embedded Python** - a fully self-contained package that does not require users to have Python installed.

## Overview

Nanodesk Desktop uses a dual-mode architecture:
- **Development mode**: Uses your system Python with installed dependencies
- **Production mode**: Uses embedded Python bundled with the application

## Prerequisites

- Windows 10/11
- Python 3.11+ (for building only)
- PyInstaller: `pip install pyinstaller`
- Inno Setup 6.x (optional, for creating installer)

## Quick Build

### Option 1: One-Click Build (Recommended)

```powershell
# Complete build with embedded Python and installer
.\nanodesk\scripts\build_all.ps1 -Clean

# Or just update the app without rebuilding embedded Python
.\nanodesk\scripts\build_all.ps1
```

Output:
- `dist/Nanodesk/` - Portable version (folder)
- `dist/Nanodesk-Setup-x.x.x.exe` - Installer (if Inno Setup is installed)

### Option 2: Manual Build Steps

```powershell
# Step 1: Prepare embedded Python (one-time)
python .\nanodesk\scripts\prepare_embedded_python.py

# Step 2: Build desktop app
.\nanodesk\scripts\build_desktop.ps1

# Step 3: Create installer (optional)
iscc .\nanodesk\scripts\setup.iss
```

## Architecture

### Embedded Python

The build process downloads and configures [Windows embeddable Python](https://www.python.org/downloads/windows/):

1. Downloads `python-3.11.x-embed-amd64.zip` from python.org
2. Extracts to `build_desktop/embedded_python/`
3. Installs pip and all dependencies
4. Includes in final package at `dist/Nanodesk/python/`

### Runtime Behavior

The `ProcessManager` automatically detects the environment:

```
Priority 1: Embedded Python (dist/Nanodesk/python/python.exe)
         ↓
Priority 2: PyInstaller internal Python (_internal/python.exe)
         ↓
Priority 3: System Python (development mode)
```

See `nanodesk/desktop/core/process_manager.py` for implementation.

## Distribution

### Portable Version

Simply zip the `dist/Nanodesk` folder:

```powershell
Compress-Archive -Path dist\Nanodesk -DestinationPath Nanodesk-Portable.zip
```

Users extract and run `Nanodesk.exe`.

### Installer

The Inno Setup script creates a professional installer:
- Desktop shortcut option
- Start menu entry
- Auto-start option
- Clean uninstall

## Troubleshooting

### Build Issues

**PyInstaller not found:**
```powershell
pip install pyinstaller
```

**Missing dependencies:**
```powershell
pip install -e .
```

**Clean build:**
```powershell
Remove-Item build_desktop, build, dist -Recurse -Force
.\nanodesk\scripts\build_all.ps1 -Clean
```

### Runtime Issues

**Gateway fails to start:**
- Check log file: `%USERPROFILE%\.nanodesk\logs\gateway_*.log`
- Verify embedded Python exists: `dist/Nanodesk/python/python.exe`
- Test manually: `dist\Nanodesk\python\python.exe -m nanodesk.launcher gateway`

**Missing DLLs:**
Ensure pywin32 is installed in embedded Python:
```powershell
.\build_desktop\embedded_python\python.exe -m pip install pywin32
```

## File Structure

```
dist/Nanodesk/
├── Nanodesk.exe          # Main GUI application
├── python/               # Embedded Python
│   ├── python.exe
│   ├── Lib/
│   └── Lib/site-packages/  # nanobot and dependencies
├── _internal/            # PyInstaller files
├── resources/            # App resources
└── EMBEDDED_PYTHON       # Marker file
```

## Size Optimization

The embedded Python includes unnecessary files. You can remove:
- `python\Lib\test\` (test suite)
- `python\Lib\idlelib\` (IDLE)
- `python\Lib\tkinter\` (GUI toolkit, unless needed)
- `*.pdb` files (debug symbols)

Current approximate sizes:
- Embedded Python + nanobot: ~60-80 MB
- Final package: ~70-90 MB
- Installer (compressed): ~50-70 MB

## Customization

### Change Python Version

Edit `prepare_embedded_python.py`:
```python
PYTHON_VERSION = "3.12.0"  # Update version
```

### Add More Dependencies

Edit `prepare_embedded_python.py`:
```python
# In install_dependencies():
subprocess.run([
    str(python_exe), "-m", "pip", "install", 
    "your-package", "--no-warn-script-location"
])
```

### Custom Installer

Edit `setup.iss`:
- Change `MyAppVersion`
- Add license file
- Customize install path
- Add file associations

## CI/CD

For automated builds (GitHub Actions example):

```yaml
name: Build
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e . pyinstaller
      - name: Build
        run: |
          python nanodesk/scripts/prepare_embedded_python.py
          .\nanodesk\scripts\build_desktop.ps1
      - name: Upload
        uses: actions/upload-artifact@v3
        with:
          name: Nanodesk
          path: dist/Nanodesk
```

## License

The built application includes:
- Nanodesk (your license)
- Python (PSF License)
- Third-party packages (various licenses)

Ensure compliance with all included licenses when distributing.
