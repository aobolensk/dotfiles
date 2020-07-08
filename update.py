#!/usr/bin/python3

import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="""
Dotfiles update script.
- gathers extensions list and updates installation scripts.
""", formatter_class=argparse.RawTextHelpFormatter)
    args = parser.parse_args()
    with open("vscode-extensions.sh", "w") as f:
        f.write("#!/bin/sh\n")
        f.write("code \\\n")
        f.flush()
        subprocess.call("code --list-extensions | xargs -L 1 -I '$' echo '--install-extension $ \\'", stdout=f, shell=True)

if __name__ == "__main__":
    main()
