---
name: address-pr-comments
description: Address review comments in a GitHub PR.
---

# Address PR Review Comments

Address unresolved review comments on a GitHub PR.

## Arguments

The user may provide:

- PR number or URL (optional — if not provided, assume the PR associated with the current branch)
- Reviewer name to filter by (optional)
- Specific topic or area to focus on (optional)

## Steps

1. Collect the unresolved comments per
   `~/.claude/skills/_lib/unresolved-pr-comments.md`.
2. Show the user a summary: reviewer, file, line (or "PR-level" when `path` is
   null), and comment snippet for each.
3. Address all unresolved comments by default. If the user specified a filter (reviewer, topic), address only matching comments.
4. For each comment:
   - Read the relevant file and surrounding context.
   - Understand what the reviewer is asking for.
   - Make the requested change. If the comment is ambiguous, ask the user before changing code.
   - Do not commit, stage or unstage any changes.
   - If the reviewer asks a question, provide a reply, but do not post it
     automatically. Follow Strunk & White: active voice, definite and
     concrete wording, omit needless words. Use no possessive 's, no
     em-dashes, no non-ASCII symbols, and no semicolons.
5. After all changes are made, build and test the project to confirm the
   changes are correct. If the build or tests fail, fix the issues before
   proceeding.
6. Show a summary of what was done per comment.
