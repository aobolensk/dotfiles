import os
import subprocess
import sys

exclude_dirs = [".git"]
exclude_files = [
    "deploy.py",
    "update.py",
    "README.md",
    "vscode-extensions.sh"
]

dotfiles_dir = os.path.dirname(os.path.abspath(__file__))
home_dir = os.environ['HOME']

def main():
    print("----------------------------")
    print("Starting dotfiles deployment")
    print("----------------------------")
    for root, dirs, files in os.walk(dotfiles_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files:
                continue
            dotfiles_path = os.path.join(root, file)
            home_path = os.path.join(root.replace(dotfiles_dir, home_dir), file)
            if not input("Do you want to replace " +
                dotfiles_path + " -> " + home_path + "? ").lower().startswith("y"):
                continue
            if os.path.exists(home_path):
                os.remove(home_path)
            os.makedirs(os.path.dirname(home_path), exist_ok=True)
            os.symlink(dotfiles_path, home_path)
            print("Added symlink: " + dotfiles_path + " -> " + home_path)
    if input("Do you want to install VSCode extensions? ").lower().startswith("y"):
        subprocess.call("source " + os.path.join(dotfiles_dir, "vscode-extensions.sh"), shell=True)
    print("----------------------------")
    print("Dotfiles deployment is done")
    print("----------------------------")

if __name__ == "__main__":
    main()
