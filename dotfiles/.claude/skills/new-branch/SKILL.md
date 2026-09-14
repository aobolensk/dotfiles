---
name: new-branch
description: "Create and check out a new branch from the repository's detected default branch, naming it from the pending changes and neighboring branch history. Preserves staged and unstaged changes across checkout. Use for 'make a branch for this', 'name a branch for these changes', or 'create a branch off main'. Creates and checks out the branch; does not commit or push."
---

# New Branch

Create a branch from the repository's default branch, preserve pending changes,
and check out the new branch without committing or pushing.

## Steps

1. **Detect and fetch the default branch.** Use the shared helper rather than
   assuming `main`, `master`, or another name.

   ```bash
   main_branch=$(bash ~/.claude/skills/_lib/detect-main-branch.sh)
   git fetch origin "$main_branch"
   ```

2. **Determine the change set to name.** Prefer staged changes. If nothing is
   staged, use the tracked working-tree diff plus non-ignored untracked files,
   and tell the user which source was used.

   ```bash
   git diff --cached --stat
   git diff --cached
   git diff --stat
   git diff
   git ls-files --others --exclude-standard
   ```

3. **Learn the naming convention from this repository's history.** Inspect
   recent commits and branch names for the changed paths. Derive the shortest
   area or component prefix and a concise slug describing the change. Match
   local spelling, separators, casing, and any usual verb prefix. Do not use a
   universal prefix map or infer the convention from paths alone.

   ```bash
   git log --oneline -- <changed paths>
   git branch -a --list '*<area>*'
   ```

   If the history gives no clear convention, use the repository's established
   project or component naming and state the assumption. Ask if multiple names
   remain materially plausible.

4. **Check for collisions** across local and fetched remote branches. If the
   candidate exists, append the repository's usual numeric suffix. Otherwise
   use `-1`, `-2`, and so on.

   ```bash
   git branch -a --list "<candidate>"
   ```

5. **Create and check out the branch with pending changes preserved.**

   ```bash
   bash ~/.claude/skills/_lib/stash-preserve-across-checkout.sh \
       <candidate> "origin/$(bash ~/.claude/skills/_lib/detect-main-branch.sh)"
   ```

   If it exits nonzero, `stash pop` conflicted. Stop and show the conflict. Do
   not resolve it silently because the changes remain in the stash.

6. **Report** the branch name, the naming rationale, the source used for the
   name, and whether staged and unstaged changes landed on the new branch
   unchanged.

## Do NOT

- Do not commit or push.
- Do not guess the naming convention without checking neighboring history.
- Do not resolve a `git stash pop` conflict on your own.
