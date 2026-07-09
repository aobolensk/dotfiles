#!/usr/bin/env python3

import argparse
import datetime
import os
import runpy
import shutil
import subprocess

OVERLAY_MARKER = ".dotfiles-overlay"

OVERLAY_SKIP_ROOT_FILES = {
    OVERLAY_MARKER,
    ".gitignore",
    ".gitattributes",
    ".gitmodules",
    "README.md",
    "deploy.py",
}

dotfiles_dir = os.path.dirname(os.path.abspath(__file__))
# Use os.path.expanduser to determine the user's home directory in a
# platform independent manner even if the HOME environment variable is not set.
home_dir = os.path.expanduser("~")


def is_ignored_by_git(file_path):
    result = subprocess.run(
        ["git", "check-ignore", "-q", file_path],
        cwd=dotfiles_dir,
        capture_output=True,
    )
    return result.returncode == 0


def log(args, message):
    if not args.quiet:
        print(message)


def confirm(args, prompt):
    return args.y or input(prompt).lower().startswith("y")


def get_backup_root(args):
    if not args.backup_timestamp:
        args.backup_timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(args.backup_dir, args.backup_timestamp)


def get_backup_path(path, args):
    relative_path = os.path.relpath(path, home_dir)
    backup_path = os.path.join(get_backup_root(args), relative_path)
    if not os.path.lexists(backup_path):
        return backup_path

    suffix = 1
    while True:
        candidate_path = f"{backup_path}.{suffix}"
        if not os.path.lexists(candidate_path):
            return candidate_path
        suffix += 1


def remove_or_backup_existing_path(path, args):
    if not args.backup:
        if os.path.isdir(path) and not os.path.islink(path):
            log(args, f"Error: {path} is a real directory; use --backup to replace it safely.")
            return False
        try:
            os.remove(path)
        except OSError as e:
            log(args, f"Error: could not remove {path}: {e}")
            return False
        return True

    backup_path = get_backup_path(path, args)
    try:
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.move(path, backup_path)
    except OSError as e:
        log(args, f"Error: could not back up {path} -> {backup_path}: {e}")
        return False
    log(args, f"Backed up: {path} -> {backup_path}")
    return True


def discover_overlays():
    for entry in sorted(os.listdir(dotfiles_dir)):
        overlay_path = os.path.join(dotfiles_dir, entry)
        if os.path.isdir(overlay_path) and os.path.isfile(os.path.join(overlay_path, OVERLAY_MARKER)):
            yield overlay_path


def deploy_overlay(overlay_path, args):
    apply_ignore_filter = not is_ignored_by_git(overlay_path)
    for root, dirs, files in os.walk(overlay_path):
        dirs[:] = [d for d in dirs if d not in (".git", ".hg", ".svn")]
        for file in files:
            if root == overlay_path and file in OVERLAY_SKIP_ROOT_FILES:
                continue
            overlay_file_path = os.path.join(root, file)
            if apply_ignore_filter and is_ignored_by_git(overlay_file_path):
                continue
            home_path = os.path.join(home_dir, os.path.relpath(overlay_file_path, overlay_path))
            if os.path.islink(home_path) and os.readlink(home_path) == overlay_file_path:
                continue
            if os.path.lexists(home_path):
                if not confirm(args, f"Do you want to replace {overlay_file_path} -> {home_path}? "):
                    continue
                if not args.dry_run:
                    if not remove_or_backup_existing_path(home_path, args):
                        continue
                elif os.path.isdir(home_path) and not os.path.islink(home_path) and not args.backup:
                    log(args, f"Error: {home_path} is a real directory; use --backup to replace it safely.")
                    continue
                elif args.backup:
                    backup_path = get_backup_path(home_path, args)
                    log(args, f"Back up: {home_path} -> {backup_path}")
            if not args.dry_run:
                try:
                    os.makedirs(os.path.dirname(home_path), exist_ok=True)
                    os.symlink(overlay_file_path, home_path)
                except OSError as e:
                    log(args, f"Error: could not symlink {overlay_file_path} -> {home_path}: {e}")
                    continue
            log(args, f"Added symlink: {overlay_file_path} -> {home_path}")


