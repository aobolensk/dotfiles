import argparse
import os
import subprocess
import sys

exclude_dirs = [".git"]
exclude_files = [
    "deploy.py",
    "update.py",
    "README.md",
    "LICENSE",
    "vscode-extensions.sh"
]

sh_execute = "bash"

dotfiles_dir = os.path.dirname(os.path.abspath(__file__))
home_dir = os.environ['HOME']

def main():
    parser = argparse.ArgumentParser(description="""
Dotfiles deployment script.
- replaces user configuration files with symlinks to synchronized ones stored in this git repository.
- runs installation scripts for extensions.
""", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-y', action='store_true', dest='y', help='Force yes')
    args = parser.parse_args()
    print("----------------------------"
          "Starting dotfiles deployment"
          "----------------------------")
    for root, dirs, files in os.walk(dotfiles_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files:
                continue
            dotfiles_path = os.path.join(root, file)
            home_path = os.path.join(root.replace(dotfiles_dir, home_dir), file)
            if os.path.islink(home_path):
                continue
            if not args.y and not input("Do you want to replace " +
                dotfiles_path + " -> " + home_path + "? ").lower().startswith("y"):
                continue
            if os.path.exists(home_path):
                os.remove(home_path)
            os.makedirs(os.path.dirname(home_path), exist_ok=True)
            os.symlink(dotfiles_path, home_path)
            print("Added symlink: " + dotfiles_path + " -> " + home_path)
    if args.y or input("Do you want to install VSCode extensions? ").lower().startswith("y"):
        subprocess.call(sh_execute + ' ' + os.path.join(dotfiles_dir, "vscode-extensions.sh"), shell=True)
    print("----------------------------"
          "Dotfiles deployment is done "
          "----------------------------")

if __name__ == "__main__":
    main()
