#!/usr/bin/env bash
input=$(cat)

c_reset=$'\033[0m'
c_branch=$'\033[35m'
c_model=$'\033[36m'
c_effort=$'\033[90m'
c_ctx=$'\033[33m'
c_tok=$'\033[34m'
c_cost=$'\033[32m'
c_rl=$'\033[31m'
c_add=$'\033[32m'
c_del=$'\033[31m'

IFS=$'\x1f' read -r cwd model effort ctx_pct ctx_size tok_in tok_out cost rl_5h rl_7d < <(
    jq -r '[
        .workspace.current_dir // .cwd // "",
        .model.display_name // "",
        .effort.level // "",
        .context_window.used_percentage // "",
        .context_window.context_window_size // "",
        .context_window.total_input_tokens // "",
        .context_window.total_output_tokens // "",
        .cost.total_cost_usd // "",
        .rate_limits.five_hour.used_percentage // "",
        .rate_limits.seven_day.used_percentage // ""
    ] | join("")' <<<"$input"
)

ctx_size_fmt=""
if [ -n "$ctx_size" ]; then
    if [ "$ctx_size" -ge 1000000 ]; then
        ctx_size_fmt="$((ctx_size / 1000000))M"
    else
        ctx_size_fmt="$((ctx_size / 1000))k"
    fi
fi

git_branch=""
diff_stat=""
if [ -n "$cwd" ]; then
    branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null \
             || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        flags=""
        git -C "$cwd" --no-optional-locks diff --no-ext-diff --quiet 2>/dev/null || flags="${flags}*"
        git -C "$cwd" --no-optional-locks diff --no-ext-diff --cached --quiet 2>/dev/null || flags="${flags}+"
        git -C "$cwd" --no-optional-locks ls-files --others --exclude-standard 2>/dev/null | grep -q . && flags="${flags}?"
        git_branch="(${branch}${flags})"

        read -r added removed < <(
            git -C "$cwd" --no-optional-locks diff --no-ext-diff --numstat HEAD 2>/dev/null \
                | awk '{a+=$1; r+=$2} END {printf "%d %d", a+0, r+0}'
        )
        [ "$added" -gt 0 ] || [ "$removed" -gt 0 ] && diff_stat="${c_add}+${added}${c_reset}/${c_del}-${removed}${c_reset}"
    fi
fi

parts=""
[ -n "$git_branch" ] && parts="${c_branch}${git_branch}${c_reset}"
parts="${parts} ${c_model}${model}${c_reset}"
[ -n "$effort" ] && parts="${parts}${c_effort}:${effort}${c_reset}"
[ -n "$ctx_pct" ] && parts="${parts} ${c_ctx}ctx:${ctx_pct}%$([ -n "$ctx_size_fmt" ] && echo "/${ctx_size_fmt}")${c_reset}"
[ -n "$tok_in" ] && parts="${parts} ${c_tok}in:${tok_in}/out:${tok_out}${c_reset}"
[ -n "$cost" ] && parts="${parts} ${c_cost}\$$(printf '%.3f' "$cost")${c_reset}"
[ -n "$rl_5h" ] && parts="${parts} ${c_rl}5h:${rl_5h}%${c_reset}"
[ -n "$rl_7d" ] && parts="${parts} ${c_rl}7d:${rl_7d}%${c_reset}"
[ -n "$diff_stat" ] && parts="${parts} ${diff_stat}"

printf '%s' "$parts"
