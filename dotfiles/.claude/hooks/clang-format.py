#!/usr/bin/env python3
"""
PostToolUse hook: run clang-format -i on edited C-family files.

Only formats when the extension is C-family and a .clang-format config governs
the file, so repos without config keep their style. Reads edited paths from
Claude (tool_input.file_path) or Codex (apply_patch command). Always exits 0 so
clang-format never blocks an edit.
"""

import json
import os
import re
import shutil
import subprocess
import sys

# Extensions clang-format handles well. Kept tight on purpose.
EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cxx", ".c++", ".cp", ".cu", ".cuh",
    ".h", ".hh", ".hpp", ".hxx", ".h++", ".inl", ".ipp", ".tpp",
    ".m", ".mm", ".proto",
}
CONFIG_NAMES = (".clang-format", "_clang-format")
# Codex apply_patch headers, e.g. "*** Update File: foo.cpp", "*** Move to: bar.cpp".
PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update|Move to)(?: File)?: (.+)$", re.MULTILINE)
# Unified diff hunk header, e.g. "@@ -12,3 +12,4 @@". Group 2 is new-file start, group 4 is new-file length.
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", re.MULTILINE)


def candidate_paths(payload):
    tool_input = payload.get("tool_input") or {}
    # Claude Code: single file path on the tool input.
    path = tool_input.get("file_path")
    if isinstance(path, str) and path:
        yield path
    # Codex apply_patch: parse paths out of the patch body.
    if payload.get("tool_name") == "apply_patch":
        command = tool_input.get("command")
        if isinstance(command, str):
            for match in PATCH_FILE_RE.findall(command):
                yield match.strip()


def has_clang_format_config(file_path):
    directory = os.path.dirname(os.path.abspath(file_path))
    while True:
        for name in CONFIG_NAMES:
            if os.path.isfile(os.path.join(directory, name)):
                return True
        parent = os.path.dirname(directory)
        if parent == directory:
            return False
        directory = parent


def git_root(file_path):
    directory = os.path.dirname(os.path.abspath(file_path))
    result = subprocess.run(
        ["git", "-C", directory, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def is_tracked(repo_root, file_path):
    result = subprocess.run(
        ["git", "-C", repo_root, "ls-files", "--error-unmatch", file_path],
        capture_output=True,
        timeout=10,
    )
    return result.returncode == 0


def changed_line_ranges(repo_root, file_path):
    """Return "start:end" strings (clang-format --lines syntax) for hunks changed since HEAD.

    Return None to format the whole file.
    """
    if not is_tracked(repo_root, file_path):
        return None
    result = subprocess.run(
        ["git", "-C", repo_root, "diff", "--unified=0", "--no-color", "HEAD", "--", file_path],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        return None
    ranges = []
    for start, length in HUNK_RE.findall(result.stdout):
        length = int(length) if length else 1
        if length == 0:
            # Pure deletion: clang-format has nothing to reformat on the new side.
            continue
        ranges.append("{}:{}".format(start, int(start) + length - 1))
    if not ranges:
        # No diff against HEAD (e.g. file matches HEAD already): nothing to format.
        return []
    return ranges


def should_format(file_path):
    if not os.path.isfile(file_path):
        return False
    if os.path.splitext(file_path)[1].lower() not in EXTENSIONS:
        return False
    return has_clang_format_config(file_path)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(payload, dict):
        return

    clang_format = shutil.which("clang-format")
    if not clang_format:
        return

    seen = set()
    for path in candidate_paths(payload):
        real = os.path.realpath(path)
        if real in seen:
            continue
        seen.add(real)
        if not should_format(path):
            continue
        root = git_root(path)
        cmd = [clang_format, "-i", "--style=file"]
        if root:
            ranges = changed_line_ranges(root, path)
            if ranges == []:
                continue
            if ranges:
                cmd += ["--lines={}".format(r) for r in ranges]
        cmd.append(path)
        try:
            subprocess.run(cmd, capture_output=True, timeout=30)
        except Exception:
            pass


if __name__ == "__main__":
    main()
