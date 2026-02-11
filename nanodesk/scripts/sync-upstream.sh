#!/bin/bash
# Sync upstream changes to nanodesk branch

set -e

echo "==> 1. Updating main branch (tracking upstream)"
git checkout main
git fetch upstream
git merge upstream/main --ff-only
git push origin main

echo ""
echo "==> 2. Syncing to nanodesk branch"
git checkout nanodesk
git merge main -m "sync: merge upstream changes into nanodesk"

echo ""
echo "==> 3. Handling README conflicts (if any)"
if git diff --name-only --diff-filter=U | grep -q "README.md"; then
    echo "⚠️  README.md has conflicts, keeping our version..."
    git checkout --ours README.md
    git add README.md
    git commit -m "sync: resolve README conflict (keep ours)" || true
fi

echo ""
echo "✅ Sync complete!"
echo ""
echo "If there are other conflicts, resolve them and run:"
echo "  git add ."
echo "  git commit -m 'sync: resolve conflicts'"
echo "  git push origin nanodesk"
