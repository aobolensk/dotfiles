# Global instructions

- Delegate to subagents where applicable to keep main context clean; process their results in the main session. Use the same model as the main agent.
- Never stage, unstage, commit, or post GitHub reviews/comments unless explicitly asked.
- Prefer root-cause fixes over workarounds. If only a workaround is feasible, label it as such and ask first.
- Before inventing a pattern, mirror how sibling/neighbouring code already solves it.
- Don't expand scope: no opportunistic refactors, renames, or cleanups. Ask first.
- Generated artifacts (commits, PRs, comments, TODOs, scripts, repros) take the shortest form conveying the change. Commits: one-line subject, 0-2 sentence body. No diff recap, banner comments, or narrative echo.
- Match reply length to the question. No preamble or "let me...". End-of-turn summary: one sentence or none.
- Reviews/suggestions/analyses: lead with the top finding; surface only items worth acting on. No mixed critical-plus-nits lists.
