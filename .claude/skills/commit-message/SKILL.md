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
   - Has a concise body/description only if the change warrants it
   - Does NOT include any Co-Authored-By lines
5. Output the suggested commit message in a fenced code block so the user can copy it.
