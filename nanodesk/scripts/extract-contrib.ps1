# Extract a commit from nanodesk branch to a clean contrib branch for PR (Windows PowerShell)
# Usage: .\nanodesk\scripts\extract-contrib.ps1 <commit-hash>

param(
    [Parameter(Mandatory=$true)]
    [string]$CommitHash
)

$ErrorActionPreference = "Stop"

Write-Host "==> 1. Ensuring main is up to date" -ForegroundColor Cyan
git checkout main
if ($LASTEXITCODE -ne 0) { exit 1 }

try {
    git pull upstream main
} catch {
    git fetch upstream
    git merge upstream/main --ff-only
}

Write-Host "`n==> 2. Creating contrib branch" -ForegroundColor Cyan
$branchName = "contrib/$(Get-Date -Format 'yyyyMMdd-HHmmss')"
git checkout -b $branchName
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n==> 3. Cherry-picking commit $CommitHash" -ForegroundColor Cyan
git cherry-pick $CommitHash
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n⚠️  Cherry-pick has conflicts. Resolve them:" -ForegroundColor Yellow
    Write-Host "  1. Fix the conflicts in the files"
    Write-Host "  2. git add ."
    Write-Host "  3. git cherry-pick --continue"
    Write-Host "  4. Re-run this script if needed"
    exit 1
}

Write-Host "`n==> 4. Pushing to origin" -ForegroundColor Cyan
git push -u origin $branchName
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n✅ Contrib branch created: $branchName" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Go to GitHub: https://github.com/HKUDS/nanobot/pulls"
Write-Host "  2. Click 'New pull request'"
Write-Host "  3. Choose 'compare across forks'"
Write-Host "  4. Select your fork and branch: $branchName"
Write-Host "  5. Create the PR!"
