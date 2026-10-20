---
name: background-session
description: Moves the current Claude Code conversation into a background session that survives SSH drops and terminal closes, and stays reattachable with `claude attach`. Use when asked "move this session to the background", "detach this session", "keep this running if ssh dies", "make this survive disconnect". Does not kill the current session or modify transcripts.
---

# Background Session

Continue the current conversation as a background session and give the reattach command. Does not stop anything.

## Steps

1. Check for work launched from this session that is still running (workflows, background agents, background
   shell commands). Exiting kills it, and the background copy never receives its completion notification.
   If any is running, ask via `AskUserQuestion`: "Hand over (Recommended)" or "Wait until it finishes".
   On wait, stop here and say what is pending. On hand over, stop each running workflow with `TaskStop` so
   it does not run twice, and record its script path and run id. Background agents and shell commands cannot
   be handed over: list them and ask again if any exist.
2. Start the background copy of this session (the live one is still running, so this forks it under a new id).
   If workflows were stopped, pass a prompt so the copy resumes them. Finished agents come back from cache:

   ```bash
   claude --bg --resume "$CLAUDE_CODE_SESSION_ID" \
     "Resume workflow: Workflow({scriptPath: '<path>', resumeFromRunId: '<run id>'})"
   ```

   With no workflows, omit the prompt.
3. Report the id it prints and tell the user, in this order:
   - Exit this foreground session (`/exit`), since the background copy now holds the conversation.
   - Reattach anytime with `claude attach <id>`. Ctrl+Z detaches back to the shell and the session keeps running.
   - Other commands: `claude agents` (list), `claude logs <id>`, `claude stop <id>`.

4. If the command fails or prints no id, show the error and stop. Do not retry in a loop.

## Do NOT

- Do NOT stop, kill, or `rm` any session, including the current one.
- Do NOT stop a workflow unless the user chose "Hand over".
- Do NOT edit or delete transcript files.
- Do NOT start more than one background copy per invocation.
