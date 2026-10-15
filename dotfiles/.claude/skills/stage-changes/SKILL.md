---
name: stage-changes
description: Stage only the unstaged hunks related to the current task, evaluated hunk by hunk, leaving unrelated changes unstaged. Triggers on "stage changes", "stage what we did". Does not commit.
---

# Stage Changes

Stage the hunks that belong to the work just done. Never commits.

## Steps

1. Follow `~/.claude/skills/_lib/select-hunks.md` with diff source `git diff`
   (unstaged changes) plus untracked files.
2. Stage the selected patch: `git apply --cached --unidiff-zero --recount <patch>`.
   Stage whole files with `git add <path>` only when every hunk is selected.
   Untracked files: `git add <path>` for selected ones only.
3. Verify with `git diff --cached` that only selected hunks are staged.

## Do NOT

- Commit, push, or stage unselected hunks.
