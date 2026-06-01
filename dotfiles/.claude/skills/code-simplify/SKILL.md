---
name: code-simplify
description: Simplify existing code without changing behavior. Use when asked to reduce complexity, remove overengineering, clean up abstractions, or make code easier to read and maintain.
---

# Simplify Code

## Goal

Make the code simpler, clearer, and easier to maintain while preserving behavior.

## When to use

Use this skill when the user asks to:

- simplify code
- reduce complexity
- remove overengineering
- clean up abstractions
- make code more readable
- refactor without changing behavior
- replace clever code with straightforward code

## Rules

1. Preserve existing behavior unless the user explicitly asks for behavior changes.
2. Prefer small, obvious improvements over large rewrites.
3. Do not introduce new dependencies unless clearly justified.
4. Do not redesign architecture unless the current design is causing real complexity.
5. Keep public APIs stable unless the user asks otherwise.
6. Prefer readable control flow over clever abstraction.
7. Delete dead code, unused helpers, redundant wrappers, and unnecessary indirection.
8. Consolidate duplicated logic only when it improves clarity.
9. Keep error handling explicit and understandable.
10. Run or suggest relevant tests when possible.

## Workflow

1. Inspect the target code and identify unnecessary complexity.
2. Separate safe simplifications from risky redesigns.
3. Make the smallest useful changes first.
4. Preserve names and structure where they help readability.
5. After editing, summarize what was simplified and why.

## Simplification checklist

Look for:

- redundant abstractions
- unnecessary classes, interfaces, wrappers, factories, or helpers
- duplicated branches
- deeply nested conditionals
- overly generic code used in only one place
- premature optimization
- unclear naming
- dead code
- unused parameters
- excessive configuration
- needless async/concurrency
- complex tests that can be made direct

## Output format

After changes, report:

- What changed
- What behavior was preserved
- Any tests run
- Any risky simplifications intentionally avoided

## Default behavior

If the requested simplification is broad, start with local, low-risk edits. Do not perform a large rewrite unless the user explicitly asks for it.
