#!/usr/bin/env bash
# Usage: stash-preserve-across-checkout.sh <new-branch> <base-ref>
#
# git stash pop onto a different base commit silently reclassifies cleanly
# auto-merged staged files as unstaged (no conflict shown), so the staged
# path list is captured up front and restored after a clean pop.

set -eu

new_branch=$1
base_ref=$2

if [ -z "$(git status --porcelain)" ]; then
    git checkout -b "$new_branch" "$base_ref"
    exit 0
fi

staged_paths=$(git diff --name-only --cached)

git stash push --include-untracked -m "stash-preserve-across-checkout: $new_branch"
git checkout -b "$new_branch" "$base_ref"

if git stash pop; then
    git reset -q -- .
    if [ -n "$staged_paths" ]; then
        printf '%s\n' "$staged_paths" | git add --pathspec-from-file=- --
    fi
    exit 0
else
    echo "stash-preserve-across-checkout: stash pop conflicted, resolve manually (changes are in the stash)" >&2
    exit 1
fi
