#!/usr/bin/env bash
# Print the name of the main/default branch for the current repo.

set -eu

if branch=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null); then
    echo "${branch#origin/}"
    exit 0
fi

if git remote set-head origin --auto >/dev/null 2>&1; then
    if branch=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null); then
        echo "${branch#origin/}"
        exit 0
    fi
fi

if command -v gh >/dev/null 2>&1; then
    if branch=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null); then
        if [ -n "$branch" ]; then
            echo "$branch"
            exit 0
        fi
    fi
fi

for candidate in main master trunk; do
    if git show-ref --verify --quiet "refs/heads/$candidate" \
        || git show-ref --verify --quiet "refs/remotes/origin/$candidate"; then
        echo "$candidate"
        exit 0
    fi
done

echo "detect-main-branch: could not determine main branch" >&2
exit 1
