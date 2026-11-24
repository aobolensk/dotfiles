#!/usr/bin/env python3
"""
WorktreeCreate / WorktreeRemove / SessionEnd hook: keep Claude-created git worktrees under
$CLAUDE_CODE_TMPDIR/claude-<uid>/worktrees/<project-slug>/<name> instead of
<repo>/.claude/worktrees/<name>.

Mirrors the default git behavior: branch worktree-<name> from origin/HEAD
(falling back to HEAD), and removal deletes the worktree and that branch
unless it has unmerged commits.

Worktrees Claude creates itself (EnterWorktree, subagents) are recorded per
Claude process and force-removed after that process exits. Ones started with
`claude --worktree` are not, because they are created before the first prompt.
"""

import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import time


def git(*args):
    return subprocess.run(("git",) + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True)


def git_check(*args):
    res = git(*args)
    if res.returncode != 0:
        sys.exit("git {} failed: {}".format(" ".join(args), res.stderr.strip()))
    return res.stdout.strip()


def common_dir(path):
    res = git("-C", path, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return res.stdout.strip() if res.returncode == 0 else None


def is_registered(common, path):
    out = git_check("--git-dir", common, "worktree", "list", "--porcelain")
    return "worktree " + path in out.splitlines()


def ref_exists(common, ref):
    return git("--git-dir", common, "rev-parse", "--verify", "-q", ref).returncode == 0


def worktree_root():
    # Same base Claude Code uses for its own temp files.
    base = os.environ.get("CLAUDE_CODE_TMPDIR") or tempfile.gettempdir()
    root = os.path.join(os.path.realpath(base), "claude-{}".format(os.getuid()))
    # The base may be a shared /tmp, so refuse a directory another user planted.
    os.makedirs(root, mode=0o700, exist_ok=True)
    st = os.lstat(root)
    if stat.S_ISLNK(st.st_mode) or st.st_uid != os.getuid():
        sys.exit("{} is not a directory owned by the current user".format(root))
    return os.path.join(root, "worktrees")


def record_file(pid):
    return os.path.join(worktree_root(), ".sessions", pid)


def claude_pid():
    pid = os.environ.get("CLAUDE_PID", "")
    return pid if pid.isdigit() else None


def create(payload):
    # Same mapping as the default, so distinct names like a.b and a-b stay distinct.
    name = payload.get("name", "").replace("/", "+")
    if not re.fullmatch(r"[A-Za-z0-9._+-]+", name) or name in (".", ".."):
        sys.exit("invalid worktree name: {!r}".format(payload.get("name")))
    cwd = payload["cwd"]
    common = common_dir(cwd)
    if not common:
        sys.exit("not a git repository: {}".format(cwd))
    # Main checkout of a regular repo, or the git dir itself for bare repos and submodules.
    top = os.path.dirname(common) if os.path.basename(common) == ".git" else common
    dest = os.path.join(worktree_root(), re.sub(r"[^A-Za-z0-9]", "-", top), name)

    if os.path.exists(dest):
        if common_dir(dest) != common:
            sys.exit("{} exists and is not a worktree of {}".format(dest, top))
        print(dest)
        return

    if is_registered(common, dest):
        # The directory was deleted behind git, e.g. by a tmp cleanup.
        git_check("--git-dir", common, "worktree", "remove", "--force", dest)
    branch = "worktree-" + name
    if ref_exists(common, "refs/heads/" + branch):
        git_check("-C", cwd, "worktree", "add", dest, branch)
    else:
        base = "origin/HEAD" if ref_exists(common, "origin/HEAD^{commit}") else "HEAD"
        # No upstream, like the default. Tracking also writes .git/config, which fails for parallel creates.
        git_check("-C", cwd, "worktree", "add", "--no-track", "-b", branch, dest, base)

    pid = claude_pid()
    # prompt_id is absent until the first prompt, so `claude --worktree` is not recorded.
    if pid and payload.get("prompt_id"):
        record = record_file(pid)
        os.makedirs(os.path.dirname(record), exist_ok=True)
        with open(record, "a") as f:
            f.write("{}\t{}\n".format(common, dest))
    print(dest)


def remove(payload):
    path = payload["worktree_path"]
    common = common_dir(path) or common_dir(payload["cwd"])
    if not common:
        sys.exit("cannot find the repository of {}".format(path))
    if not is_registered(common, path):
        if os.path.exists(path):
            sys.exit("{} is not a worktree of {}".format(path, common))
        # Gone and unknown to this repo, so its branch is not ours to delete.
        return
    # Claude runs this hook from inside the worktree, and git fails once its cwd is deleted.
    os.chdir(common)
    git_check("--git-dir", common, "worktree", "remove", "--force", path)
    branch = "worktree-" + os.path.basename(path)
    if ref_exists(common, "refs/heads/" + branch):
        # Claude only checks for uncommitted files before removing, so keep unmerged commits.
        # Without an upstream, -d only checks HEAD, so also accept a branch merged into origin/HEAD.
        merged = git("--git-dir", common, "merge-base", "--is-ancestor", "refs/heads/" + branch,
                     "origin/HEAD").returncode == 0
        res = git("--git-dir", common, "branch", "-D" if merged else "-d", branch)
        if res.returncode != 0:
            print("kept branch {}: {}".format(branch, res.stderr.strip()), file=sys.stderr)


def alive(pid):
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    return True


def cleanup(pid):
    """Remove the worktrees recorded for a Claude process once it has exited."""
    while alive(pid):
        time.sleep(0.5)
    record = record_file(pid)
    claimed = "{}.{}".format(record, os.getpid())
    try:
        # Claim the record so a second cleanup for the same pid finds nothing to do.
        os.rename(record, claimed)
        with open(claimed) as f:
            lines = f.read().splitlines()
    except OSError:
        return
    for line in lines:
        common, path = line.split("\t")
        try:
            remove({"worktree_path": path, "cwd": common})
        except SystemExit as e:
            print(e, file=sys.stderr)
    os.unlink(claimed)


def main():
    if sys.argv[1:2] == ["--cleanup"]:
        cleanup(sys.argv[2])
        return
    payload = json.load(sys.stdin)
    event = payload.get("hook_event_name")
    if event == "WorktreeCreate":
        create(payload)
    elif event == "WorktreeRemove":
        remove(payload)
    elif event == "SessionEnd" and payload.get("reason") not in ("clear", "resume"):
        # /clear and /resume keep the Claude process running, possibly inside a worktree.
        pid = claude_pid()
        if pid and os.path.exists(record_file(pid)):
            # Detached, so it can wait for Claude to exit and is not bound by the hook timeout.
            with open(os.path.join(worktree_root(), "cleanup.log"), "a") as log:
                subprocess.Popen((sys.executable, os.path.realpath(__file__), "--cleanup", pid), cwd="/",
                                 start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=log)


if __name__ == "__main__":
    main()
