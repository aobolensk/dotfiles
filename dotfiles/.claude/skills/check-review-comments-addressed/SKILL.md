---
name: check-review-comments-addressed
description: Check whether the current changes fully address the review comments on a GitHub PR, and list every gap. Use when the user asks "do these changes fulfill the review comments fully?", "did I miss anything from the review?", "verify I addressed all comments", or "what is left from the review". Reports only; does not modify code, commit, or post.
---

# Check Review Comments Addressed

Verify that the code as it stands fulfills every review comment, and list all
gaps. Read-only: reports findings, changes nothing.

## Arguments

- **PR number or URL** (optional): defaults to the current branch's PR.
- **Reviewer** (optional): restrict the check to that reviewer's comments.

## Steps

1. Collect the unresolved comments per
   `~/.claude/skills/_lib/unresolved-pr-comments.md`.
2. Determine what changed since each comment. For a comment created at `T`,
   take the branch commits after `T` (`git log --since=<T> <main>..HEAD`, with
   `<main>` from `~/.claude/skills/_lib/detect-main-branch.sh`) plus the
   uncommitted diff (`git diff HEAD`), and inspect the current content of the
   file the comment points at. `line` refers to the reviewed diff, so locate
   the code by its content, not by the number alone.
3. Classify each comment: addressed (name the code that proves it), partial
   (name the missing part), not addressed, addressed differently (name the
   divergence), or needs a reply rather than code.
4. Hunt for gaps beyond the literal text of each comment:
   - **Sibling occurrences**: the same pattern the reviewer flagged, still
     present elsewhere (grep for it across the diff and the touched files).
   - **Implied follow-through**: a rename, signature, or behavior change made
     for the reviewer but not propagated to callers, tests, docs, or comments.
   - **Missing tests**: a reviewer-reported bug fixed with no regression test.
   - **Scope creep**: changes on the branch that no comment asked for, which
     the reviewer has not seen.
   - **Regressions**: an edit made for one comment that undoes another.
5. Report using the format below.

## Output format

One verdict line, then one line per gap. Nothing else: no per-comment recap,
no list of the addressed comments, no restating the reviewer's text.

```text
<N>/<M> addressed. <one-line bottom line>
- <file>:<line> (@reviewer): <what is still missing>
```

## Do NOT

- Do not modify, stage, commit, or push any code.
- Do not post replies or resolve threads on GitHub.
- Do not call a comment addressed without checking the code that does it.
- Do not pad the report: gaps only, no nits the reviewer never raised.
