#!/usr/bin/env bash
# Usage: stash-hunks.sh <patch-file> <message>
#
# Stashes only the hunks in <patch-file> (a -U0 diff against HEAD of tracked
# files): records them as a regular stash entry, then removes them from the
# working tree and the index. The index content is a per-file 3-way merge
# (index + HEAD - selected), so a patch mixing staged and unstaged hunks is
# handled. Leaves all other changes untouched.

set -eu

patch=$1
msg=$2
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

GIT_INDEX_FILE=$tmp/idx git read-tree HEAD
GIT_INDEX_FILE=$tmp/idx git apply --cached --unidiff-zero --recount "$patch"
tree=$(GIT_INDEX_FILE=$tmp/idx git write-tree)

git apply --numstat "$patch" | cut -f3- | while IFS= read -r path; do
    mode=$(git ls-files -s -- "$path" | cut -d' ' -f1)
    git show ":$path" > "$tmp/cur"
    git show "$tree:$path" > "$tmp/base"
    git show "HEAD:$path" > "$tmp/head"
    git merge-file -p "$tmp/cur" "$tmp/base" "$tmp/head" > "$tmp/out"
    printf '%s %s\t%s\n' "$mode" "$(git hash-object -w "$tmp/out")" "$path"
done > "$tmp/index-info"

label="On $(git branch --show-current): $msg"
index_commit=$(git commit-tree "HEAD^{tree}" -p HEAD -m "index on $label")
commit=$(git commit-tree "$tree" -p HEAD -p "$index_commit" -m "$label")
git stash store -m "$label" "$commit"

git apply -R --unidiff-zero --recount "$patch"
git update-index --index-info < "$tmp/index-info"
