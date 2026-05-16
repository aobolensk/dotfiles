#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess

OVERLAY_MARKER = ".dotfiles-overlay"

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
    # If the overlay directory itself is gitignored in the public repo
    # (e.g. dotfiles-private/), don't apply the per-file ignore filter inside
    # it: the overlay has its own VCS rules, not ours.
    apply_ignore_filter = not is_ignored_by_git(overlay_path)
    for root, dirs, files in os.walk(overlay_path):
        for file in files:
            if file == OVERLAY_MARKER:
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


def materialize_codex_skills(overlay_path, args):
    # Codex does not discover skills through symlinks, so materialize a copy
    # See https://github.com/openai/codex/issues/11314 and https://github.com/openai/codex/issues/15756
    repo_agents_skills = os.path.join(overlay_path, ".agents", "skills")
    home_agents_skills = os.path.join(home_dir, ".agents", "skills")
    if not os.path.isdir(repo_agents_skills):
        return
    if os.path.lexists(home_agents_skills) and not args.dry_run:
        if os.path.isdir(home_agents_skills) and not os.path.islink(home_agents_skills):
            shutil.rmtree(home_agents_skills)
        else:
            os.remove(home_agents_skills)
    if not args.dry_run:
        shutil.copytree(repo_agents_skills, home_agents_skills)
    if not args.quiet:
        print("Copied skills: " + repo_agents_skills + " -> " + home_agents_skills)


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
    for overlay_path in overlays:
        if not args.quiet:
            print("Deploying overlay: " + overlay_path)
        deploy_overlay(overlay_path, args)
        materialize_codex_skills(overlay_path, args)
    if args.y or input("Do you want to install VSCode extensions? ").lower().startswith("y"):
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
