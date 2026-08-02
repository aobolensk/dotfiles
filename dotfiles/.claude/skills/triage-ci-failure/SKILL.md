---
name: triage-ci-failure
description: Diagnose and fix failed CI jobs by fetching logs, identifying root causes, and applying fixes.
---

# Triage CI Failure

Diagnose and fix failed CI jobs on the current branch or a specified PR/commit.

The user may provide a PR number or URL, job name, or run ID. Otherwise use the
PR for the current branch and its most recent failed run, or CI for the latest
commit when the branch has no PR.

## Workflow

1. **Resolve the target.** Use the given PR or run ID. Otherwise run
   `~/.claude/skills/_lib/find-pr.sh`; if it finds no PR, use the current branch
   and latest commit.

2. **Find every failing check.** Unless a run ID was given, use `gh run list --branch <branch> --limit 10 --json databaseId,status,conclusion,name,event`. For a PR, also run
   `gh pr view <pr> --json statusCheckRollup` so external checks are not missed.
   Honor a requested job name when narrowing the results.

3. **Inspect jobs in each relevant Actions run.** Check every run except those
   concluded as `cancelled`, `skipped`, or `success`; an in-progress run can
   already contain failures. Run `gh run view <run-id> --json jobs -q '.jobs[] | {name, status, conclusion}'`.

4. **Fetch failed Actions logs once per run.** Run `gh run view <run-id> --log-failed`, then extract the error, stack trace, and surrounding context.

5. **Fetch failed external-check details.** Read the check `detailsUrl` or
   `targetUrl` from `statusCheckRollup`, then inspect that provider page or its
   authenticated API/CLI. If access is unavailable, report the check and URL as
   a blocker instead of ignoring it.

6. **Diagnose the root cause.** Classify the failure as test, build, lint,
   timeout, or infrastructure, then read the named tests, source files, and
   configuration. Distinguish product defects from stale expectations, flaky
   tests, and provider failures.

7. **Apply the smallest root-cause fix.** Update a test only when the intended
   behavior changed. Use a formatter or linter fix mode when appropriate. Do not
   commit changes.

8. **Verify locally when possible.** Run the focused failing command first,
   then any proportionate broader test, lint, type-check, or build command.

9. **Report the result.** Name each addressed failure, its root cause and fix,
   the local verification result, and any remaining flaky, infrastructure, or
   inaccessible external checks.
