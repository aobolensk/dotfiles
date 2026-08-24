#!/usr/bin/env bash
# Usage: revert-restore-diff.sh revert <path>...
#        revert-restore-diff.sh restore <diff-file>
#
# Temporarily removes uncommitted changes to specific paths without touching
# the index, so staged/unstaged status is preserved. Do not use `git stash`
# for this: `git stash pop` drops the staged/unstaged status of whatever it
# restores.
#
# `revert` captures the working-tree diff for <path>..., reverse-applies it,
# and prints the diff file path (pass it to `restore` later to put the
# changes back).

set -eu

mode=$1
shift

case "$mode" in
revert)
    diff_file=$(mktemp)
    git diff HEAD -- "$@" > "$diff_file"
    git apply -R "$diff_file"
    echo "$diff_file"
    ;;
restore)
    git apply "$1"
    rm -f "$1"
    ;;
*)
    echo "usage: revert-restore-diff.sh {revert <path>...|restore <diff-file>}" >&2
    exit 1
    ;;
esac
