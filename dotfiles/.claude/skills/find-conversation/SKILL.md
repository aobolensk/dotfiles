---
name: find-conversation
description: Finds past Claude Code conversations in the current directory matching a description, offers the best candidates, and loads the picked one into the current conversation to continue from it. Use when asked "find the conversation about X", "which session was I doing X in", "resume the chat where we...", "attach to the dialogue about...". Read-only; does not modify transcripts.
---

# Find Conversation

Search this directory's Claude Code sessions by description, let the user pick one, and load it into the
current conversation. Read-only.

## Arguments

- **description** (required): what the conversation was about. If missing, ask.

## Steps

1. List sessions of the current directory with title, mtime, and first prompt:

   ```bash
   d=~/.claude/projects/$(pwd | sed 's/[^A-Za-z0-9]/-/g')
   for f in $(ls -t "$d"/*.jsonl); do
     printf '%s\t%s\t%s\t%s\n' "$(basename "$f" .jsonl)" "$(date -r "$f" +%F)" \
       "$(jq -rs '[.[]|select(.type=="ai-title").aiTitle]|last // ""' "$f")" \
       "$(jq -rs '[.[]|select(.type=="user" and (.message.content|type=="string")
         and (.message.content|startswith("<")|not))|.message.content][0] // ""|.[0:120]' "$f")"
   done
   ```

2. Rank by match to the description (title, first prompt). If fewer than 2 plausible hits, grep the transcripts
   for the key terms: `grep -il -- '<term>' "$d"/*.jsonl`.
3. Ask via `AskUserQuestion` with up to 4 best candidates, label = title, description = date + first prompt
   snippet. Put the best first, marked "(Recommended)". If none match, say so and stop.
4. Attach by loading the chosen transcript into this conversation (a live session cannot switch to another, so
   import its text turns):

   ```bash
   jq -r 'select(.type=="user" or .type=="assistant") | .type as $t | .message.content
     | (if type=="string" then . else map(select(.type=="text").text)|join("\n") end)
     | select(length>0 and (startswith("<")|not)) | "[\($t)] \(.[0:1500])"' "$d/<session-id>.jsonl" | tail -n 150
   ```

   Read it, state in one sentence where the conversation left off, and continue from there. If the output is
   cut off, read earlier turns only on request.

## Do NOT

- Do NOT edit, delete, or move transcript files.
- Do NOT dump transcript contents beyond short snippets.
- Do NOT search other directories unless asked.
