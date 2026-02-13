#!/usr/bin/env pwsh
# Nanodesk Automated Test Suite
# Usage: .\nanodesk\scripts\run_tests.ps1 [-Verbose] [-SkipBuild]

param(
    [switch]$Verbose,
    [switch]$SkipBuild,
    [switch]$AutoFix
)

$ErrorActionPreference = "Stop"
$script:Passed = 0
$script:Failed = 0
$script:Warnings = 0

function Write-TestHeader($text) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-TestResult($name, $passed, $message = "") {
    if ($passed) {
        Write-Host "  ✓ $name" -ForegroundColor Green
        $script:Passed++
    } else {
        Write-Host "  ✗ $name" -ForegroundColor Red
        if ($message) {
            Write-Host "    $message" -ForegroundColor DarkRed
        }
        $script:Failed++
    }
}

function Write-TestWarning($name, $message) {
    Write-Host "  ⚠ $name" -ForegroundColor Yellow
    if ($message) {
        Write-Host "    $message" -ForegroundColor DarkYellow
    }
    $script:Warnings++
}

# ========================================
# Test 1: Environment Checks
# ========================================
Write-TestHeader "Test 1: Environment Checks"

# Python version
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(1[1-9]|[2-9][0-9])") {
    Write-TestResult "Python version ($pythonVersion)" $true
} else {
    Write-TestResult "Python version ($pythonVersion)" $false "Requires Python 3.11+"
}

# Git branch
$branch = git branch --show-current 2>$null
if ($branch -eq "develop") {
    Write-TestResult "Git branch (develop)" $true
} else {
    Write-TestResult "Git branch ($branch)" $false "Should be 'develop' branch"
}

# Check upstream remote
$upstream = git remote -v 2>$null | Select-String "upstream.*nanobot"
if ($upstream) {
    Write-TestResult "Upstream remote configured" $true
} else {
    Write-TestWarning "Upstream remote" "upstream remote not found. Run: git remote add upstream https://github.com/HKUDS/nanobot.git"
}

# ========================================
# Test 2: Dependency Checks
# ========================================
Write-TestHeader "Test 2: Dependency Checks"

$requiredPackages = @(
    @{Name="nanobot"; Module="nanobot"},
    @{Name="nanodesk"; Module="nanodesk"},
    @{Name="typer"; Module="typer"},
    @{Name="litellm"; Module="litellm"},
    @{Name="pydantic"; Module="pydantic"},
    @{Name="loguru"; Module="loguru"}
)

foreach ($pkg in $requiredPackages) {
    try {
        python -c "import $($pkg.Module)" 2>$null
        Write-TestResult "Package: $($pkg.Name)" $true
    } catch {
        Write-TestResult "Package: $($pkg.Name)" $false "Not installed. Run: pip install -e ."
    }
}

# Optional packages for search tools
$optionalPackages = @(
    @{Name="duckduckgo-search"; Module="duckduckgo_search"},
    @{Name="playwright"; Module="playwright"}
)

foreach ($pkg in $optionalPackages) {
    try {
        python -c "import $($pkg.Module)" 2>$null
        Write-TestResult "Optional: $($pkg.Name)" $true
    } catch {
        Write-TestWarning "Optional: $($pkg.Name)" "Not installed. Search tools won't work. Run: pip install $($pkg.Name)"
    }
}

# ========================================
# Test 3: Code Quality
# ========================================
Write-TestHeader "Test 3: Code Quality Checks"

# Check if ruff is installed
$ruffInstalled = $null -ne (Get-Command ruff -ErrorAction SilentlyContinue)
if (-not $ruffInstalled) {
    Write-Host "  Installing ruff..." -ForegroundColor Yellow
    pip install ruff -q
}

# Run ruff check
Write-Host "`n  Running ruff check..." -ForegroundColor Gray
$ruffOutput = python -m ruff check nanodesk/ --output-format=concise 2>&1
$ruffExit = $LASTEXITCODE

if ($ruffExit -eq 0) {
    Write-TestResult "Ruff lint check" $true
} else {
    $errorCount = ($ruffOutput | Select-String "^nanodesk" | Measure-Object).Count
    Write-TestResult "Ruff lint check" $false "$errorCount issues found"
    
    if ($AutoFix) {
        Write-Host "`n  Auto-fixing issues..." -ForegroundColor Yellow
        python -m ruff check nanodesk/ --fix -q
        Write-Host "  Fixed issues where possible." -ForegroundColor Green
    } elseif ($Verbose) {
        Write-Host "`n  Ruff output:" -ForegroundColor Gray
        $ruffOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
        Write-Host "`n  Run with -AutoFix to auto-fix issues." -ForegroundColor Yellow
    }
}

# Run ruff format check
Write-Host "`n  Running ruff format check..." -ForegroundColor Gray
$ruffFormatOutput = python -m ruff format --check nanodesk/ 2>&1
$ruffFormatExit = $LASTEXITCODE

if ($ruffFormatExit -eq 0) {
    Write-TestResult "Ruff format check" $true
} else {
    Write-TestResult "Ruff format check" $false "Files need formatting"
    if ($AutoFix) {
        Write-Host "  Auto-formatting..." -ForegroundColor Yellow
        python -m ruff format nanodesk/ -q
    }
}

# ========================================
# Test 4: Import Tests
# ========================================
Write-TestHeader "Test 4: Import Tests"

$importTests = @(
    @{Name="nanobot core"; Code="import nanobot"},
    @{Name="nanodesk core"; Code="import nanodesk"},
    @{Name="nanodesk.bootstrap"; Code="from nanodesk import bootstrap"},
    @{Name="nanobot.agent.loop"; Code="from nanobot.agent.loop import AgentLoop"},
    @{Name="nanobot.agent.memory"; Code="from nanobot.agent.memory import MemoryStore"},
    @{Name="ToolRegistry"; Code="from nanobot.agent.tools.registry import ToolRegistry"}
)

