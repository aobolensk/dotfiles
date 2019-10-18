import os

exclude_dirs = ".git"
exclude_files = "deploy.py"

dotfiles_dir = os.path.dirname(os.path.abspath(__file__))
home_dir = os.environ['HOME']

def main():
    for root, dirs, files in os.walk(dotfiles_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files:
                continue
            dotfiles_path = os.path.join(root, file)
            home_path = os.path.join(root.replace(dotfiles_dir, home_dir), file)
            if (os.path.exists(home_path) and
                not input("Do you want to replace " +
                dotfiles_path + " -> " + home_path + "? ").lower().startswith("y")):
                continue
            if os.path.exists(home_path):
                os.remove(home_path)
            os.symlink(dotfiles_path, home_path)
            print("Added symlink: " + dotfiles_path + " -> " + home_path)


if __name__ == "__main__":
    main()
