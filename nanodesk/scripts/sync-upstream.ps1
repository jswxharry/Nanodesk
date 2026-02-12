#!/usr/bin/env pwsh
# Nanodesk upstream sync script
# Usage: .\sync-upstream.ps1 [-Push] [-Force]

param([switch]$Push, [switch]$Force)
$ErrorActionPreference = "Stop"

function Stop-WithHint($msg, $hint) {
    Write-Host "✗ $msg" -ForegroundColor Red
    Write-Host $hint -ForegroundColor Cyan
    exit 1
}

# 1. Check upstream remote
if (-not (git remote | Select-String "^upstream$")) {
    git remote add upstream https://github.com/HKUDS/nanobot.git
    Write-Host "Added upstream remote"
}

# 2. Fetch updates
git fetch upstream
if ($LASTEXITCODE -ne 0) {
    Stop-WithHint "Fetch failed" "Check network connection or upstream remote config"
}

# 3. Check for updates
$updates = git log --oneline main..upstream/main
if (-not $updates) {
    Write-Host "Already up to date" -ForegroundColor Green
    exit 0
}

Write-Host "Found updates:" -ForegroundColor Yellow
$updates

# 4. Check for local changes
if ((git status --porcelain) -and -not $Force) {
    Stop-WithHint "Uncommitted changes" "Run: git stash or git commit, or use -Force to continue"
}

# 5. Update main branch
git checkout main
if ($LASTEXITCODE -ne 0) {
    Stop-WithHint "Cannot switch to main" "Check: git status"
}

git merge upstream/main --ff-only | Out-Null
if ($LASTEXITCODE -ne 0) {
    git checkout nanodesk 2>$null
    Stop-WithHint "Main cannot fast-forward" "Local main may have extra commits. Check: git log upstream/main..main"
}

# 6. Merge to nanodesk
git checkout nanodesk
if ($LASTEXITCODE -ne 0) {
    Stop-WithHint "Cannot switch to nanodesk" "Check if branch exists"
}

git merge main -m "sync: merge upstream" | Out-Null

if ($LASTEXITCODE -ne 0) {
    # Has conflicts, try auto-resolve
    $conflicts = git diff --name-only --diff-filter=U
    if (-not $conflicts) {
        Stop-WithHint "Merge failed" "No conflicts but merge failed. Check: git status"
    }
    
    Write-Host "Found conflicts, auto-resolving..." -ForegroundColor Yellow
    
    # nanobot/ accept upstream, nanodesk/ keep local
    $conflictFiles = git diff --name-only --diff-filter=U
    $hasUnresolvable = $false
    
    foreach ($file in $conflictFiles) {
        if ($file -like "nanobot/*") {
            git checkout --theirs "$file"
            git add "$file"
        }
        elseif ($file -like "nanodesk/*") {
            git checkout --ours "$file"
            git add "$file"
        }
        else {
            $hasUnresolvable = $true
            Write-Host "  ! $file cannot auto-resolve" -ForegroundColor Red
        }
    }
    
    if ($hasUnresolvable) {
        git checkout nanodesk 2>$null
        Stop-WithHint "Unresolvable conflicts in non-standard dirs" "Resolve manually and commit"
    }
    
    git commit -m "sync: merge upstream and resolve conflicts" | Out-Null
    Write-Host "Conflicts resolved" -ForegroundColor Green
} else {
    Write-Host "Merge success" -ForegroundColor Green
}

# 7. Status
Write-Host ""
Write-Host "Status: main=$(git rev-parse --short main), nanodesk=$(git rev-parse --short nanodesk)"

# 8. Push
if ($Push) {
    git push origin main nanodesk
    Write-Host "Pushed" -ForegroundColor Green
} else {
    $resp = Read-Host "Push to origin? (y/N)"
    if ($resp -eq 'y') {
        git push origin main nanodesk
        Write-Host "Pushed" -ForegroundColor Green
    }
}
