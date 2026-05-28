---
name: rebase-main
description: Rebase the current branch on top of the repository's main/default branch. Auto-detects the main branch name (main, master, etc.). Stops on conflicts or a dirty working tree.
---

# Rebase Current Branch On Main

Replay the current branch's commits on top of the latest main branch.

## Steps

1. Follow the shared preflight in
   `~/.claude/skills/_lib/sync-with-main.md` (detect main branch, verify
   clean working tree, fetch `origin/<main-branch>`).
2. Warn the user before proceeding if the current branch already has a
   remote tracking branch with commits that aren't on HEAD — rebasing will
   require a force-push to update it. Confirm before continuing.
3. Run the rebase:
   ```bash
   git rebase origin/<main-branch>
   ```
   Do NOT use `-i` (interactive) — this skill is non-interactive.
4. Handle conflicts per the shared "Conflict handling" section. When all
   conflicts in the current step are resolved, return here for the
   "Continue after conflict resolution" step below. If the user wants to
   abort, run `git rebase --abort`.
5. On success, follow the shared "On success" reporting step.

## Continue after conflict resolution

Once every conflicted file in the current rebase step is resolved and
staged, advance the rebase with:

```bash
git rebase --continue
```

Do NOT use `git commit` here — `git commit` is generally disallowed, but
`git rebase --continue` is the proper command for resuming an in-progress
rebase and is allowed. If it opens an editor for the commit message,
accept the existing message unchanged. Never use `git rebase --skip`
unless the user explicitly asks. If the next replayed commit also
conflicts, loop back to step 4.

## Notes

- Do NOT push. If the branch was previously pushed, the user will need to
  force-push (`git push --force-with-lease`) themselves — surface this
  reminder but don't run it.
- Never run `git rebase` against a branch that has been merged or is shared
  with collaborators without explicit user confirmation.
