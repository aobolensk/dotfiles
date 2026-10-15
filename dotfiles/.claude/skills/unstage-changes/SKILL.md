---
name: unstage-changes
description: Unstage only the staged hunks that are unrelated to the current task (or that the user names), evaluated hunk by hunk, keeping changes in the working tree. Triggers on "unstage changes". Does not commit or discard anything.
---

# Unstage Changes

Move selected staged hunks back to unstaged. Working tree content is never lost.

## Steps

1. Follow `~/.claude/skills/_lib/select-hunks.md` with diff source
   `git diff --cached`. Here *selected* means the hunks to unstage: those the
   user named, or if none named, those unrelated to the current task.
2. Unstage the selected patch:
   `git apply --cached -R --unidiff-zero --recount <patch>`.
   Whole files where every hunk is selected: `git restore --staged <path>`.
3. Verify with `git diff --cached`.

## Do NOT

- Commit, discard working-tree changes, or use `git reset --hard` / `git checkout --`.
