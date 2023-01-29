# dotfiles

### Dependencies

- required
  - git
  - Python 3.5+

### These dotfiles provide config for the following applications:
  - bash
  - i3wm

      Ubuntu:
      ```bash
      $ sudo apt install i3 i3-wm py3status i3lock-fancy xautolock
      ```
  - vim
  - tmux
  - [Visual Studio Code](https://code.visualstudio.com/)
  - alacritty

### Prerequisites

Ubuntu:
```bash
$ sudo apt install git python3
```

macOS:
```bash
$ brew install git python
```

### Deploy dotfiles

```bash
$ python3 deploy.py
```

### Update VSCode extensions list

```bash
$ python3 update.py
```
