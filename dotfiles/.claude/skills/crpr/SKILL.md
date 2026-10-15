---
name: crpr
description: "Run the Claude Code built-in /code-review at max effort on a PR given by the user. Use for 'crpr <pr>' or 'review PR 123'. Claude Code only. Reports only; does not modify code or post comments."
disable-model-invocation: true
argument-hint: "<pr number, URL, or branch>"
---

# CRPR

Claude Code only: relies on the built-in `code-review` skill. In any other harness, say so and stop.

PR: $ARGUMENTS

1. If the PR above is empty, ask the user for it and stop. Never auto-detect.
2. Invoke the `code-review` skill via the Skill tool with args `max <PR above>`.

## Do NOT

- Do not pass `--fix` or `--comment`, and do not stage, commit, push, or post comments.
