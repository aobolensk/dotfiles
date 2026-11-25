#!/usr/bin/env python3
"""
SessionStart / PreToolUse hook: keep Claude scratch files in
$CLAUDE_CODE_TMPDIR/claude-<uid>/tmp, next to its own temp files and worktrees.

SessionStart points TMPDIR, TMP and TEMP of Bash commands there and tells Claude
the path. PreToolUse denies writing files under /tmp or /var/tmp outside the
Claude Code temp dir and the project, Bash commands that mention them, and
writing .log files outside the scratch dir.
"""

import json
import os
import re
import shlex
import stat
import sys

TMP_DIRS = ("/tmp", "/var/tmp")
# /tmp or /var/tmp with the path after it, unless part of a longer path or word.
TMP_PATH = re.compile(r"(?<![\w.~/})-])/(?:var/)?tmp(?![\w.-])[^\s'\"`;|&()<>,:{}]*")
# $TMPDIR, $TMP or $TEMP at the start of a path, which SessionStart points at the scratch dir.
TMP_VAR = re.compile(r"^\$\{?(?:TMPDIR|TMP|TEMP)\}?(?=/|$)")
PIPE_OPS = {";", "&&", "||", "|", "&", "|&", "(", ")"}
REDIRECTS = {">", ">>", ">|", ">&", "&>", "&>>"}


def scratch_dir():
    # Same base Claude Code uses for its own temp files.
    base = os.environ.get("CLAUDE_CODE_TMPDIR")
    if not base:
        import tempfile  # Slow to import, so only when needed.
        base = tempfile.gettempdir()
    root = os.path.join(os.path.realpath(base), "claude-{}".format(os.getuid()))
    # The base may be a shared /tmp, so refuse a directory another user planted.
    os.makedirs(root, mode=0o700, exist_ok=True)
    st = os.lstat(root)
    if stat.S_ISLNK(st.st_mode) or st.st_uid != os.getuid():
        sys.exit("{} is not a directory owned by the current user".format(root))
    path = os.path.join(root, "tmp")
    os.makedirs(path, exist_ok=True)
    return path


def allowed_dirs(scratch):
    # Claude Code temp files and worktrees sit next to the scratch dir, and the user may keep a project in /tmp.
    dirs = [os.path.dirname(scratch)]
    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if project:
        dirs.append(os.path.realpath(project))
    return dirs


def inside(path, dirs):
    return any(path == d or path.startswith(d + "/") for d in dirs)


def blocked(path, allowed):
    path = os.path.normpath(path)
    return inside(path, TMP_DIRS) and not inside(os.path.realpath(path), allowed)


def subcommands(command):
    """Yield token lists per pipeline segment, respecting shell quoting, like block-reads.py."""
    # shlex treats a newline as whitespace, so lex each line on its own.
    for line in command.splitlines():
        lex = shlex.shlex(line, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        try:
            tokens = list(lex)
        except ValueError:
            continue
        cur = []
        for tok in tokens + [";"]:
            if tok not in PIPE_OPS:
                cur.append(tok)
            elif cur:
                yield cur
                cur = []


def resolve(path, cwd, scratch):
    return os.path.join(cwd, os.path.expanduser(TMP_VAR.sub(lambda m: scratch, path)))


def log_writes(command, cwd, scratch):
    """Yield the .log files that redirects and tee in the command write, following its cd."""
    for tokens in subcommands(command):
        prog = os.path.basename(tokens[0])
        args = [t for t in tokens[1:] if not t.startswith("-")]
        if prog == "cd":
            cwd = resolve(args[0] if args else "~", cwd, scratch)
            continue
        if prog in ("bash", "sh") and "-c" in tokens[1:-1]:
            yield from log_writes(tokens[tokens.index("-c") + 1], cwd, scratch)
        targets = [t for op, t in zip(tokens, tokens[1:]) if op in REDIRECTS]
        if prog == "tee":
            targets += args
        yield from (resolve(t, cwd, scratch) for t in targets if t.endswith(".log"))


def misplaced_log(path, scratch):
    # Other variables can not be resolved here, so let them through.
    return "$" not in path and path.endswith(".log") and not inside(os.path.realpath(path), (scratch,))


def session_start():
    scratch = scratch_dir()
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    hint = ""
    if env_file:
        with open(env_file, "a") as f:
            f.write("export TMPDIR={0} TMP={0} TEMP={0}\n".format(shlex.quote(scratch)))
        hint = " ($TMPDIR in Bash)"
    print("Put scratch files, logs, repros and clones in {}{}, not in /tmp.".format(scratch, hint))


def pre_tool_use(payload):
    scratch = scratch_dir()
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    if tool == "Bash":
        command = tool_input.get("command") or ""
        paths = TMP_PATH.findall(command)
        logs = list(log_writes(command, payload.get("cwd") or os.getcwd(), scratch))
    else:
        paths = [tool_input.get("file_path") or ""]
        logs = paths if tool == "Write" else []
    allowed = allowed_dirs(scratch)
    hits = [p for p in paths if blocked(p, allowed)] + [p for p in logs if misplaced_log(p, scratch)]
    if hits:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Blocked `{}`. Use {} ($TMPDIR in Bash) for scratch files and logs "
                                            "instead. To read a file the user put in /tmp, use the Read tool."
                                            .format(hits[0], scratch),
            }
        }))


def main():
    payload = json.load(sys.stdin)
    event = payload.get("hook_event_name")
    if event == "SessionStart":
        session_start()
    elif event == "PreToolUse":
        pre_tool_use(payload)


if __name__ == "__main__":
    main()
