# Select Hunks

Shared hunk-level selection for `stage-changes`, `unstage-changes`, and
`stash-changes`. The caller supplies the diff source and the action.

## Select

1. Run `git status --short` to list changed and untracked files.
2. Dump the caller's diff once into a temp file and read it:
   `patch=$(mktemp); git diff -U0 <source-args> > "$patch"; echo "$patch"`.
   Shell state does not persist between calls, so reuse the printed path as
   `<patch>` below.
3. Classify every hunk as *selected* or *left*. Relatedness is decided per
   hunk, never per file. A hunk is selected if the current task produced it
   (or the user named it). Treat as left:
   - Hunks already in the working tree before the task started.
   - Hunks from an earlier, separate piece of work in the same session.
   - Untracked scratch or report files the task did not produce.
   - Changes in areas the task never touched.
4. Report a table before acting: hunk header, one-line summary, verdict.
   Call out any hunk that mixes selected and left lines.
5. If a selected hunk depends on a left one (it uses a symbol or behaviour
   the left hunk introduces), or the reverse for unstage/stash, say so and
   ask whether to proceed or pull in the prerequisite. Do not decide silently.
6. Skip files that may hold secrets (`.env`, credentials) and flag them.

## Build the patch

Edit `<patch>` in place: delete unselected hunks and file sections, and trim
mixed hunks. `-U0` keeps hunks splittable.

Apply it with `git apply --unidiff-zero --recount` (counts in edited hunk
headers need not be exact). Never use `git add -A`, `git add .`, or
`git add -u`, and never `git add -p` (interactive, unavailable).

Whole files where every hunk is selected may use plain path commands.

## Verify and report

Check the result with the caller's verify command and `git status --short`.
Report selected versus left hunks by name, repeating any dependency caveat.
