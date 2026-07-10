---
name: merge-main
description: Merge the repository's main/default branch into the current branch. Auto-detects the main branch name (main, master, etc.). Stops on conflicts or a dirty working tree.
---

# Merge Main Into Current Branch

Bring the latest changes from the repository's main branch into the current
branch via a merge commit.

## Steps

1. Follow the shared preflight in
   `~/.claude/skills/_lib/sync-with-main.md` (detect main branch, verify
   clean working tree, fetch `origin/<main-branch>`).
2. Run the merge:

   ```bash
   git merge --no-edit origin/<main-branch>
   ```

   - Use `--no-edit` so the default merge commit message is accepted
     without opening an editor.
   - Do not pass `--no-ff` or `--ff-only` unless the user asks; let git
     fast-forward when it can.
3. Handle conflicts per the shared "Conflict handling" section. When all
   conflicts are resolved, return here for the "Continue after conflict
   resolution" step below. If the user wants to abort, run
   `git merge --abort`.
4. On success, follow the shared "On success" reporting step.

## Continue after conflict resolution

Once every conflicted file is resolved and staged, finalize the merge with:

```bash
git merge --continue
```

Do NOT use `git commit` here — `git commit` is generally disallowed, but
`git merge --continue` is the proper command for finishing an in-progress
merge and is allowed. If it opens an editor for the merge commit message,
accept the existing message unchanged.

## Notes

- Do NOT push. The user will push when they're ready.
- Do NOT amend or rewrite existing commits.
