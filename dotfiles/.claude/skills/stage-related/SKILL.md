---
name: stage-related
description: Stage only the working-tree changes related to the current task, leaving unrelated or pre-existing changes unstaged. Does not commit.
---

# Stage Related Changes

Selectively `git add` the files that belong to the work just done, and leave
everything else alone.

## Steps

1. Run `git status --short` to list all changed and untracked files.
2. Decide which paths are part of the current task. A file is *related* if it
   was created or edited as part of this task's change set. Treat as
   *unrelated* (do NOT stage):
   - Files that were already modified before the task started.
   - Untracked scratch/report files not produced by the task.
   - Changes in subprojects/areas the task never touched.
   When unsure whether a file belongs, ask rather than staging it.
3. Stage only the related paths by name:

   ```bash
   git add <path> [<path> ...]
   ```

   Never use `git add -A`, `git add .`, or `git add -u` — they sweep in
   unrelated changes.
4. Run `git status --short` again and report what is now staged (`M`/`A`)
   versus what was deliberately left unstaged.

## Notes

- Do NOT commit. Staging only.
- Skip files that may hold secrets (`.env`, credentials); flag them instead.
