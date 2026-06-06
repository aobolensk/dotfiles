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
        try:
            subprocess.run(
                [clang_format, "-i", "--style=file", path],
                capture_output=True,
                timeout=30,
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
