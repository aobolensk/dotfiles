---
name: commit-message
description: Generate a commit message based on the current staged changes, matching the repository's existing commit style. Does not commit.
---

# Generate Commit Message

Generate a commit message for the current staged changes. Do NOT create a commit — only output the message.

## Steps

1. Run `git log --oneline -20` to learn the repo's commit message style (format, casing, prefixes, conventional commits, etc.).
2. Run `git diff --cached --stat` to check for staged changes. If nothing is staged, inform the user and stop.
3. Run `git diff --cached` to read the staged changes.
4. Compose a commit message that:
   - Follows the style and conventions observed in the repo's git log (e.g. conventional commits, imperative mood, prefixes)
   - Has a concise subject line
   - Has NO body by default. Only add a body when the diff has a non-obvious *why* that the subject cannot convey (e.g. a workaround, a constraint, a revert reason). If you add one, keep it to 1–3 short lines and explain *why*, not *what* — never restate the diff or list changed files/functions.
   - Mirrors the body-length norm in `git log` — if recent commits in this repo are subject-only, yours must be too.
   - Does NOT include any Co-Authored-By lines
5. Output the suggested commit message in a fenced code block so the user can copy it.
