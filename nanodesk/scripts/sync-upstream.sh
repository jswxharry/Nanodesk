#!/bin/bash
# Nanodesk upstream sync script
# Usage: ./sync-upstream.sh [--push] [--force]

set -e
PUSH=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --push) PUSH=true; shift ;;
        --force) FORCE=true; shift ;;
        *) echo "Usage: $0 [--push] [--force]"; exit 1 ;;
    esac
done

stop_with_hint() {
    echo -e "\033[31m✗ $1\033[0m"
    echo -e "\033[36m$2\033[0m"
    exit 1
}

# 1. Check upstream remote
if ! git remote | grep -q "^upstream$"; then
    git remote add upstream https://github.com/HKUDS/nanobot.git
    echo "Added upstream remote"
fi

# 2. Fetch updates
git fetch upstream || stop_with_hint "Fetch failed" "Check network connection"

# 3. Check for updates
if ! git log --oneline main..upstream/main | grep -q .; then
    echo "Already up to date"
    exit 0
fi

echo "Found updates:"
git log --oneline main..upstream/main

# 4. Check for local changes
if [ -n "$(git status --porcelain)" ] && [ "$FORCE" = false ]; then
    stop_with_hint "Uncommitted changes" "Run: git stash or git commit, or use --force to continue"
fi

# 5. Update main branch
git checkout main || stop_with_hint "Cannot switch to main" "Check git status"
git merge upstream/main --ff-only >/dev/null 2>&1 || {
    git checkout nanodesk 2>/dev/null || true
    stop_with_hint "Main cannot fast-forward" "Local main may have extra commits. Check: git log upstream/main..main"
}

# 6. Merge to nanodesk
git checkout nanodesk || stop_with_hint "Cannot switch to nanodesk" "Check if branch exists"

if git merge main -m "sync: merge upstream" >/dev/null 2>&1; then
    echo "Merge success"
else
    # Has conflicts, try auto-resolve
    CONFLICTS=$(git diff --name-only --diff-filter=U)
    if [ -z "$CONFLICTS" ]; then
        stop_with_hint "Merge failed" "No conflicts but merge failed. Check git status"
    fi
    
    echo "Found conflicts, auto-resolving..."
    
    # nanobot/ accept upstream, nanodesk/ keep local
    HAS_UNRESOLVABLE=false
    
    while IFS= read -r file; do
        case "$file" in
            nanobot/*)
                git checkout --theirs "$file"
                git add "$file"
                ;;
            nanodesk/*)
                git checkout --ours "$file"
                git add "$file"
                ;;
            *)
                HAS_UNRESOLVABLE=true
                echo "  ! $file cannot auto-resolve"
                ;;
        esac
    done <<< "$CONFLICTS"
    
    if [ "$HAS_UNRESOLVABLE" = true ]; then
        git checkout nanodesk 2>/dev/null || true
        stop_with_hint "Unresolvable conflicts in non-standard dirs" "Resolve manually and commit"
    fi
    
    git commit -m "sync: merge upstream and resolve conflicts" >/dev/null
    echo "Conflicts resolved"
fi

# 7. Status
echo ""
echo "Status: main=$(git rev-parse --short main), nanodesk=$(git rev-parse --short nanodesk)"

# 8. Push
if [ "$PUSH" = true ]; then
    git push origin main nanodesk
    echo "Pushed"
else
    read -p "Push to origin? (y/N) " resp
    if [[ "$resp" =~ ^[Yy]$ ]]; then
        git push origin main nanodesk
        echo "Pushed"
    fi
fi
