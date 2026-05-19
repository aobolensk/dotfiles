#!/usr/bin/env bash
# Print the PR number for the current branch, or exit non-zero.
# Tries: branch->PR association, then a PR search by HEAD SHA, then by branch name.
set -euo pipefail

pr=$(gh pr view --json number -q .number 2>/dev/null) || pr=
[ -n "$pr" ] || pr=$(gh pr list --state all --search "$(git rev-parse HEAD)" \
                       --json number -q '.[0].number // empty')
[ -n "$pr" ] || pr=$(gh pr list --state all --head "$(git branch --show-current)" \
                       --json number -q '.[0].number // empty')

[ -n "$pr" ] || { echo "no PR found for current branch" >&2; exit 1; }
echo "$pr"