foreach ($test in $importTests) {
    try {
        python -c $test.Code 2>$null
        Write-TestResult "Import: $($test.Name)" $true
    } catch {
        Write-TestResult "Import: $($test.Name)" $false $_.Exception.Message
    }
}

# ========================================
# Test 5: Custom Tools Registration
# ========================================
Write-TestHeader "Test 5: Custom Tools Registration"

$toolsCheckCode = @"
from pathlib import Path
from nanodesk import bootstrap
bootstrap.inject()

from nanobot.agent.loop import AgentLoop
from nanobot.bus.queue import MessageBus

bus = MessageBus()
loop = AgentLoop(
    provider=None,
    workspace=Path('./workspace'),
    bus=bus,
    model='test'
)

tools = loop.tools.tool_names
required_tools = ['ddg_search', 'browser_search', 'browser_fetch']
missing = [t for t in required_tools if t not in tools]

if missing:
    print(f"MISSING:{','.join(missing)}")
else:
    print(f"OK:{','.join(required_tools)}")
    print(f"ALL:{','.join(tools)}")
"@

try {
    $toolsOutput = python -c $toolsCheckCode 2>&1
    if ($toolsOutput -match "^OK:") {
        $registeredTools = ($toolsOutput | Select-String "^OK:").Line -replace "^OK:", ""
        Write-TestResult "Custom tools registered" $true "Tools: $registeredTools"
    } else {
        $missingTools = ($toolsOutput | Select-String "^MISSING:").Line -replace "^MISSING:", ""
        Write-TestResult "Custom tools registered" $false "Missing: $missingTools"
    }
    
    if ($Verbose -and ($toolsOutput -match "^ALL:")) {
        $allTools = ($toolsOutput | Select-String "^ALL:").Line -replace "^ALL:", ""
        Write-Host "`n  All registered tools:" -ForegroundColor Gray
        $allTools -split "," | ForEach-Object { Write-Host "    - $_" -ForegroundColor DarkGray }
    }
} catch {
    Write-TestResult "Custom tools registered" $false $_.Exception.Message
}

# ========================================
# Test 6: Configuration Schema
# ========================================
Write-TestHeader "Test 6: Configuration Validation"

$schemaTest = @"
from nanobot.config.schema import Config, AgentsConfig, ProvidersConfig
c = Config()
print("Schema OK")
"@

try {
    python -c $schemaTest 2>$null
    Write-TestResult "Configuration schema" $true
} catch {
    Write-TestResult "Configuration schema" $false $_.Exception.Message
}

# ========================================
# Test 7: Pytest (if available)
# ========================================
Write-TestHeader "Test 7: Unit Tests"

$pytestInstalled = $null -ne (Get-Command pytest -ErrorAction SilentlyContinue)
if ($pytestInstalled) {
    Write-Host "  Running pytest..." -ForegroundColor Gray
    $pytestOutput = pytest tests/ -v --tb=short 2>&1
    $pytestExit = $LASTEXITCODE
    
    if ($pytestExit -eq 0) {
        Write-TestResult "Unit tests" $true
    } else {
        Write-TestResult "Unit tests" $false "Some tests failed"
        if ($Verbose) {
            $pytestOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
        }
    }
} else {
    Write-TestWarning "Unit tests" "pytest not installed. Run: pip install pytest pytest-asyncio"
}

# ========================================
# Test 8: Build Test (optional)
# ========================================
if (-not $SkipBuild) {
    Write-TestHeader "Test 8: Build Test"
    
    Write-Host "  Checking build scripts..." -ForegroundColor Gray
    $buildScripts = @(
        "nanodesk/scripts/build_all.ps1",
        "nanodesk/scripts/build_desktop.ps1",
        "nanodesk/scripts/prepare_embedded_python.py"
    )
    
    foreach ($script in $buildScripts) {
        if (Test-Path $script) {
            Write-TestResult "Build script: $(Split-Path $script -Leaf)" $true
        } else {
            Write-TestResult "Build script: $(Split-Path $script -Leaf)" $false "File not found"
        }
    }
    
    # Note: Full build test is time-consuming, skip by default
    Write-Host "`n  Note: Full build test skipped (use -Verbose to see build script validation)" -ForegroundColor Yellow
}

# ========================================
# Summary
# ========================================
Write-TestHeader "Test Summary"

Write-Host "  Passed:   " -NoNewline
Write-Host $script:Passed -ForegroundColor Green
Write-Host "  Failed:   " -NoNewline
if ($script:Failed -gt 0) {
    Write-Host $script:Failed -ForegroundColor Red
} else {
    Write-Host $script:Failed -ForegroundColor Green
}
Write-Host "  Warnings: " -NoNewline
Write-Host $script:Warnings -ForegroundColor Yellow

$total = $script:Passed + $script:Failed
$percentage = if ($total -gt 0) { [math]::Round(($script:Passed / $total) * 100, 1) } else { 0 }

Write-Host "`n  Success Rate: $percentage%" -NoNewline
if ($percentage -ge 90) {
    Write-Host " (Excellent)" -ForegroundColor Green
} elseif ($percentage -ge 70) {
    Write-Host " (Good)" -ForegroundColor Yellow
} else {
    Write-Host " (Needs Improvement)" -ForegroundColor Red
}

# Exit code
if ($script:Failed -eq 0) {
    Write-Host "`n✓ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n✗ Some tests failed. Please review the output above." -ForegroundColor Red
    exit 1
}
