# Shared steps: collect the unresolved review comments of a PR

Shared by the `address-pr-comments`, `check-review-comments-addressed`, and
`draft-reviewer-reply` skills.

1. Fetch all three comment sources, parsing the full JSON output (never
   truncate with `head`/`tail`). If the user gave a PR number or URL, pass it;
   otherwise omit the argument and the script resolves the current branch's PR
   itself via `find-pr.sh`. If resolution fails, ask the user to pick a PR.

   ```bash
   bash ~/.claude/skills/_lib/fetch-pr-comments.sh <pr>
   ```

   Each line is one comment object tagged with `source`: `inline` (file/line),
   `review` (review-level summary), `issue` (PR-level conversation).

2. Sort by `created_at`. Drop objects with `is_resolved: true`. `is_resolved:
   null` means no thread state (review and issue comments), so treat those as
   still open.

3. If the user gave a reviewer filter, drop comments by other authors.

4. Identify each comment by `<path>:<line>` from the `path` and `line` fields,
   or `PR-level` when `path` is null.
