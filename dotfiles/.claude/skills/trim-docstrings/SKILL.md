---
name: trim-docstrings
argument-hint: [light|aggressive|max|all] [scope]
description: Alias for trim-prose, scoped to docstrings. Shrink or delete docstrings just authored or substantially rewritten in the current change, including module/class headers and Args/Returns/Raises sections, or strip every docstring in a named scope (all). Use when asked to trim, shorten, cut down, or remove docstrings.
---

# Trim Docstrings

Alias. Follow [[trim-prose]] (`~/.claude/skills/trim-prose/SKILL.md`), reading
its level off the same arguments, and restrict the pass to docstrings: module,
class, function and method docstrings, no inline comments.
