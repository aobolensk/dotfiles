#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess

dotfiles_dir = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(description="""
Dotfiles update script.
- gathers extensions list and updates installation scripts.
""", formatter_class=argparse.RawTextHelpFormatter)
    _ = parser.parse_args()
    if shutil.which("code"):
        with open(os.path.join(dotfiles_dir, "vscode-extensions.sh"), "w", encoding="utf-8", newline='\n') as f:
            f.write("#!/bin/sh\n\n")
            f.write("set -e\n\n")
            f.write("vscode_exec=${1:-code}\n\n")
            f.write("\"$vscode_exec\" --force \\\n")
            f.flush()
            proc = subprocess.run([
                "code",
                "--list-extensions",
            ], stdout=subprocess.PIPE, check=True)
            out = proc.stdout.decode("utf-8").strip().split('\n')
            for line in out:
                f.write("--install-extension {} \\\n".format(line))
    else:
        print("Warning: VSCode not found in PATH. Skipping extension update.")


if __name__ == "__main__":
    main()
