#!/usr/bin/env bash
# Usage: stash-preserve-across-checkout.sh <new-branch> <base-ref>
#
# A plain checkout -b keeps staged, unstaged, and untracked changes as is,
# unless they overlap files that differ from base-ref. Only then stash and
# pop with --index. If --index does not apply, pop plainly and restage the
# originally staged paths, since a plain pop silently unstages them.

set -eu

new_branch=$1
base_ref=$2

if err=$(git checkout -q -b "$new_branch" "$base_ref" 2>&1); then
    exit 0
fi

# Nothing to stash means the failure is not an overlap
if [ -z "$(git status --porcelain)" ]; then
    echo "$err" >&2
    exit 1
fi

staged_paths=$(git diff --name-only --cached)

git stash push --include-untracked -m "stash-preserve-across-checkout: $new_branch"

# Still on the original base here, so popping back restores the exact state
if ! git checkout -b "$new_branch" "$base_ref"; then
    git stash pop --index
    exit 1
fi

if git stash pop --index; then
    exit 0
fi

# A conflict leaves unmerged paths, anything else is retried without --index
if [ -z "$(git ls-files -u)" ] && git stash pop; then
    git reset -q -- .
    if [ -n "$staged_paths" ]; then
        printf '%s\n' "$staged_paths" | git add --pathspec-from-file=- --
    fi
    exit 0
fi

echo "stash-preserve-across-checkout: stash pop failed, resolve manually (changes may be in the stash)" >&2
exit 1
