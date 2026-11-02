# dotfiles

## Dependencies

- required
  - git
  - Python 3.8+

## Supported applications

- bash
- i3wm

  Ubuntu:

  ```bash
  sudo apt install i3 i3-wm py3status i3lock-fancy xautolock
  ```

- vim
- tmux
- [Visual Studio Code](https://code.visualstudio.com/)
- alacritty

## Prerequisites

Ubuntu:

```bash
sudo apt install git python3
```

macOS:

```bash
brew install git python
```

Windows: enable Developer Mode (or run as administrator) so symlinks can be
created, and clone with `git clone -c core.symlinks=true`. Run as
`python deploy.py`.

## Layout

Any top-level directory containing a `.dotfiles-overlay` marker is symlinked
into `~` preserving relative paths (e.g. `dotfiles/.bashrc` → `~/.bashrc`).
The default overlay is `dotfiles/`; drop additional overlay dirs (private,
work, etc.) as siblings at the repo root and re-run `./deploy.py`.

## Deploy dotfiles

```bash
./deploy.py
```

`dotfiles/.agents/skills/` is copied (not symlinked) to `~/.agents/skills/` for
Codex compatibility.

## Update VSCode extensions list

```bash
./update.py
```
