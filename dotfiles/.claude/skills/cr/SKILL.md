---
name: cr
description: "Run the Claude Code built-in /code-review at max effort on the staged changes and apply the fixes. Use for 'cr' or 'review and fix my changes'. Claude Code only. Does not stage or commit."
disable-model-invocation: true
---

# CR

Claude Code only: relies on the built-in `code-review` skill. In any other harness, say so and stop.

1. Run `git diff --cached --stat`. If nothing is staged, say so and stop.
2. Invoke the `code-review` skill via the Skill tool with args
   `max --fix staged changes only (git diff --cached)`. Without the target,
   code-review falls back to the whole working tree diff.

## Do NOT

- Do not stage, commit, push, or post comments.
