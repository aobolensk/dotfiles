---
name: triage-ci-failure
description: Diagnose and fix failed CI jobs by fetching logs, identifying root causes, and applying fixes.
---

# Triage CI Failure

Diagnose and fix failed CI jobs on the current branch or a specified PR/commit.

## Arguments

The user may provide:
- PR number or URL (optional — defaults to PR for current branch, or latest commit's CI)
- Specific job name to focus on (optional)
- Run ID (optional — defaults to most recent failed run)

## Steps

1. **Identify the CI run to fix.**
   - If a PR number/URL was given, use it. Otherwise run `~/.claude/skills/_lib/find-pr.sh` to get the PR number for the current branch.
   - If `find-pr.sh` exits non-zero (no PR found), fall back to the current branch's latest commit.

2. **List recent workflow runs and find failures.**
   ```
   gh run list --branch <branch> --limit 10 --json databaseId,status,conclusion,name,event
   ```
   Filter to runs with `conclusion: "failure"`. If a specific run ID was given, use that instead.

3. **Get failed jobs from the run.**
   ```
   gh run view <run-id> --json jobs
   ```
   Identify which jobs failed (look for `conclusion: "failure"`).

4. **Fetch logs for each failed job.**
   ```
   gh run view <run-id> --log-failed
   ```
   If logs are too large, use `--log-failed` which only fetches failed steps. Parse the output to extract error messages, stack traces, and failure context.

5. **Analyze the failure.** Common categories:
   - **Test failures**: Parse test output, identify failing test names and assertions
   - **Build errors**: Compiler/type errors, missing dependencies
   - **Lint/format**: ESLint, Prettier, Clippy, etc.
   - **Timeout**: Job exceeded time limit
   - **Infrastructure**: Network issues, service unavailable, rate limits

6. **Read relevant source files.** Based on the error messages:
   - For test failures: read the failing test file and the code under test
   - For build errors: read the file(s) mentioned in compiler output
   - For lint errors: read the flagged file(s) and line(s)

7. **Fix the issue.**
   - Make the necessary code changes to resolve the failure
   - For test failures: fix the code or update the test if the new behavior is correct
   - For lint/format: run the formatter/linter with `--fix` if available, or apply fixes manually
   - Do NOT commit changes automatically

8. **Verify the fix locally** (if possible).
   - If the failed check can be run locally (tests, lint, type-check, build), run it to confirm the fix works
   - Report whether local verification passed

9. **Summarize.**
   - List each failure that was addressed
   - Describe the root cause and the fix applied
   - Note any failures that couldn't be fixed automatically (e.g., flaky tests, infra issues)
