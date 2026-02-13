#!/bin/bash
# Extract a commit from nanodesk branch to a clean contrib branch for PR

COMMIT_HASH=$1

if [ -z "$COMMIT_HASH" ]; then
    echo "Usage: $0 <commit-hash>"
    echo ""
    echo "Extract a clean commit from nanodesk branch to a new contrib branch"
    echo "that can be used to create PR to upstream."
    exit 1
fi

echo "==> 1. Ensuring main is up to date"
git checkout main
git pull upstream main 2>/dev/null || git fetch upstream && git merge upstream/main --ff-only

echo ""
echo "==> 2. Creating contrib branch"
BRANCH_NAME="contrib/$(date +%s)"
git checkout -b "$BRANCH_NAME"

echo ""
echo "==> 3. Cherry-picking commit $COMMIT_HASH"
if git cherry-pick "$COMMIT_HASH"; then
    echo "✅ Cherry-pick successful!"
else
    echo ""
    echo "⚠️  Cherry-pick has conflicts. Resolve them:"
    echo "  1. Fix the conflicts in the files"
    echo "  2. git add ."
    echo "  3. git cherry-pick --continue"
    echo "  4. Re-run this script if needed"
    exit 1
fi

echo ""
echo "==> 4. Pushing to origin"
git push -u origin "$BRANCH_NAME"

echo ""
echo "✅ Contrib branch created: $BRANCH_NAME"
echo ""
echo "Next steps:"
echo "  1. Go to GitHub: https://github.com/HKUDS/nanobot/pulls"
echo "  2. Click 'New pull request'"
echo "  3. Choose 'compare across forks'"
echo "  4. Select your fork and branch: $BRANCH_NAME"
echo "  5. Create the PR!"
