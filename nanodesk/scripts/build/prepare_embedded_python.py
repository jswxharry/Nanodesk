#!/usr/bin/env python3
"""
Prepare embedded Python for Nanodesk Desktop build.
This downloads and configures Windows embeddable Python with all dependencies.
"""
import os
import sys
import shutil
import urllib.request
import zipfile
import subprocess
from pathlib import Path

PYTHON_VERSION = "3.11.9"
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"


def download_file(url: str, dest: Path, desc: str = "Downloading") -> bool:
    """Download file with progress."""
    if dest.exists():
        print(f"  {dest.name} already exists, skipping download")
        return True
    
    print(f"  {desc}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"  Downloaded: {dest.name}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def extract_zip(zip_path: Path, dest_dir: Path) -> bool:
    """Extract zip file."""
    print(f"  Extracting {zip_path.name}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(dest_dir)
        print(f"  Extracted to: {dest_dir}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def enable_site_packages(python_dir: Path) -> bool:
    """Enable site-packages in pythonxx._pth file."""
    pth_files = list(python_dir.glob("python*._pth"))
    if not pth_files:
        print("  Warning: No .pth file found")
        return False
    
    pth_file = pth_files[0]
    content = pth_file.read_text()
    
    # Uncomment import site
    if "#import site" in content:
        content = content.replace("#import site", "import site")
        pth_file.write_text(content)
        print(f"  Enabled site-packages in {pth_file.name}")
        return True
    
    return True


def install_pip(python_exe: Path) -> bool:
    """Install pip in embedded Python."""
    get_pip = python_exe.parent / "get-pip.py"
    
    # Download get-pip.py if not exists
    if not get_pip.exists():
        print("  Downloading get-pip.py...")
        if not download_file(
            "https://bootstrap.pypa.io/get-pip.py",
            get_pip,
            "Downloading get-pip.py"
        ):
            return False
    
    # Install pip
    print("  Installing pip...")
    result = subprocess.run(
        [str(python_exe), str(get_pip), "--no-warn-script-location"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"  Error installing pip: {result.stderr}")
        return False
    
    print("  Pip installed successfully")
    return True


def install_dependencies(python_exe: Path, project_root: Path) -> bool:
    """Install nanobot and dependencies."""
    print("  Installing nanobot-ai and dependencies...")
    print("  This may take a few minutes...")
    
    # Upgrade pip first
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "--no-warn-script-location"],
        capture_output=True
    )
    
    # Install build tools first (required for building nanobot from source)
    print("  Installing build tools (hatchling)...")
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "hatchling", "--no-warn-script-location"],
        capture_output=True
    )
    
    # Install nanobot from project
    result = subprocess.run(
        [str(python_exe), "-m", "pip", "install", str(project_root), "--no-warn-script-location"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        return False
    
    # Install additional Windows dependencies
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "pywin32", "--no-warn-script-location"],
        capture_output=True
    )
    
    print("  Dependencies installed successfully")
    return True


def prepare_embedded_python(build_dir: Path, project_root: Path) -> Path:
    """Main function to prepare embedded Python."""
    print("=" * 50)
    print("Preparing Embedded Python for Nanodesk")
    print("=" * 50)
    
    embedded_dir = build_dir / "embedded_python"
    
    # Check if already prepared
    python_exe = embedded_dir / "python.exe"
    if python_exe.exists():
        print(f"\nEmbedded Python already exists: {embedded_dir}")
        return embedded_dir
    
    # Create directories
    embedded_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir = build_dir / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    # Download Python
    print("\n[1/4] Downloading Python embeddable package...")
    zip_path = downloads_dir / f"python-{PYTHON_VERSION}-embed-amd64.zip"
    if not download_file(PYTHON_URL, zip_path):
        sys.exit(1)
    
    # Extract Python
    print("\n[2/4] Extracting Python...")
    if not extract_zip(zip_path, embedded_dir):
        sys.exit(1)
    
    # Enable site-packages
    print("\n[3/4] Configuring Python...")
    enable_site_packages(embedded_dir)
    
    # Install pip
    print("\n[4/4] Installing dependencies...")
    if not install_pip(python_exe):
        sys.exit(1)
    
    if not install_dependencies(python_exe, project_root):
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Embedded Python prepared successfully!")
    print(f"Location: {embedded_dir}")
    print("=" * 50)
    
    return embedded_dir


if __name__ == "__main__":
    # Determine project root (nanodesk/scripts/build/ → project root)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    
    # Build directory
    build_dir = project_root / "build_desktop"
    build_dir.mkdir(exist_ok=True)
    
    try:
        prepare_embedded_python(build_dir, project_root)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
