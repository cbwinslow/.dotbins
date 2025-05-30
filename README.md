# 🛠️ dotbins Tool Collection

[![dotbins](https://img.shields.io/badge/powered%20by-dotbins-blue.svg?style=flat-square)](https://github.com/basnijholt/dotbins) [![Version](https://img.shields.io/badge/version-2.3.0-green.svg?style=flat-square)](https://github.com/basnijholt/dotbins/releases)

This directory contains command-line tools automatically managed by [dotbins](https://github.com/basnijholt/dotbins).

## 📋 Table of Contents

- [What is dotbins?](#-what-is-dotbins)
- [Installed Tools](#-installed-tools)
- [Tool Statistics](#-tool-statistics)
- [Shell Integration](#-shell-integration)
- [Installing and Updating Tools](#-installing-and-updating-tools)
- [Quick Commands](#-quick-commands)
- [Configuration File](#-configuration-file)
- [Additional Information](#ℹ️-additional-information)

## 📦 What is dotbins?

**dotbins** is a utility for managing CLI tool binaries in your dotfiles repository. It downloads and organizes binaries for popular command-line tools across multiple platforms (macOS, Linux) and architectures (amd64, arm64).

**Key features:**

- ✅ **Cross-platform support** - Manages tools for different OSes and CPU architectures
- ✅ **No admin privileges** - Perfect for systems where you lack sudo access
- ✅ **Version tracking** - Keeps track of installed tools with update timestamps
- ✅ **GitHub integration** - Automatically downloads from GitHub releases
- ✅ **Simple configuration** - YAML-based config with auto-detection capabilities

Learn more: [github.com/basnijholt/dotbins](https://github.com/basnijholt/dotbins)

## 🔍 Installed Tools

| Tool | Repository | Version | Updated | Platforms & Architectures |
| :--- | :--------- | :------ | :------ | :------------------------ |
| [atuin](https://github.com/atuinsh/atuin) | atuinsh/atuin | 18.6.1 | May 26, 2025 | linux (amd64, arm64) • macos (arm64) |
| [bat](https://github.com/sharkdp/bat) | sharkdp/bat | 0.25.0 | Apr 16, 2025 | linux (amd64, arm64) • macos (arm64) |
| [delta](https://github.com/dandavison/delta) | dandavison/delta | 0.18.2 | Apr 01, 2025 | linux (amd64, arm64) • macos (arm64) |
| [direnv](https://github.com/direnv/direnv) | direnv/direnv | 2.36.0 | Apr 16, 2025 | linux (amd64, arm64) • macos (arm64) |
| [duf](https://github.com/muesli/duf) | muesli/duf | 0.8.1 | Apr 16, 2025 | linux (amd64, arm64) • macos (arm64) |
| [dust](https://github.com/bootandy/dust) | bootandy/dust | 1.2.0 | Apr 16, 2025 | linux (amd64, arm64) • macos (arm64) |
| [eza](https://github.com/eza-community/eza) | eza-community/eza | 0.21.4 | May 30, 2025 | linux (amd64, arm64) |
| [fd](https://github.com/sharkdp/fd) | sharkdp/fd | 10.2.0 | Apr 16, 2025 | linux (amd64, arm64) • macos (arm64) |
| [fzf](https://github.com/junegunn/fzf) | junegunn/fzf | 0.62.0 | May 05, 2025 | linux (amd64, arm64) • macos (arm64) |
| [git-lfs](https://github.com/git-lfs/git-lfs) | git-lfs/git-lfs | 3.6.1 | Apr 16, 2025 | linux (amd64, arm64) • macos (arm64) |
| [hyperfine](https://github.com/sharkdp/hyperfine) | sharkdp/hyperfine | 1.19.0 | Apr 16, 2025 | linux (amd64, arm64) • macos (arm64) |
| [keychain](https://github.com/funtoo/keychain) | funtoo/keychain | 2.9.5 | May 26, 2025 | linux (amd64, arm64) • macos (arm64) |
| [lazygit](https://github.com/jesseduffield/lazygit) | jesseduffield/lazygit | 0.51.1 | May 26, 2025 | linux (amd64, arm64) • macos (arm64) |
| [micromamba](https://github.com/mamba-org/micromamba-releases) | mamba-org/micromamba-releases | 2.1.1-0 | May 06, 2025 | linux (amd64, arm64) • macos (arm64) |
| [rg](https://github.com/BurntSushi/ripgrep) | BurntSushi/ripgrep | 14.1.1 | Apr 01, 2025 | linux (amd64, arm64) • macos (arm64) |
| [starship](https://github.com/starship/starship) | starship/starship | 1.23.0 | Apr 28, 2025 | linux (amd64, arm64) • macos (arm64) |
| [uv](https://github.com/astral-sh/uv) | astral-sh/uv | 0.7.9 | May 30, 2025 | linux (amd64, arm64) • macos (arm64) |
| [yazi](https://github.com/sxyazi/yazi) | sxyazi/yazi | 25.5.31 | May 30, 2025 | linux (amd64, arm64) • macos (arm64) |
| [zoxide](https://github.com/ajeetdsouza/zoxide) | ajeetdsouza/zoxide | 0.9.8 | May 27, 2025 | linux (amd64, arm64) • macos (arm64) |

## 📊 Tool Statistics

<div align='center'><h3>📦 56 Tools | 💾 540.84 MB Total Size</h3></div>

| Tool | Total Size | Avg Size per Architecture |
| :--- | :-------- | :------------------------ |
| uv | 108.15 MB | 36.05 MB |
| atuin | 99.28 MB | 33.09 MB |
| lazygit | 60.72 MB | 20.24 MB |
| micromamba | 48.06 MB | 16.02 MB |
| yazi | 41.85 MB | 13.95 MB |
| git-lfs | 34.49 MB | 11.5 MB |
| starship | 28.89 MB | 9.63 MB |
| direnv | 22.61 MB | 7.54 MB |
| delta | 18.64 MB | 6.21 MB |
| bat | 16.22 MB | 5.41 MB |
| rg | 15.46 MB | 5.15 MB |
| fzf | 11.33 MB | 3.78 MB |
| fd | 9.6 MB | 3.2 MB |
| dust | 7.92 MB | 2.64 MB |
| duf | 6.55 MB | 2.18 MB |
| eza | 4.22 MB | 2.11 MB |
| hyperfine | 3.6 MB | 1.2 MB |
| zoxide | 3.12 MB | 1.04 MB |
| keychain | 138.87 KB | 46.29 KB |

## 💻 Shell Integration

Add one of the following snippets to your shell configuration file to use the platform-specific binaries:

For **Bash**:
```bash
source $HOME/.dotbins/shell/bash.sh
```

For **Zsh**:
```bash
source $HOME/.dotbins/shell/zsh.sh
```

For **Fish**:
```fish
source $HOME/.dotbins/shell/fish.fish
```

For **Nushell**:
```nu
source $HOME/.dotbins/shell/nushell.nu
```

## 🔄 Installing and Updating Tools

### Install or update all tools
```bash
dotbins sync
```

### Install or update specific tools only
```bash
dotbins sync tool1 tool2
```

### Install or update for current platform only
```bash
dotbins sync --current
```

### Force reinstall of all tools
```bash
dotbins sync --force
```


## 🚀 Quick Commands

<details>
<summary>All available commands</summary>

```
dotbins list           # List all available tools
dotbins init           # Initialize directory structure
dotbins sync           # Install and update tools to their latest versions
dotbins readme         # Regenerate this README
dotbins status         # Show installed tool versions
dotbins get REPO       # Install tool directly to ~/.local/bin
```

For detailed usage information, run `dotbins --help` or `dotbins <command> --help`
</details>

## 📁 Configuration File

dotbins is configured using a YAML file (`dotbins.yaml`).
This configuration defines which tools to manage, their sources, and platform compatibility.

**Current Configuration:**

```yaml
tools_dir: ~/.dotbins

platforms:
  linux:
    - amd64
    - arm64
  macos:
    - arm64

tools:
  delta: dandavison/delta
  duf: muesli/duf
  dust: bootandy/dust
  fd: sharkdp/fd
  git-lfs: git-lfs/git-lfs
  hyperfine: sharkdp/hyperfine
  rg: BurntSushi/ripgrep
  yazi: sxyazi/yazi

  bat:
    repo: sharkdp/bat
    shell_code:
      bash,zsh: |
        alias bat="bat --paging=never"
        alias cat="bat --plain --paging=never"
  direnv:
    repo: direnv/direnv
    shell_code:
      bash,zsh: |
        eval "$(direnv hook __DOTBINS_SHELL__)"
  eza:
    repo: eza-community/eza
    shell_code:
      bash,zsh: |
        alias l="eza --long --all --git --icons=auto"
  fzf:
    repo: junegunn/fzf
    shell_code:
      zsh: |
        source <(fzf --zsh)
      bash: |
        eval "$(fzf --bash)"
  lazygit:
    repo: jesseduffield/lazygit
    shell_code:
      bash,zsh: |
        alias lg="lazygit"
  micromamba:
    repo: mamba-org/micromamba-releases
    shell_code:
      bash,zsh: |
        alias mm="micromamba"
  starship:
    repo: starship/starship
    shell_code:
      bash,zsh: |
        eval "$(starship init __DOTBINS_SHELL__)"
  zoxide:
    repo: ajeetdsouza/zoxide
    shell_code:
      bash,zsh: |
        eval "$(zoxide init __DOTBINS_SHELL__)"
  atuin:
    repo: atuinsh/atuin
    shell_code:
      bash,zsh: |
        eval "$(atuin init __DOTBINS_SHELL__ --disable-up-arrow)"

  keychain:
    repo: funtoo/keychain
    asset_patterns: keychain

  uv:
    repo: astral-sh/uv
    binary_name: [uv, uvx]
    path_in_archive: [uv-*/uv, uv-*/uvx]
```

## ℹ️ Additional Information

* This README was automatically generated on May 30, 2025
* Current platform: **macos/arm64**
* For more information on dotbins, visit https://github.com/basnijholt/dotbins