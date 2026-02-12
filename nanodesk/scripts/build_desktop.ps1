# Build script for Nanodesk Desktop with embedded Python
# This creates a fully self-contained package - no Python installation required!

param(
    [switch]$Clean,
    [switch]$SkipEmbeddedPython  # Use if you already have embedded python prepared
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path (Split-Path $PSScriptRoot)
$DesktopDir = Join-Path (Join-Path $ProjectRoot "nanodesk") "desktop"
$BuildRoot = Join-Path $ProjectRoot "build_desktop"
$EmbeddedDir = Join-Path $BuildRoot "embedded_python"
$DistDir = Join-Path $ProjectRoot "dist"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Nanodesk Desktop Builder" -ForegroundColor Cyan
Write-Host "   With Embedded Python" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path (Join-Path $ProjectRoot "pyproject.toml"))) {
    Write-Error "Please run this script from the project root directory"
    exit 1
}

# Clean previous builds
if ($Clean -and (Test-Path $BuildRoot)) {
    Write-Host "Cleaning build directory..." -ForegroundColor Yellow
    Remove-Item $BuildRoot -Recurse -Force
    Write-Host "Clean complete" -ForegroundColor Green
}

# Create directories
New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null
New-Item -ItemType Directory -Force -Path $EmbeddedDir | Out-Null

# Step 1: Download and prepare embedded Python
if (-not $SkipEmbeddedPython) {
    Write-Host ""
    Write-Host "Step 1: Preparing embedded Python..." -ForegroundColor Cyan
    
    $PythonVersion = "3.11.9"
    $PythonZip = "python-$PythonVersion-embed-amd64.zip"
    $PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/$PythonZip"
    $PythonZipPath = Join-Path $BuildRoot $PythonZip
    
    # Download Python embeddable package
    if (-not (Test-Path $PythonZipPath)) {
        Write-Host "Downloading Python $PythonVersion embeddable package..." -ForegroundColor Yellow
        try {
            Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonZipPath -UseBasicParsing
            Write-Host "Downloaded: $PythonZip" -ForegroundColor Green
        } catch {
            Write-Error "Failed to download Python. Please check your internet connection."
            exit 1
        }
    } else {
        Write-Host "Python zip already exists, skipping download" -ForegroundColor Gray
    }
    
    # Extract Python
    if (-not (Test-Path (Join-Path $EmbeddedDir "python.exe"))) {
        Write-Host "Extracting Python..." -ForegroundColor Yellow
        Expand-Archive -Path $PythonZipPath -DestinationPath $EmbeddedDir -Force
        Write-Host "Python extracted" -ForegroundColor Green
    }
    
    # Enable site-packages (uncomment import site in python311._pth)
    $PthFile = Join-Path $EmbeddedDir "python311._pth"
    if (Test-Path $PthFile) {
        $content = Get-Content $PthFile -Raw
        $content = $content -replace "^#import site", "import site"
        Set-Content -Path $PthFile -Value $content -NoNewline
        Write-Host "Enabled site-packages in python311._pth" -ForegroundColor Green
    }
    
    # Download get-pip.py
    $GetPipPath = Join-Path $EmbeddedDir "get-pip.py"
    if (-not (Test-Path $GetPipPath)) {
        Write-Host "Downloading get-pip.py..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $GetPipPath -UseBasicParsing
    }
    
    # Install pip and dependencies
    Write-Host ""
    Write-Host "Installing pip and dependencies..." -ForegroundColor Yellow
    $EmbeddedPython = Join-Path $EmbeddedDir "python.exe"
    
    # Install pip
    & $EmbeddedPython $GetPipPath --no-warn-script-location
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install pip"
        exit 1
    }
    
    # Upgrade pip
    & $EmbeddedPython -m pip install --upgrade pip --no-warn-script-location
    
    # Install nanobot and all dependencies
    Write-Host "Installing nanobot-ai and dependencies..." -ForegroundColor Yellow
    & $EmbeddedPython -m pip install "$ProjectRoot" --no-warn-script-location
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install nanobot"
        exit 1
    }
    
    # Also install additional dependencies that might be needed
    & $EmbeddedPython -m pip install pywin32 --no-warn-script-location
    
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
}

# Step 2: Build desktop app with PyInstaller
Write-Host ""
Write-Host "Step 2: Building desktop application..." -ForegroundColor Cyan

# Check PyInstaller
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Build command - onedir mode for easier embedded Python integration
$MainScript = Join-Path $DesktopDir "main.py"
$ResourcesDir = Join-Path $DesktopDir "resources"
$IconPath = Join-Path (Join-Path $ResourcesDir "icons") "logo.ico"

$PyBuildDir = Join-Path $BuildRoot "pyinstaller"
$PyDistDir = Join-Path $BuildRoot "pyinstaller_dist"

