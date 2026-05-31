#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess

OVERLAY_MARKER = ".dotfiles-overlay"

OVERLAY_SKIP_ROOT_FILES = {
    OVERLAY_MARKER,
    ".gitignore",
    ".gitattributes",
    ".gitmodules",
    "README.md",
}

sh_execute = "bash"

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


def discover_overlays():
    overlays = []
    for entry in sorted(os.listdir(dotfiles_dir)):
        overlay_path = os.path.join(dotfiles_dir, entry)
        if not os.path.isdir(overlay_path):
            continue
        if not os.path.isfile(os.path.join(overlay_path, OVERLAY_MARKER)):
            continue
        overlays.append(overlay_path)
    return overlays


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
            home_path = os.path.join(root.replace(overlay_path, home_dir), file)
            if os.path.islink(home_path) and os.readlink(home_path) == overlay_file_path:
                continue
            if os.path.lexists(home_path):
                if not args.y and not input(
                        "Do you want to replace " +
                        overlay_file_path + " -> " + home_path + "? ").lower().startswith("y"):
                    continue
                if not args.dry_run:
                    os.remove(home_path)
            if not args.dry_run:
                os.makedirs(os.path.dirname(home_path), exist_ok=True)
                os.symlink(overlay_file_path, home_path)
            if not args.quiet:
                print("Added symlink: " + overlay_file_path + " -> " + home_path)


def materialize_codex_skills(overlay_path, args, reset_target):
    # Codex does not discover skills through symlinks, so materialize a copy
    # See https://github.com/openai/codex/issues/11314 and https://github.com/openai/codex/issues/15756
    home_agents_skills = os.path.join(home_dir, ".agents", "skills")
    skill_dirs = []
    for skill_dir in (".agents/skills", ".claude/skills"):
        skill_dir = os.path.join(overlay_path, skill_dir)
        if os.path.isdir(skill_dir) and os.path.realpath(skill_dir) not in skill_dirs:
            skill_dirs.append(os.path.realpath(skill_dir))
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
        if not args.quiet:
            print("Copied skills: " + skill_dir + " -> " + home_agents_skills)
    # Symlink ~/.gemini/skills to ~/.agents/skills
    if not args.dry_run:
        os.makedirs(os.path.join(home_dir, ".gemini"), exist_ok=True)
        try:
            os.symlink(home_agents_skills, os.path.join(home_dir, ".gemini", "skills"))
        except FileExistsError:
            pass

    return True


def run_deploy():
    parser = argparse.ArgumentParser(description="""
Dotfiles deployment script.
- discovers every top-level directory containing a `{marker}` file and treats
  it as an overlay whose contents are symlinked into ~ preserving relative paths.
- runs installation scripts for extensions.
""".format(marker=OVERLAY_MARKER), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-y', action='store_true', dest='y', help='Force yes')
    parser.add_argument(
        '--vscode-path',
        dest='vscode_path',
        default="code",
        help='Path or name of VS Code executable to use for extensions (default: code)',
    )
    parser.add_argument(
        '--no-vscode-extensions',
        action='store_true',
        dest='no_vscode_extensions',
        help='Skip VS Code extension installation',
    )
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', help='Suppress informational output')
    parser.add_argument('--dry-run', action='store_true', dest='dry_run', help='Dry run (does not affect any files)')
    args = parser.parse_args()

    if not args.quiet:
        print("----------------------------\n"
              "Starting dotfiles deployment\n"
              "----------------------------")
    overlays = discover_overlays()
    if not overlays and not args.quiet:
        print("No overlays found (looking for directories containing " + OVERLAY_MARKER + ").")
    reset_codex_skills = True
    for overlay_path in overlays:
        if not args.quiet:
            print("Deploying overlay: " + overlay_path)
        deploy_overlay(overlay_path, args)
        if materialize_codex_skills(overlay_path, args, reset_codex_skills):
            reset_codex_skills = False
    install_vscode_extensions = not args.no_vscode_extensions and (
        args.y or input("Do you want to install VSCode extensions? ").lower().startswith("y")
    )
    if install_vscode_extensions:
        if not args.dry_run:
            vscode_exec = args.vscode_path
            subprocess.call([
                sh_execute,
                os.path.join(dotfiles_dir, "vscode-extensions.sh"),
                vscode_exec,
            ])
    if not args.quiet:
        print("----------------------------\n"
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
