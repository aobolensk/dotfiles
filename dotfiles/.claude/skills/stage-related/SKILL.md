---
name: stage-related
description: Stage only the working-tree changes related to the current task, hunk by hunk, leaving unrelated or pre-existing changes unstaged. Does not commit.
---

# Stage Related Changes

Stage the hunks that belong to the work just done, and leave everything else
alone. Relatedness is decided per hunk, never per file.

## Steps

1. Run `git status --short` to list all changed and untracked files.
2. Run `git diff -U1 <path> | grep -n "^@@"` on each modified file to enumerate
   its hunks, then read the hunks themselves.
3. Classify every hunk as related or unrelated. A hunk is *related* if the
   current task produced it. Treat as *unrelated*:
   - Hunks that were already in the working tree before the task started.
   - Hunks belonging to an earlier, separate piece of work in the same session.
   - Untracked scratch or report files the task did not produce.
   - Changes in subprojects or areas the task never touched.
4. Report the classification as a table before staging anything: hunk header,
   one-line content summary, and the verdict. Call out any hunk that mixes
   related and unrelated lines.
5. If a related hunk depends on an unrelated one (it references a symbol or
   behaviour the unrelated hunk introduces), say so plainly and ask whether to
   stage the related hunks alone, producing an index that does not build, or to
   pull in the prerequisite. Do not decide this silently.
6. Stage the selection. `git add -p` is interactive and unavailable here, so
   construct the intended index content directly:

   ```bash
   git show HEAD:<path> > /tmp/staged.tmp
   # apply only the related hunks to /tmp/staged.tmp, e.g. with a python
   # script of exact string replacements, asserting each anchor matches once
   blob=$(git hash-object -w /tmp/staged.tmp)
   git update-index --cacheinfo 100644,$blob,<path>
   ```

   This leaves the working tree untouched and shows the file as `MM`.

   Use plain `git add <path>` only when every hunk in that file is related.
   Never use `git add -A`, `git add .`, or `git add -u`, which sweep in
   unrelated changes.
7. Verify with `git diff --cached <path>` that the staged diff contains the
   related hunks and nothing else.
8. Run `git status --short` again and report what is now staged (`M`/`A`/`MM`)
   versus what was deliberately left unstaged, listing the excluded hunks by
   name. Repeat any caveat from step 5, such as the staged tree not building.

## Notes

- Do NOT commit. Staging only.
- Skip files that may hold secrets (`.env`, credentials), and flag them instead.