$buildArgs = @(
    $MainScript
    "--name=Nanodesk"
    "--onedir"
    "--windowed"
    "--noconfirm"
    "--clean"
    "--distpath=$PyDistDir"
    "--workpath=$PyBuildDir"
)

# Add icon if exists
if (Test-Path $IconPath) {
    $buildArgs += "--icon=$IconPath"
}

# Add resources
$buildArgs += "--add-data=$ResourcesDir;resources"

# Add nanodesk desktop modules (hidden imports)
$buildArgs += "--hidden-import=nanodesk.desktop.core.config_manager"
$buildArgs += "--hidden-import=nanodesk.desktop.core.process_manager"
$buildArgs += "--hidden-import=nanodesk.desktop.core.log_handler"
$buildArgs += "--hidden-import=nanodesk.desktop.core.system_tray"
$buildArgs += "--hidden-import=nanodesk.desktop.core.embedded_gateway"
$buildArgs += "--hidden-import=nanodesk.desktop.core.gateway_service"
$buildArgs += "--hidden-import=nanodesk.desktop.windows.main_window"
$buildArgs += "--hidden-import=nanodesk.desktop.windows.setup_wizard"
$buildArgs += "--hidden-import=nanodesk.desktop.app"
$buildArgs += "--hidden-import=nanodesk.desktop.gateway_runner"

# Collect entire nanodesk.desktop package
$buildArgs += "--collect-all=nanodesk.desktop"

Write-Host "Running PyInstaller..." -ForegroundColor Yellow
& pyinstaller @buildArgs

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed"
    exit 1
}

Write-Host "Desktop app built successfully" -ForegroundColor Green

# Step 3: Merge embedded Python into distribution
Write-Host ""
    Write-Host "Step 3: Creating final distribution..." -ForegroundColor Cyan

$SourceAppDir = Join-Path $PyDistDir "Nanodesk"
$FinalDistDir = Join-Path $DistDir "Nanodesk"

# Clean and create final dist
if (Test-Path $FinalDistDir) {
    Write-Host "Removing old distribution..." -ForegroundColor Yellow
    # Try to remove, handle file locks gracefully
    try {
        Remove-Item $FinalDistDir -Recurse -Force -ErrorAction Stop
    } catch {
        Write-Host "Warning: Could not remove old files. Retrying with delay..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        # Kill any running Nanodesk processes
        Get-Process | Where-Object { $_.Name -eq "Nanodesk" } | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        Remove-Item $FinalDistDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
New-Item -ItemType Directory -Force -Path $FinalDistDir | Out-Null

# Copy PyInstaller output
Write-Host "Copying application files..." -ForegroundColor Yellow
Copy-Item -Path "$SourceAppDir\*" -Destination $FinalDistDir -Recurse -Force

# Copy embedded Python (excluding unnecessary files to save space)
Write-Host "Copying embedded Python..." -ForegroundColor Yellow
$TargetPythonDir = Join-Path $FinalDistDir "python"
New-Item -ItemType Directory -Force -Path $TargetPythonDir | Out-Null

# Copy Python files (exclude some large unnecessary files)
$ExcludePatterns = @("*.pdb", "__pycache__", "*.pyc", "test", "tests", "idlelib", "tkinter", "turtle*")
Get-ChildItem -Path $EmbeddedDir | ForEach-Object {
    $shouldExclude = $false
    foreach ($pattern in $ExcludePatterns) {
        if ($_.Name -like $pattern) {
            $shouldExclude = $true
            break
        }
    }
    if (-not $shouldExclude) {
        $dest = Join-Path $TargetPythonDir $_.Name
        if ($_.PSIsContainer) {
            Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
        } else {
            Copy-Item -Path $_.FullName -Destination $dest -Force
        }
    }
}

# Create marker file to indicate embedded mode
$MarkerFile = Join-Path $FinalDistDir "EMBEDDED_PYTHON"
"This package includes embedded Python. No system Python required." | Set-Content -Path $MarkerFile

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Build Successful!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output: $FinalDistDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "To distribute:" -ForegroundColor Yellow
Write-Host "  1. Zip the folder: $FinalDistDir" -ForegroundColor Yellow
Write-Host "  2. Or create installer with Inno Setup" -ForegroundColor Yellow
Write-Host ""
Write-Host "Package info:" -ForegroundColor Cyan
$Size = (Get-ChildItem $FinalDistDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "  Total size: $([math]::Round($Size, 2)) MB" -ForegroundColor White
Write-Host "  Embedded Python: $TargetPythonDir" -ForegroundColor White
Write-Host "  Entry point: $FinalDistDir\Nanodesk.exe" -ForegroundColor White
Write-Host ""
Write-Host "This package is FULLY SELF-CONTAINED!" -ForegroundColor Green
Write-Host "Users do NOT need Python installed." -ForegroundColor Green
