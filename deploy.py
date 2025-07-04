#!/usr/bin/env python3

import argparse
import os
import subprocess

exclude_dirs = [
    ".git",
    ".github",
    "__pycache__",
]
exclude_files = [
    ".editorconfig",
    "LICENSE",
    "README.md",
    "deploy.py",
    "update.py",
    "vscode-extensions.sh"
]

sh_execute = "bash"

dotfiles_dir = os.path.dirname(os.path.abspath(__file__))
# Use os.path.expanduser to determine the user's home directory in a
# platform independent manner even if the HOME environment variable is not set.
home_dir = os.path.expanduser("~")


def main():
    parser = argparse.ArgumentParser(description="""
Dotfiles deployment script.
- replaces user configuration files with symlinks to synchronized ones stored in this git repository.
- runs installation scripts for extensions.
""", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-y', action='store_true', dest='y', help='Force yes')
    parser.add_argument('--dry-run', action='store_true', dest='dry_run', help='Dry run (does not affect any files)')
    args = parser.parse_args()
    print("----------------------------\n"
          "Starting dotfiles deployment\n"
          "----------------------------")
    for root, dirs, files in os.walk(dotfiles_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files:
                continue
            dotfiles_path = os.path.join(root, file)
            home_path = os.path.join(root.replace(dotfiles_dir, home_dir), file)
            if os.path.islink(home_path) and os.readlink(home_path) == dotfiles_path:
                continue
            if os.path.lexists(home_path):
                if not args.y and not input(
                        "Do you want to replace " +
                        dotfiles_path + " -> " + home_path + "? ").lower().startswith("y"):
                    continue
                if not args.dry_run:
                    os.remove(home_path)
            if not args.dry_run:
                os.makedirs(os.path.dirname(home_path), exist_ok=True)
                os.symlink(dotfiles_path, home_path)
            print("Added symlink: " + dotfiles_path + " -> " + home_path)
    if args.y or input("Do you want to install VSCode extensions? ").lower().startswith("y"):
        if not args.dry_run:
            subprocess.call([
                sh_execute,
                os.path.join(dotfiles_dir, "vscode-extensions.sh"),
            ])
    print("----------------------------\n"
          "Dotfiles deployment is done \n"
          "----------------------------")


if __name__ == "__main__":
    main()
