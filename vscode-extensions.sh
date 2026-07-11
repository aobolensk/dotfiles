#!/bin/sh

set -e

vscode_exec=${1:-code}

"$vscode_exec" --force \
--install-extension alefragnani.bookmarks \
--install-extension anthropic.claude-code \
--install-extension cschlosser.doxdocgen \
--install-extension docker.docker \
--install-extension eamodio.gitlens \
--install-extension editorconfig.editorconfig \
--install-extension esbenp.prettier-vscode \
--install-extension galarius.vscode-opencl \
--install-extension github.vscode-github-actions \
--install-extension github.vscode-pull-request-github \
--install-extension jackiotyu.git-worktree-manager \
--install-extension james-yu.latex-workshop \
--install-extension jeff-hykin.better-cpp-syntax \
--install-extension kisstkondoros.vscode-gutter-preview \
--install-extension lextudio.restructuredtext \
--install-extension lextudio.restructuredtext-pack \
--install-extension llvm-vs-code-extensions.vscode-mlir \
--install-extension mechatroner.rainbow-csv \
--install-extension mohsen1.prettify-json \
--install-extension ms-azuretools.vscode-containers \
--install-extension ms-azuretools.vscode-docker \
--install-extension ms-python.debugpy \
--install-extension ms-python.isort \
--install-extension ms-python.python \
--install-extension ms-python.vscode-pylance \
--install-extension ms-python.vscode-python-envs \
--install-extension ms-toolsai.jupyter \
--install-extension ms-toolsai.jupyter-keymap \
--install-extension ms-toolsai.jupyter-renderers \
--install-extension ms-toolsai.vscode-jupyter-cell-tags \
--install-extension ms-toolsai.vscode-jupyter-slideshow \
--install-extension ms-vscode-remote.remote-containers \
--install-extension ms-vscode-remote.remote-ssh \
--install-extension ms-vscode-remote.remote-ssh-edit \
--install-extension ms-vscode-remote.remote-wsl \
--install-extension ms-vscode-remote.vscode-remote-extensionpack \
--install-extension ms-vscode.cmake-tools \
--install-extension ms-vscode.cpp-devtools \
--install-extension ms-vscode.cpptools \
--install-extension ms-vscode.cpptools-extension-pack \
--install-extension ms-vscode.cpptools-themes \
--install-extension ms-vscode.remote-explorer \
--install-extension ms-vscode.remote-server \
--install-extension openai.chatgpt \
--install-extension openai.openai-chatgpt-adhoc \
--install-extension redhat.vscode-yaml \
--install-extension rreverser.llvm \
--install-extension streetsidesoftware.code-spell-checker \
--install-extension streetsidesoftware.code-spell-checker-russian \
--install-extension takumii.markdowntable \
--install-extension trond-snekvik.simple-rst \
--install-extension twxs.cmake \
--install-extension tyriar.sort-lines \
--install-extension vscode-icons-team.vscode-icons \
--install-extension vscodevim.vim \
--install-extension xaver.clang-format \
