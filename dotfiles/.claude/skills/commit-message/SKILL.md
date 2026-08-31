---
name: commit-message
description: Generate a commit message based on the current staged changes, matching the repository's existing commit style. Does not commit.
---

# Generate Commit Message

Generate a commit message for the current staged changes. Do NOT create a
commit — only output the message.

## Steps

**Every invocation must re-run the commands below from scratch.** Staged
contents change between invocations (commits land, stages get extended or
reset, branches switch). Never reuse a message you generated earlier in the
session — re-read the diff first, even on back-to-back invocations.

1. Run `git log --oneline -20` to learn the repo's general commit message
   style (format, casing, conventional commits, etc.).
2. Run `git diff --cached --stat` to check for staged changes. If nothing is staged, inform the user and stop.
3. Run `git diff --cached` to read the staged changes.
4. If the repo uses per-area tags/prefixes (e.g. `[COMPONENT]`, `[Area]`),
   verify the tag against the touched paths' own history, not the generic
   log from step 1 or a guess from the file path: run
   `git log --oneline -- <changed paths>` and use the tag neighbouring
   commits for those exact paths already use.
5. Compose a commit message that:
   - Follows the style and conventions observed in the repo's git log (e.g. conventional commits, imperative mood, prefixes)
   - Has a short subject line, ideally under 72 chars including any prefix.
     Cut filler like "in order to", "this change", "properly", "correctly".
   - Has NO body by default. Only add a body when the diff has a non-obvious
     *why* that the subject cannot convey (e.g. a workaround, a constraint, a
     revert reason). If you add one, keep it to 1–2 short lines and explain
     *why*, not *what* — never restate the diff or list changed files/functions.
   - Uses plain, direct wording. Prefer short everyday words over precise but
     heavy ones, and one clause over two joined by "and", "which", or "so
     that". Drop any word, clause, or line that does not change what the
     reader understands — given two phrasings that say the same thing, take
     the shorter one.
   - Follows Strunk & White's *Elements of Style*: active voice, definite and
     concrete wording, omit needless words.
   - Uses no possessive 's, no em-dashes, no non-ASCII symbols (arrows,
     Unicode bullets, etc.), and no semicolons.
   - Mirrors the body-length norm in `git log` — if recent commits in this repo are subject-only, yours must be too.
   - Does NOT include any Co-Authored-By lines
   - Is derived from the staged diff only — do NOT infer intent, scope, or prefix from the current branch name
6. On success, output ONLY the commit message in a fenced code block — no preamble, explanation, or trailing commentary.
