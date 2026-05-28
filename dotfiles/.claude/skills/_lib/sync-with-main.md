# Shared steps: sync the current branch with main

These steps are shared between the `merge-main` and `rebase-main` skills.
The caller picks the integration mode.

## Detect the main branch

Run the shared detection script (resolved relative to this file):

```bash
bash ~/.claude/skills/_lib/detect-main-branch.sh
```

It prints the branch name (e.g. `main`, `master`) and exits non-zero if it
can't determine one. If it fails, ask the user which branch to use rather
than guessing.

## Preflight

1. Confirm we're inside a git repo: `git rev-parse --is-inside-work-tree`.
2. Get the current branch: `git rev-parse --abbrev-ref HEAD`.
3. If the current branch equals the detected main branch, stop and tell the
   user — there is nothing to merge/rebase into itself.
4. Check the working tree with `git status --porcelain`.
5. Fetch the latest main from origin:
   `git fetch origin <main-branch>`.
   If there is no `origin` remote, fall back to `git fetch --all` and warn.

## Integrate

Call the mode-specific step from the calling skill (merge or rebase),
operating against `origin/<main-branch>` so we use the freshly-fetched ref
rather than a possibly-stale local main.

## Conflict handling

If the merge/rebase reports conflicts, attempt to resolve them intelligently
before involving the user:

1. Run `git status` to list conflicted files, and `git diff --name-only
   --diff-filter=U` to enumerate them programmatically.
2. For each conflicted file:
   a. Read the full file (with conflict markers) to see both sides in
      context. If helpful, also inspect:
      - `git log --oneline -5 <file>` on both sides for intent,
      - `git show :1:<file>` (base), `:2:<file>` (ours/HEAD),
        `:3:<file>` (theirs/incoming) for the three-way view.
   b. Decide if the conflict is safely auto-resolvable. Good candidates:
      - Both sides added imports / list entries / changelog lines → union
        them, preserving order/sort conventions.
      - Pure formatting or whitespace conflicts → take the more complete
        side.
      - One side renamed/moved code that the other side edited in place →
        apply the edit at the new location.
      - Lockfile/generated-file conflicts (`package-lock.json`, `yarn.lock`,
        `Cargo.lock`, `pnpm-lock.yaml`, `go.sum`, etc.) → don't hand-edit;
        take one side and regenerate (e.g. `npm install`, `cargo
        generate-lockfile`) so the file is consistent. Prefer regenerating
        from the incoming-main side unless the branch intentionally bumped
        deps.
      - Trivially compatible logic edits where both intents are clear and
        non-overlapping.
      Bad candidates (do NOT auto-resolve — stop and ask):
      - Conflicts in business logic where intent is ambiguous.
      - Either side deleted a file the other modified (rename/delete).
      - Conflicts you don't understand after reading surrounding code.
   c. If resolvable: edit the file to remove all `<<<<<<<`, `=======`,
      `>>>>>>>` markers and produce the merged content. Then
      `git add <file>`.
   d. If not resolvable: leave the file conflicted and note it for the
      user.
3. After attempting all files, run `git diff --check` to confirm no
   leftover conflict markers in staged files, and re-run `git status` to
   see what's left.
4. If everything is resolved, hand back to the calling skill's
   "Continue after conflict resolution" step to finalize the in-progress
   operation. Do not invent your own finalization command here.
5. Briefly summarize each auto-resolution to the user (file + what you did
   + why) so they can sanity-check. Do not claim success silently.
6. If any files were left unresolved, list them, show the conflicting
   hunks, and ask the user how to proceed (resolve together, or abort with
   the mode-specific `--abort` command from the calling skill).

## On success

Report a short summary: the main branch name used, the integration mode,
and the new HEAD (`git log -1 --oneline`).
