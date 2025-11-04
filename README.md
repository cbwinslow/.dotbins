# 🛠️ dotbins Tool Collection

[![dotbins](https://img.shields.io/badge/powered%20by-dotbins-blue.svg?style=flat-square)](https://github.com/basnijholt/dotbins) [![Version](https://img.shields.io/badge/version-2.3.0-green.svg?style=flat-square)](https://github.com/basnijholt/dotbins/releases)

This directory contains command-line tools automatically managed by [dotbins](https://github.com/basnijholt/dotbins).

## 📚 **NEW:** Enhanced Documentation & Tools

This repository now includes comprehensive documentation and AI-powered helper tools:

### Documentation
- **[📖 Usage Guide](docs/USAGE.md)** - Complete walkthrough with examples, troubleshooting, and how-to guides
- **[🏗️ Architecture Guide](docs/ARCHITECTURE.md)** - Technical deep-dive into how dotbins works
- **[📊 Assessment & Analysis](docs/ASSESSMENT.md)** - Repository evaluation, pros/cons, and recommendations

### Helper Scripts
- **[🔍 dotbins-verify](scripts/dotbins-verify)** - Health check and installation verification
- **[📝 dotbins-info](scripts/dotbins-info)** - Tool information, search, and discovery
- **[⚙️ dotbins-setup](scripts/dotbins-setup)** - Automated setup for new machines
- **[🤖 ai-metadata.py](scripts/ai-metadata.py)** - AI-powered metadata generator
- **[📋 Scripts README](scripts/README.md)** - Complete scripts documentation

### AI Integration
- **[🚀 OpenRouter SDK](lib/openrouter/README.md)** - Standalone Python SDK for AI-powered features
- Free models support (Gemini, LLaMA, Qwen)
- Web search integration for current information
- Can be extracted as separate repository

### Quick Start

**New machine setup:**
```bash
curl -fsSL https://raw.githubusercontent.com/cbwinslow/.dotbins/main/scripts/dotbins-setup | bash
```

**Verify installation:**
```bash
~/.dotbins/scripts/dotbins-verify
```

**Explore tools:**
```bash
~/.dotbins/scripts/dotbins-info list
```

---

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
| [atuin](https://github.com/atuinsh/atuin) | atuinsh/atuin | 18.10.0 | Oct 23, 2025 | linux (amd64, arm64) • macos (arm64) |
| [bat](https://github.com/sharkdp/bat) | sharkdp/bat | 0.26.0 | Oct 23, 2025 | linux (amd64, arm64) • macos (arm64) |
| [delta](https://github.com/dandavison/delta) | dandavison/delta | 0.18.2 | Aug 21, 2025 | linux (amd64, arm64) • macos (arm64) |
| [direnv](https://github.com/direnv/direnv) | direnv/direnv | 2.37.1 | Oct 08, 2025 | linux (amd64, arm64) • macos (arm64) |
| [duf](https://github.com/muesli/duf) | muesli/duf | 0.9.1 | Oct 08, 2025 | linux (amd64, arm64) • macos (arm64) |
| [dust](https://github.com/bootandy/dust) | bootandy/dust | 1.2.3 | Oct 08, 2025 | linux (amd64, arm64) • macos (arm64) |
| [eza](https://github.com/eza-community/eza) | eza-community/eza | 0.23.4 | Oct 08, 2025 | linux (amd64, arm64) |
| [fd](https://github.com/sharkdp/fd) | sharkdp/fd | 10.3.0 | Oct 08, 2025 | linux (amd64, arm64) • macos (arm64) |
| [fzf](https://github.com/junegunn/fzf) | junegunn/fzf | 0.66.1 | Oct 28, 2025 | linux (amd64, arm64) • macos (arm64) |
| [git-lfs](https://github.com/git-lfs/git-lfs) | git-lfs/git-lfs | 3.7.1 | Oct 23, 2025 | linux (amd64, arm64) • macos (arm64) |
| [hyperfine](https://github.com/sharkdp/hyperfine) | sharkdp/hyperfine | 1.19.0 | Oct 08, 2025 | linux (amd64, arm64) • macos (arm64) |
| [lazygit](https://github.com/jesseduffield/lazygit) | jesseduffield/lazygit | 0.55.1 | Oct 08, 2025 | linux (amd64, arm64) • macos (arm64) |
| [micromamba](https://github.com/mamba-org/micromamba-releases) | mamba-org/micromamba-releases | 2.3.3-0 | Oct 23, 2025 | linux (amd64, arm64) • macos (arm64) |
| [rg](https://github.com/BurntSushi/ripgrep) | BurntSushi/ripgrep | 15.1.0 | Oct 23, 2025 | linux (amd64, arm64) • macos (arm64) |
| [starship](https://github.com/starship/starship) | starship/starship | 1.24.0 | Oct 28, 2025 | linux (amd64, arm64) • macos (arm64) |
| [uv](https://github.com/astral-sh/uv) | astral-sh/uv | 0.9.5 | Oct 23, 2025 | linux (amd64, arm64) • macos (arm64) |
| [yazi](https://github.com/sxyazi/yazi) | sxyazi/yazi | 25.5.31 | Oct 08, 2025 | linux (amd64, arm64) • macos (arm64) |
| [zoxide](https://github.com/ajeetdsouza/zoxide) | ajeetdsouza/zoxide | 0.9.8 | Oct 08, 2025 | linux (amd64, arm64) • macos (arm64) |

## 📊 Tool Statistics

<div align='center'><h3>📦 53 Tools | 💾 204.1 MB Total Size</h3></div>

| Tool | Total Size | Avg Size per Architecture |
| :--- | :-------- | :------------------------ |
| uv | 40.09 MB | 13.36 MB |
| atuin | 30.52 MB | 10.17 MB |
| starship | 29.87 MB | 9.96 MB |
| lazygit | 20.44 MB | 6.81 MB |
| micromamba | 13.19 MB | 4.4 MB |
| fzf | 12.59 MB | 4.2 MB |
| yazi | 12.4 MB | 4.13 MB |
| git-lfs | 11.93 MB | 3.98 MB |
| direnv | 7.53 MB | 2.51 MB |
| delta | 5.76 MB | 1.92 MB |
| bat | 5.57 MB | 1.86 MB |
| rg | 3.86 MB | 1.29 MB |
| duf | 2.94 MB | 1002.08 KB |
| fd | 2.83 MB | 967.4 KB |
| dust | 2.55 MB | 870.86 KB |
| hyperfine | 1.1 MB | 374.08 KB |
| zoxide | 945.23 KB | 315.08 KB |
| eza | 264.0 B | 132.0 B |

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

# Enable Git LFS helper script generation
generate_lfs_scripts: true

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
        alias l="eza -lah --git --icons"
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

  uv:
    repo: astral-sh/uv
    binary_name: [uv, uvx]
    path_in_archive: [uv-*/uv, uv-*/uvx]
```

## ℹ️ Additional Information

* This README was automatically generated on Oct 28, 2025
* Current platform: **macos/arm64**
* For more information on dotbins, visit https://github.com/basnijholt/dotbins