---
name: suggest-reviewers
description: Suggests reviewers for the PR on the current branch, based on CODEOWNERS, git history and blame of the touched code, and past reviewers of related PRs. Use for "suggest reviewers", "who should review this", "who to request review from". Reports only; does not request reviews, post, stage or commit.
---

# Suggest Reviewers

Rank candidate reviewers for the current branch PR. Read-only: never request reviews, comment, stage or commit.

## Arguments

- **PR number or URL** (optional): defaults to the PR for the current branch.

## Steps

1. Resolve the PR with `~/.claude/skills/_lib/find-pr.sh` (skip if given). If it fails, fall back to the diff
   against `$(~/.claude/skills/_lib/detect-main-branch.sh)` and ask whether to continue without a PR.
2. Collect the changed files: `gh pr diff <pr> --name-only`. Note the PR author and existing reviewers and
   requests via `gh pr view <pr> --json author,reviewRequests,reviews`.
3. Gather signals, per changed file or directory:
   - CODEOWNERS (`.github/CODEOWNERS`, `CODEOWNERS`, `docs/CODEOWNERS`) matches.
   - Recent authors: `git log --since=1.year --format=%an%x09%ae -- <path>`.
   - Blame owners of the lines the PR modifies, on the base revision.
   - Reviewers and approvers of recent merged PRs touching the same paths:
     `gh pr list --state merged --search "<path>" --json number,author,reviews`.
4. Score by weight: CODEOWNERS > blame of modified lines > prior reviewers of the same paths > recent authors.
   Drop the PR author and bots. Map git identities to GitHub logins where possible, and say when unsure.
5. Print the top 3-5 candidates.

## Output format

One line per candidate: `@login (or name) - why (e.g. CODEOWNER of X, 60% blame of Y, reviewed Z)`.
Mark already-requested reviewers. Lead with the strongest candidate.
Wrap logins in backticks so nobody is notified.

## Do NOT

- Request reviews, comment, or post anything on GitHub.
- Stage, unstage or commit.
- Include the PR author or bots.
