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

1. Identify the PR. If not provided, assume the PR associated with the current branch (e.g. `gh pr view --json number,url`). If no PR is associated with the current branch, ask the user to pick one.
2. Fetch review comments:
   ```
   gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate
   ```
   Also fetch review-level comments:
   ```
   gh api repos/{owner}/{repo}/pulls/{number}/reviews --paginate
   ```
3. Filter to unresolved/pending comments. If a reviewer filter was given, narrow to that reviewer. Show the user a summary: reviewer, file, line, and comment snippet for each.
4. Address all unresolved comments by default. If the user specified a filter (reviewer, topic), address only matching comments.
5. For each comment:
   - Read the relevant file and surrounding context.
   - Understand what the reviewer is asking for.
   - Make the requested change. If the comment is ambiguous, ask the user before changing code.
   - Do not commit, stage or unstage any changes.
   - If the reviewer asks a question. Provide a reply, but do not post it automatically.
6. After all changes are made, show a summary of what was done per comment.
