#!/usr/bin/env python3

import argparse
import fnmatch
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


def parse_gitignore(gitignore_path):
    if not os.path.exists(gitignore_path):
        return []

    patterns = []
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                patterns.append(line)
    return patterns


def is_ignored_by_git(file_path, gitignore_patterns):
    rel_path = os.path.relpath(file_path, dotfiles_dir)

    for pattern in gitignore_patterns:
        if pattern.endswith('/'):
            dir_pattern = pattern[:-1]
            if fnmatch.fnmatch(rel_path, dir_pattern) or fnmatch.fnmatch(rel_path, dir_pattern + '/*'):
                return True
            path_parts = rel_path.split(os.sep)
            for i in range(len(path_parts)):
                partial_path = os.sep.join(path_parts[:i+1])
                if fnmatch.fnmatch(partial_path, dir_pattern):
                    return True
        else:
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            if '/' not in pattern and fnmatch.fnmatch(os.path.basename(rel_path), pattern):
                return True

    return False


def main():
    parser = argparse.ArgumentParser(description="""
Dotfiles deployment script.
- replaces user configuration files with symlinks to synchronized ones stored in this git repository.
- runs installation scripts for extensions.
""", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-y', action='store_true', dest='y', help='Force yes')
    parser.add_argument(
        '--vscode-path',
        dest='vscode_path',
        default="code",
        help='Path or name of VS Code executable to use for extensions (default: code)',
    )
    parser.add_argument('--dry-run', action='store_true', dest='dry_run', help='Dry run (does not affect any files)')
    args = parser.parse_args()

    gitignore_path = os.path.join(dotfiles_dir, '.gitignore')
    gitignore_patterns = parse_gitignore(gitignore_path)

    global_gitignore_path = os.path.join(dotfiles_dir, '.gitignore_global')
    gitignore_patterns.extend(parse_gitignore(global_gitignore_path))

    print("----------------------------\n"
          "Starting dotfiles deployment\n"
          "----------------------------")
    for root, dirs, files in os.walk(dotfiles_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files:
                continue
            dotfiles_path = os.path.join(root, file)

            if is_ignored_by_git(dotfiles_path, gitignore_patterns):
                continue
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
            vscode_exec = args.vscode_path
            subprocess.call([
                sh_execute,
                os.path.join(dotfiles_dir, "vscode-extensions.sh"),
                vscode_exec,
            ])
    print("----------------------------\n"
          "Dotfiles deployment is done \n"
          "----------------------------")


if __name__ == "__main__":
    main()
