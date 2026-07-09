#!/usr/bin/env bash
input=$(cat)

IFS=$'\t' read -r cwd model effort ctx_pct tok_in tok_out cost < <(
    jq -r '[
        .workspace.current_dir // .cwd // "",
        .model.display_name // "",
        .effort.level // "",
        .context_window.used_percentage // "",
        .context_window.total_input_tokens // "",
        .context_window.total_output_tokens // "",
        .cost.total_cost_usd // ""
    ] | @tsv' <<<"$input"
)

git_branch=""
if [ -n "$cwd" ]; then
    branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null \
             || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        flags=""
        git -C "$cwd" --no-optional-locks diff --no-ext-diff --quiet 2>/dev/null || flags="${flags}*"
        git -C "$cwd" --no-optional-locks diff --no-ext-diff --cached --quiet 2>/dev/null || flags="${flags}+"
        git -C "$cwd" --no-optional-locks ls-files --others --exclude-standard 2>/dev/null | grep -q . && flags="${flags}?"
        git_branch="(${branch}${flags})"
    fi
fi

parts=""
[ -n "$git_branch" ] && parts="${git_branch}"
parts="${parts} ${model}"
[ -n "$effort" ] && parts="${parts}:${effort}"
[ -n "$ctx_pct" ] && parts="${parts} ctx:${ctx_pct}%"
[ -n "$tok_in" ] && parts="${parts} in:${tok_in}/out:${tok_out}"
[ -n "$cost" ] && parts="${parts} \$$(printf '%.3f' "$cost")"

printf '%s' "$parts"
