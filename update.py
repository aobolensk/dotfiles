import subprocess

def main():
    with open("vscode-extensions.sh", "w") as f:
        subprocess.call("code --list-extensions | xargs -L 1 echo code --install-extension", stdout=f, shell=True)

if __name__ == "__main__":
    main()
