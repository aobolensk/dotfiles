import subprocess

def main():
    with open("vscode-extensions.sh", "w") as f:
        f.write("#!/bin/sh\n")
        f.write("code \\\n")
        f.flush()
        subprocess.call("code --list-extensions | xargs -L 1 -I '$' echo '--install-extension $ \\'", stdout=f, shell=True)

if __name__ == "__main__":
    main()
