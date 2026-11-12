---
name: smp
description: "Run the Claude Code built-in /simplify on the staged changes and apply the fixes. Use for 'smp' or 'simplify my changes'. Claude Code only. Does not stage or commit."
disable-model-invocation: true
---

# SMP

Claude Code only: relies on the built-in `simplify` skill. In any other harness, say so and stop.

1. Run `git diff --cached --stat`. If nothing is staged, say so and stop.
2. Invoke the `simplify` skill via the Skill tool with args
   `staged changes only (git diff --cached)`. Without the target,
   simplify falls back to the whole working tree diff.

## Do NOT

- Do not stage, commit, push, or post comments.
