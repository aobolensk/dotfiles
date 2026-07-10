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

1. Identify the PR. If not provided, run `~/.claude/skills/_lib/find-pr.sh` to
   get the PR number for the current branch. If it exits non-zero, ask the
   user to pick one.
2. Fetch comments from all three endpoints, parsing the full JSON output
   (never truncate with `head`/`tail`):

   ```bash
   gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate   # inline (file/line) review comments
   gh api repos/{owner}/{repo}/pulls/{number}/reviews --paginate     # review-level summary bodies
   gh api repos/{owner}/{repo}/issues/{number}/comments --paginate   # general PR conversation comments
   ```

3. Merge all three sources, sort by timestamp, and filter to
   unresolved/pending comments. If a reviewer filter was given, narrow to that
   reviewer. Show the user a summary: reviewer, file, line (or "PR-level" for
   review-level/issue comments), and comment snippet for each.
4. Address all unresolved comments by default. If the user specified a filter (reviewer, topic), address only matching comments.
5. For each comment:
   - Read the relevant file and surrounding context.
   - Understand what the reviewer is asking for.
   - Make the requested change. If the comment is ambiguous, ask the user before changing code.
   - Do not commit, stage or unstage any changes.
   - If the reviewer asks a question. Provide a reply, but do not post it automatically.
6. After all changes are made, build and test the project to confirm the
   changes are correct. If the build or tests fail, fix the issues before
   proceeding.
7. Show a summary of what was done per comment.
