---
name: stash-changes
description: Stash only the hunks related to the current task (or that the user names), evaluated hunk by hunk, leaving other changes in place. Triggers on "stash changes". Does not commit or drop stashes.
---

# Stash Changes

Stash selected hunks from staged and unstaged changes. Never commits.

## Steps

1. Follow `~/.claude/skills/_lib/select-hunks.md` with diff source
   `git diff HEAD`. *Selected* means the hunks to stash: those the user
   named, or if none named, those produced by the current task.
2. Stash the selected hunks:
   `~/.claude/skills/_lib/stash-hunks.sh <patch> "<short message>"`.
   Whole files where every hunk is selected, or selected untracked files:
   `git stash push --include-untracked -m "<message>" -- <path>...`.
3. Verify with `git stash show -p stash@{0}` that it holds only selected
   hunks. Report the stash ref.

## Do NOT

- Commit, drop, or pop stashes, or stash unselected hunks.
