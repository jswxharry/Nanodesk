#!/usr/bin/env pwsh
<#
.SYNOPSIS
    关闭所有 Nanodesk 相关进程
.DESCRIPTION
    强制结束 Nanodesk 桌面应用、Gateway 和嵌入 Python 进程
#>

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "   Stopping All Nanodesk Processes" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

$killed = @()

# 1. 关闭 Nanodesk 桌面应用
$nanodeskProcesses = Get-Process | Where-Object { 
    $_.Name -eq "Nanodesk" -or 
    $_.Path -like "*Nanodesk*" 
}
foreach ($proc in $nanodeskProcesses) {
    Write-Host "Killing Nanodesk Desktop (PID: $($proc.Id))..." -ForegroundColor Red
    $proc.Kill()
    $proc.WaitForExit(2000) | Out-Null
    $killed += "Nanodesk Desktop (PID: $($proc.Id))"
}

# 2. 关闭 Gateway（通过 python -m nanodesk.launcher gateway）
$pythonProcesses = Get-Process | Where-Object { 
    $_.Name -eq "python" -or $_.Name -eq "pythonw" 
}
foreach ($proc in $pythonProcesses) {
    try {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId=$($proc.Id)").CommandLine
        if ($cmdLine -like "*nanodesk.launcher*gateway*" -or 
            $cmdLine -like "*nanobot*gateway*") {
            Write-Host "Killing Gateway (PID: $($proc.Id))..." -ForegroundColor Red
            $proc.Kill()
            $proc.WaitForExit(2000) | Out-Null
            $killed += "Gateway (PID: $($proc.Id))"
        }
    } catch {}
}

# 3. 关闭嵌入 Python（如果在运行）
$embeddedPython = Get-Process | Where-Object { 
    $_.Path -like "*dist\Nanodesk\python*" 
}
foreach ($proc in $embeddedPython) {
    Write-Host "Killing Embedded Python (PID: $($proc.Id))..." -ForegroundColor Red
    $proc.Kill()
    $proc.WaitForExit(2000) | Out-Null
    $killed += "Embedded Python (PID: $($proc.Id))"
}

# 4. 关闭残留的 PyInstaller 进程
$pyInstallerProcesses = Get-Process | Where-Object { 
    $_.Name -like "*_internal*" -or 
    $_.Path -like "*pyinstaller*"
}
foreach ($proc in $pyInstallerProcesses) {
    Write-Host "Killing PyInstaller process (PID: $($proc.Id))..." -ForegroundColor Red
    $proc.Kill()
    $killed += "PyInstaller (PID: $($proc.Id))"
}

Write-Host ""
if ($killed.Count -gt 0) {
    Write-Host "Killed processes:" -ForegroundColor Green
    $killed | ForEach-Object { Write-Host "  ✓ $_" -ForegroundColor Green }
} else {
    Write-Host "No Nanodesk processes found." -ForegroundColor Gray
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan
