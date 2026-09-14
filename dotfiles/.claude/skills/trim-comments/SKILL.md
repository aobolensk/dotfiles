---
name: trim-comments
argument-hint: [light|aggressive|max|all] [scope]
description: Alias for trim-prose, scoped to comments. Shrink or delete comments just authored or substantially rewritten in the current change, or strip every comment in a named scope (all). Use when asked to trim, shorten, minimize, cut down, or remove comments.
---

# Trim Comments

Alias. Follow [[trim-prose]] (`~/.claude/skills/trim-prose/SKILL.md`), reading
its level off the same arguments, and restrict the pass to comments: inline and
block comments only, no docstrings.
