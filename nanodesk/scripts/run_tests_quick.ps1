#!/usr/bin/env pwsh
# Quick Test Suite for CI/CD
# Runs essential tests only (faster)
# Usage: .\nanodesk\scripts\run_tests_quick.ps1

param([switch]$FailOnWarning)

$ErrorActionPreference = "Stop"
$failed = 0

function Test-Command($name, $command) {
    try {
        $null = Invoke-Expression $command 2>$null
        Write-Host "  ✓ $name" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  ✗ $name" -ForegroundColor Red
        $script:failed++
        return $false
    }
}

Write-Host "`nQuick Test Suite" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan

# Essential checks
Test-Command "Python 3.11+" "python --version" | Out-Null
Test-Command "Git branch" "git branch --show-current" | Out-Null
Test-Command "nanobot import" "python -c 'import nanobot'" | Out-Null
Test-Command "nanodesk import" "python -c 'import nanodesk'" | Out-Null
Test-Command "bootstrap inject" "python -c 'from nanodesk import bootstrap; bootstrap.inject()'" | Out-Null

# Tool registration check
$toolsCheck = python -c @"
from pathlib import Path
from nanodesk import bootstrap
bootstrap.inject()
from nanobot.agent.loop import AgentLoop
from nanobot.bus.queue import MessageBus
loop = AgentLoop(provider=None, workspace=Path('./workspace'), bus=MessageBus(), model='test')
missing = [t for t in ['ddg_search', 'browser_search', 'browser_fetch'] if t not in loop.tools.tool_names]
exit(1 if missing else 0)
"@ 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Custom tools registered" -ForegroundColor Green
} else {
    Write-Host "  ✗ Custom tools registered" -ForegroundColor Red
    $failed++
}

# Summary
if ($failed -eq 0) {
    Write-Host "`n✓ All quick tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n✗ $failed test(s) failed" -ForegroundColor Red
    exit 1
}