def materialize_codex_skills(overlay_path, args, reset_target):
    # Codex does not discover skills through symlinks, so materialize a copy
    # See https://github.com/openai/codex/issues/11314 and https://github.com/openai/codex/issues/15756
    home_agents_skills = os.path.join(home_dir, ".agents", "skills")
    skill_dirs = []
    for skill_dir in (".agents/skills", ".claude/skills"):
        skill_dir = os.path.realpath(os.path.join(overlay_path, skill_dir))
        if os.path.isdir(skill_dir) and skill_dir not in skill_dirs:
            skill_dirs.append(skill_dir)
    if not skill_dirs:
        return False
    if reset_target and os.path.lexists(home_agents_skills) and not args.dry_run:
        if os.path.isdir(home_agents_skills) and not os.path.islink(home_agents_skills):
            shutil.rmtree(home_agents_skills)
        else:
            os.remove(home_agents_skills)
    if not args.dry_run:
        os.makedirs(home_agents_skills, exist_ok=True)
    for skill_dir in skill_dirs:
        if not args.dry_run:
            shutil.copytree(skill_dir, home_agents_skills, dirs_exist_ok=True)
        log(args, f"Copied skills: {skill_dir} -> {home_agents_skills}")
    # Symlink ~/.gemini/skills to ~/.agents/skills
    if not args.dry_run:
        os.makedirs(os.path.join(home_dir, ".gemini"), exist_ok=True)
        try:
            os.symlink(home_agents_skills, os.path.join(home_dir, ".gemini", "skills"))
        except FileExistsError:
            pass

    return True


def run_overlay_deploy_hook(overlay_path, args):
    hook_path = os.path.join(overlay_path, "deploy.py")
    if not os.path.isfile(hook_path) or args.dry_run:
        return
    log(args, f"Running overlay deploy hook: {hook_path}")
    runpy.run_path(hook_path, run_name="__hook__")["main"](args)


def run_deploy():
    parser = argparse.ArgumentParser(
        description="""
Dotfiles deployment script.
- discovers every top-level directory containing a `{marker}` file and treats
  it as an overlay whose contents are symlinked into ~ preserving relative paths.
- runs installation scripts for extensions.
""".format(marker=OVERLAY_MARKER), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-y', action='store_true', help='Force yes')
    parser.add_argument(
        '--vscode-path',
        default="code",
        help='Path or name of VS Code executable to use for extensions (default: code)',
    )
    parser.add_argument(
        '--no-vscode-extensions',
        action='store_true',
        help='Skip VS Code extension installation',
    )
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress informational output')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (does not affect any files)')
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Move replaced files into a timestamped backup directory instead of deleting them',
    )
    parser.add_argument(
        '--backup-dir',
        default=os.path.join(home_dir, ".dotfiles-backup"),
        help='Directory for backups when --backup is used (default: ~/.dotfiles-backup)',
    )
    args = parser.parse_args()
    args.backup_dir = os.path.abspath(os.path.expanduser(args.backup_dir))
    args.backup_timestamp = None

    log(args, "----------------------------\n"
              "Starting dotfiles deployment\n"
              "----------------------------")
    found_overlay = False
    reset_codex_skills = True
    for overlay_path in discover_overlays():
        found_overlay = True
        log(args, f"Deploying overlay: {overlay_path}")
        deploy_overlay(overlay_path, args)
        if materialize_codex_skills(overlay_path, args, reset_codex_skills):
            reset_codex_skills = False
        run_overlay_deploy_hook(overlay_path, args)
    if not found_overlay:
        log(args, f"No overlays found (looking for directories containing {OVERLAY_MARKER}).")
    if (
        not args.no_vscode_extensions
        and confirm(args, "Do you want to install VSCode extensions? ")
        and not args.dry_run
    ):
        subprocess.call(["bash", os.path.join(dotfiles_dir, "vscode-extensions.sh"), args.vscode_path])
    log(args, "----------------------------\n"
              "Dotfiles deployment is done \n"
              "----------------------------")


def main():
    try:
        run_deploy()
    except KeyboardInterrupt:
        print("\nAborted.")
        raise SystemExit(130)


if __name__ == "__main__":
    main()
