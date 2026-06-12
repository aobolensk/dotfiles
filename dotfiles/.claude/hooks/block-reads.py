#!/usr/bin/env python3
"""
PreToolUse hook: deny reading files whose name/path matches block-reads.txt

Covers the Read tool (file_path) and common shell read commands (cat, less,
head, tail, ...) passed to Bash. See block-reads.txt for the patterns.
"""

import fnmatch
import json
import shlex
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("block-reads.txt")
DENY_MESSAGE = "Reading this file is on the deny-list. Ask the user before reading it."
PIPE_OPS = {";", "&&", "||", "|", "&", "|&", "(", ")"}
# Shell programs that read file contents to stdout / a pager.
READ_PROGS = {
    "cat", "bat", "less", "more", "head", "tail", "tac", "nl",
    "od", "xxd", "hexdump", "strings", "grep", "egrep", "fgrep",
    "rg", "ag", "awk", "sed", "cut", "sort", "uniq", "wc",
    "vi", "vim", "nvim", "view", "open", "xdg-open",
}


def load_patterns():
    try:
        text = CONFIG_PATH.read_text()
    except OSError:
        return []
    out = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def matches(path, patterns):
    """Return the first pattern matching the given path, or None."""
    if not path:
        return None
    name = path.rsplit("/", 1)[-1]
    for pat in patterns:
        target = path if "/" in pat else name
        if fnmatch.fnmatch(target, pat):
            return pat
    return None


def _lex_segments(text):
    lex = shlex.shlex(text, posix=True, punctuation_chars=True)
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


def subcommands(cmd):
    """Yield token lists per pipeline segment, respecting shell quoting."""
    # Split on newlines first: shlex treats a newline as ordinary whitespace,
    # so without this a multi-line command collapses into one segment and a
    # reader on a later line hides behind a benign program on the first line.
    for line in cmd.splitlines():
        if line.strip():
            yield from _lex_segments(line)


def scan_bash(cmd, patterns):
    """Return (pattern, path) for the first blocked file arg, or None."""
    try:
        segments = list(subcommands(cmd))
    except ValueError:
        return None
    for tokens in segments:
        if not tokens:
            continue
        prog = tokens[0].rsplit("/", 1)[-1]
        if prog not in READ_PROGS:
            continue
        for arg in tokens[1:]:
            if arg.startswith("-"):
                continue
            hit = matches(arg, patterns)
            if hit:
                return hit, arg
    return None


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    patterns = load_patterns()
    if not patterns:
        return
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}

    if tool == "Read":
        path = tool_input.get("file_path", "")
        hit = matches(path, patterns)
        if hit:
            deny(f"Blocked reading `{path}` (pattern `{hit}`). {DENY_MESSAGE}")
        return

    if tool == "Bash":
        cmd = tool_input.get("command", "")
        if not cmd:
            return
        found = scan_bash(cmd, patterns)
        if found:
            pat, path = found
            deny(f"Blocked reading `{path}` (pattern `{pat}`). {DENY_MESSAGE}")
        return


if __name__ == "__main__":
    main()
