#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Nanodesk 版本发布脚本
.DESCRIPTION
    自动化版本号更新、Git 提交和标签创建
.PARAMETER Version
    新版本号（格式: MAJOR.MINOR.PATCH，例如: 0.2.0）
.PARAMETER SkipBuild
    跳过构建步骤
.EXAMPLE
    .\nanodesk\scripts\release\release.ps1 -Version "0.2.0"
#>

param(
    [Parameter(Mandatory=$true, HelpMessage="新版本号，格式: MAJOR.MINOR.PATCH")]
    [string]$Version,
    
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

# 验证版本号格式
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    Write-Error "版本号格式错误！请使用 MAJOR.MINOR.PATCH 格式（例如: 0.2.0）"
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Nanodesk Release Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取项目根目录
$ScriptDir = Split-Path -Parent $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

# 检查 Git 状态
Write-Host "[1/6] Checking Git status..." -ForegroundColor Yellow
$branch = git branch --show-current
if ($branch -ne "nanodesk") {
    Write-Error "当前不在 nanodesk 分支！请先切换到 nanodesk 分支"
    exit 1
}

$status = git status --porcelain
if ($status) {
    Write-Error "工作区有未提交的更改！请先提交或暂存"
    Write-Host $status
    exit 1
}
Write-Host "  ✓ Git status clean" -ForegroundColor Green

# 更新版本号
Write-Host ""
Write-Host "[2/6] Updating version numbers..." -ForegroundColor Yellow

$versionFiles = @(
    @{Path="nanodesk/__init__.py"; Pattern='__version__ = "[\d\.]+"'; Replacement="__version__ = `"$Version`""},
    @{Path="nanodesk/desktop/__init__.py"; Pattern='__version__ = "[\d\.]+"'; Replacement="__version__ = `"$Version`""}
)

foreach ($file in $versionFiles) {
    $fullPath = Join-Path $ProjectRoot $file.Path
    if (Test-Path $fullPath) {
        $content = Get-Content $fullPath -Raw
        $newContent = $content -replace $file.Pattern, $file.Replacement
        Set-Content $fullPath $newContent -NoNewline
        Write-Host "  ✓ Updated $($file.Path)" -ForegroundColor Green
    } else {
        Write-Error "File not found: $($file.Path)"
        exit 1
    }
}

# 可选：构建桌面应用
if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "[3/6] Building desktop application..." -ForegroundColor Yellow
    & "$ScriptDir\build_all.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed!"
        exit 1
    }
    Write-Host "  ✓ Build completed" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[3/6] Skipping build (use -SkipBuild)" -ForegroundColor Gray
}

# Git 提交
Write-Host ""
Write-Host "[4/6] Creating Git commit..." -ForegroundColor Yellow
git add -A
git commit -m "release: bump version to $Version"
Write-Host "  ✓ Commit created" -ForegroundColor Green

# 创建标签
Write-Host ""
Write-Host "[5/6] Creating Git tag..." -ForegroundColor Yellow
$tagName = "v$Version"
$existingTag = git tag -l $tagName
if ($existingTag) {
    Write-Warning "Tag $tagName already exists. Deleting old tag..."
    git tag -d $tagName
}
git tag -a $tagName -m "Release version $Version"
Write-Host "  ✓ Tag created: $tagName" -ForegroundColor Green

# 显示总结
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Release $Version Prepared!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review the changes: git log -1" -ForegroundColor White
Write-Host "  2. Push to remote:    git push origin nanodesk" -ForegroundColor White
Write-Host "  3. Push tag:          git push origin $tagName" -ForegroundColor White
Write-Host ""

if (-not $SkipBuild) {
    Write-Host "Build artifacts:" -ForegroundColor Cyan
    Write-Host "  - dist/Nanodesk/ (portable version)" -ForegroundColor White
    Write-Host "  - dist/Nanodesk-Portable.zip (if created)" -ForegroundColor White
    Write-Host ""
}

Write-Host "To create GitHub Release:" -ForegroundColor Cyan
Write-Host "  https://github.com/jswxharry/Nanodesk/releases/new?tag=$tagName" -ForegroundColor White
Write-Host ""
