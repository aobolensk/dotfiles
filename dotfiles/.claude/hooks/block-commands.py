#!/usr/bin/env python3
"""
PreToolUse hook: deny shell commands listed in block-commands.txt

See block-commands.txt for the list of rejected commands
"""

import json
import shlex
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("block-commands.txt")
DENY_MESSAGE = "This command is on the deny-list. Ask the user before running it."
PIPE_OPS = {";", "&&", "||", "|", "&", "|&"}


def load_patterns():
    """Return list of (raw, prog, positionals, flags) parsed from the config."""
    try:
        text = CONFIG_PATH.read_text()
    except OSError:
        return []
    out = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        words = line.split()
        pos = [t for t in words[1:] if not t.startswith("-")]
        flags = [t for t in words[1:] if t.startswith("-")]
        out.append((line, words[0], pos, flags))
    return out


def subcommands(cmd):
    """Yield token lists per pipeline segment, respecting shell quoting."""
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    cur = []
    for tok in lex:
        if tok in PIPE_OPS:
            if cur:
                yield cur
                cur = []
        else:
            cur.append(tok)
    if cur:
        yield cur


def first_match(tokens, patterns):
    if not tokens:
        return None
    prog = tokens[0].rsplit("/", 1)[-1]
    args = tokens[1:]
    arg_pos = [a for a in args if not a.startswith("-")]
    for raw, p_prog, p_pos, p_flags in patterns:
        if p_prog == prog and arg_pos[: len(p_pos)] == p_pos and all(f in args for f in p_flags):
            return raw
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if payload.get("tool_name") != "Bash":
        return
    cmd = (payload.get("tool_input") or {}).get("command", "")
    patterns = load_patterns()
    if not (cmd and patterns):
        return
    try:
        for tokens in subcommands(cmd):
            hit = first_match(tokens, patterns)
            if hit:
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Blocked `{hit}`. {DENY_MESSAGE}",
                    }
                }))
                return
    except ValueError:
        return


if __name__ == "__main__":
    main()
