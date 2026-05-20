# Global instructions

- Use subagents to delegate tasks where it is applicable so the main agent's context stays clean. Manipulate subagent results in the main session.
- Use the same model for subagents as the one used in the main agent.
- Do not stage, unstage or commit changes, and do not post GitHub reviews, comments, or similar actions unless explicitly asked.
- Prefer a proper root-cause fix over a workaround. If only a workaround is feasible, label it as such and ask before applying it.
- Before inventing a pattern, check how sibling backends and neighbouring code already solve the same problem and mirror that approach.
- Do not expand scope beyond what was asked: no opportunistic refactors, renames, or out of scope cleanups. Ask first if the change is indeed desired.
- Generated artifacts (commits, PRs, comments, TODOs, scripts, repros) take the shortest form that conveys the change. Commits: one-line subject, 0-2 sentence body. No diff recap, no banner comments, no narrative echo lines.
- Match reply length to the question. No preamble, no "let me...". End-of-turn summary: one sentence or none.
- Reviews/suggestions/analyses: lead with the top finding; surface only items worth acting on. No mixed critical-plus-nits lists.
