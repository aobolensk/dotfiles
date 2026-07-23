#!/usr/bin/env bash
# Fetch all three PR comment sources for the given PR number (or current
# branch's PR if omitted) and print them as newline-delimited JSON, one
# object per comment, each tagged with a "source" field:
#   inline  - repos/{owner}/{repo}/pulls/{number}/comments   (file/line review comments)
#   review  - repos/{owner}/{repo}/pulls/{number}/reviews     (review-level summary bodies)
#   issue   - repos/{owner}/{repo}/issues/{number}/comments   (general PR conversation comments)
set -euo pipefail

pr="${1:-}"
[ -n "$pr" ] || pr=$(bash "$(dirname "$0")/find-pr.sh")

gh api "repos/{owner}/{repo}/pulls/$pr/comments" --paginate \
    --jq '.[] | . + {source: "inline"}'
gh api "repos/{owner}/{repo}/pulls/$pr/reviews" --paginate \
    --jq '.[] | . + {source: "review"}'
gh api "repos/{owner}/{repo}/issues/$pr/comments" --paginate \
    --jq '.[] | . + {source: "issue"}'
