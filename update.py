#!/usr/bin/python3

import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="""
Dotfiles update script.
- gathers extensions list and updates installation scripts.
""", formatter_class=argparse.RawTextHelpFormatter)
    args = parser.parse_args()
    with open("vscode-extensions.sh", "w", encoding="utf-8", newline='\n') as f:
        f.write("#!/bin/sh\n")
        f.write("code \\\n")
        f.flush()
        proc = subprocess.run("code --list-extensions", stdout=subprocess.PIPE, shell=True, check=True)
        out = proc.stdout.decode("utf-8").strip().split('\n')
        for line in out:
            f.write("--install-extension {} \\\n".format(line))

if __name__ == "__main__":
    main()
