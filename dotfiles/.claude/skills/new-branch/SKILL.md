---
name: new-branch
description: "Create and check out a new branch from the default branch, named from pending changes and branch history, keeping staged and unstaged changes. Use for 'make a branch for this' or 'create a branch off main'. Does not commit or push."
---

# New Branch

Batch commands: aim for three tool calls (recon, create, report).

1. **Recon.** Detect and fetch the default branch, then list the changes and
   neighboring history. Prefer staged changes, else the working-tree diff plus
   untracked files, and say which source was used. Use `--stat`. Read a full
   diff only if the purpose is unclear. For a clean tree, name from the
   conversation or ask.

   ```bash
   main_branch=$(bash ~/.claude/skills/_lib/detect-main-branch.sh)
   git fetch -q origin "$main_branch"
   echo "main=$main_branch"
   git diff --cached --stat; echo "--- unstaged"; git diff --stat
   echo "--- untracked"; git ls-files --others --exclude-standard
   echo "--- history"; git log --oneline -8 -- <changed paths>
   echo "--- branches"; git branch -a --list '*<area>*'
   ```

   If the paths are unknown, run the first four commands, then history and
   branches in a second call.

2. **Name.** Analyze the recent commit subjects touching the changed paths and
   the matching branch names to learn the convention. Derive the shortest area
   prefix and a concise slug, matching local spelling, separators, casing, and
   verb prefix. Never use a generic prefix map, infer from paths alone, or
   guess without checking this history. With no clear convention,
   state the assumption, and ask if several names stay plausible. If the name
   exists, add the repository usual numeric suffix, else `-1`, `-2`.

3. **Create.** Variables do not persist between calls, so substitute
   `<main_branch>` with the default branch detected and printed in step 1.

   ```bash
   bash ~/.claude/skills/_lib/stash-preserve-across-checkout.sh \
       <candidate> origin/<main_branch> && git status -sb
   ```

   On nonzero exit, `stash pop` conflicted. Stop and show the conflict. Do not
   resolve it, the changes remain in the stash.

4. **Report** the name, rationale, change source, and whether staged and
   unstaged changes landed unchanged.

Never commit or push.
