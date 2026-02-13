#!/usr/bin/env pwsh
<#
.SYNOPSIS
    启动 Nanodesk 桌面应用（开发模式）
.DESCRIPTION
    自动设置 UTF-8 编码环境变量后启动桌面应用
#>

$ErrorActionPreference = "Stop"

# 设置 UTF-8 环境变量
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# 获取项目根目录
$ScriptDir = Split-Path -Parent $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScriptDir

# 启动桌面应用
Write-Host "Starting Nanodesk Desktop..." -ForegroundColor Cyan
Write-Host "UTF-8 encoding enabled" -ForegroundColor Gray

Set-Location $ProjectRoot
python -m nanodesk.desktop.main
