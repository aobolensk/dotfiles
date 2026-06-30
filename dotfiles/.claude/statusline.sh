#!/usr/bin/env bash
input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
model=$(echo "$input" | jq -r '.model.display_name // ""')
ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // ""')
tok_in=$(echo "$input" | jq -r '.context_window.total_input_tokens // ""')
tok_out=$(echo "$input" | jq -r '.context_window.total_output_tokens // ""')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // ""')

git_branch=""
if [ -n "$cwd" ] && git -C "$cwd" --no-optional-locks rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null \
             || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        flags=""
        git -C "$cwd" --no-optional-locks diff --no-ext-diff --quiet 2>/dev/null || flags="${flags}*"
        git -C "$cwd" --no-optional-locks diff --no-ext-diff --cached --quiet 2>/dev/null || flags="${flags}+"
        [ -n "$(git -C "$cwd" --no-optional-locks ls-files --others --exclude-standard 2>/dev/null)" ] && flags="${flags}?"
        git_branch="(${branch}${flags})"
    fi
fi

parts=""
[ -n "$git_branch" ] && parts="${git_branch}"
parts="${parts} ${model}"
[ -n "$ctx_pct" ] && parts="${parts} ctx:${ctx_pct}%"
[ -n "$tok_in" ] && parts="${parts} in:${tok_in}/out:${tok_out}"
[ -n "$cost" ] && parts="${parts} \$$(printf '%.3f' "$cost")"

printf '%s' "$parts"
