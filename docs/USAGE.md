# .dotbins Usage Guide

**Complete walkthrough for using the .dotbins repository**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding the Repository](#understanding-the-repository)
3. [Installation](#installation)
4. [Daily Usage](#daily-usage)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)
8. [Examples](#examples)

---

## Quick Start

### For the Impatient

```bash
# 1. Install the dotbins tool (not in this repo!)
pip install dotbins

# 2. Clone this repository
git clone https://github.com/cbwinslow/.dotbins ~/.dotbins
cd ~/.dotbins

# 3. Add to your shell config (~/.bashrc or ~/.zshrc)
echo 'source ~/.dotbins/shell/bash.sh' >> ~/.bashrc  # or zsh.sh for zsh

# 4. Reload your shell
source ~/.bashrc  # or: exec bash

# 5. Update/install tools
dotbins sync

# 6. Verify it works
fzf --version
bat --version
```

**That's it!** Your CLI tools are now available.

---

## Understanding the Repository

### What Is This Repository?

This repository is a **data storage** for pre-compiled CLI tool binaries. Think of it as a "library" of tools that you can sync across machines.

**Important:** This repository does NOT contain the `dotbins` command-line tool itself. That tool is installed separately via `pip install dotbins`.

### Repository Structure

```
.dotbins/
├── linux/                    # Linux binaries
│   ├── amd64/               # x86_64 architecture
│   │   └── bin/            # Binary files
│   │       ├── fzf
│   │       ├── bat
│   │       └── ...
│   └── arm64/               # ARM64 architecture
│       └── bin/
│           └── ...
├── macos/                    # macOS binaries
│   └── arm64/               # Apple Silicon
│       └── bin/
│           └── ...
├── shell/                    # Shell integration scripts
│   ├── bash.sh             # Bash configuration
│   ├── zsh.sh              # Zsh configuration
│   ├── fish.fish           # Fish shell configuration
│   ├── nushell.nu          # Nushell configuration
│   └── powershell.ps1      # PowerShell configuration
├── docs/                     # Documentation
│   ├── USAGE.md            # This file
│   ├── ASSESSMENT.md       # Repository assessment
│   └── ARCHITECTURE.md     # Technical details
├── dotbins.yaml             # Configuration file
├── manifest.json            # Tool versions and metadata
├── configure-lfs-skip-smudge.py  # Git LFS helper
├── .gitattributes          # Git LFS configuration
└── README.md               # Auto-generated README
```

### What Gets Stored?

**Currently (with Git LFS):**
- ✅ Full binaries for all platforms (~580MB)
- ✅ Version information
- ✅ SHA256 checksums
- ✅ Download URLs

**Planned (URL-based approach):**
- ✅ Download URLs only
- ✅ Version information
- ✅ SHA256 checksums
- ❌ No actual binaries in Git

---

## Installation

### Prerequisites

1. **Git** - Version control
2. **Git LFS** - For downloading binaries (current approach)
3. **Python 3.8+** - For the dotbins tool
4. **pip** - Python package manager

### Step 1: Install Git LFS

<details>
<summary>Ubuntu/Debian</summary>

```bash
sudo apt-get install git-lfs
git lfs install
```
</details>

<details>
<summary>macOS</summary>

```bash
brew install git-lfs
git lfs install
```
</details>

<details>
<summary>Fedora/RHEL</summary>

```bash
sudo dnf install git-lfs
git lfs install
```
</details>

### Step 2: Install dotbins Tool

```bash
# Using pip
pip install dotbins

# Or using pipx (recommended for isolated installation)
pipx install dotbins

# Verify installation
dotbins --version
```

### Step 3: Clone This Repository

```bash
# Clone to default location
git clone https://github.com/cbwinslow/.dotbins ~/.dotbins

# Or clone to custom location
git clone https://github.com/cbwinslow/.dotbins /path/to/dotbins
```

### Step 4: Configure Shell Integration

Choose your shell and add the appropriate line:

**Bash** (`~/.bashrc`):
```bash
source ~/.dotbins/shell/bash.sh
```

**Zsh** (`~/.zshrc`):
```bash
source ~/.dotbins/shell/zsh.sh
```

**Fish** (`~/.config/fish/config.fish`):
```fish
source ~/.dotbins/shell/fish.fish
```

**Nushell** (`~/.config/nushell/config.nu`):
```nu
source ~/.dotbins/shell/nushell.nu
```

### Step 5: Reload Shell

```bash
# Bash/Zsh
source ~/.bashrc  # or ~/.zshrc

# Or restart your shell
exec bash  # or: exec zsh

# Fish
source ~/.config/fish/config.fish

# Nushell
source ~/.config/nushell/config.nu
```

### Step 6: Sync Tools

```bash
# Download/update all tools
dotbins sync

# Or sync only for your current platform
dotbins sync --current
```

### Verification

```bash
# Check that tools are in PATH
which fzf
which bat
which rg

# Test a tool
fzf --version
bat --version

# See what's installed
dotbins status
```

---

## Daily Usage

### Common Commands

#### Update All Tools
```bash
# Sync all tools to latest versions
dotbins sync

# Sync only current platform
dotbins sync --current

# Force reinstall even if up-to-date
dotbins sync --force
```

#### Update Specific Tools
```bash
# Update only fzf and bat
dotbins sync fzf bat

# Update with force
dotbins sync --force fzf
```

#### Check Status
```bash
# Show installed versions
dotbins status

# List available tools
dotbins list
```

#### Get Tool Directly
```bash
# Install tool to ~/.local/bin
dotbins get junegunn/fzf

# This bypasses the repository and installs directly
```

#### Regenerate README
```bash
# Update the README with current stats
dotbins readme
```

---

## Configuration

### The dotbins.yaml File

This file controls what tools are managed and how they're configured.

```yaml
# Where tools are stored
tools_dir: ~/.dotbins

# Enable Git LFS helper scripts
generate_lfs_scripts: true

# Supported platforms and architectures
platforms:
  linux:
    - amd64
    - arm64
  macos:
    - arm64

# Tool definitions
tools:
  # Simple form: tool_name: github_repo
  fzf: junegunn/fzf
  bat: sharkdp/bat
  rg: BurntSushi/ripgrep
  
  # Extended form with shell integration
  starship:
    repo: starship/starship
    shell_code:
      bash,zsh: |
        eval "$(starship init __DOTBINS_SHELL__)"
  
  # Multiple binaries from one repo
  uv:
    repo: astral-sh/uv
    binary_name: [uv, uvx]
    path_in_archive: [uv-*/uv, uv-*/uvx]
```

### Adding a New Tool

1. **Find the GitHub repository**
   ```bash
   # Example: adding ripgrep
   # Repository: BurntSushi/ripgrep
   ```

2. **Add to dotbins.yaml**
   ```yaml
   tools:
     rg: BurntSushi/ripgrep
   ```

3. **Sync to download**
   ```bash
   dotbins sync rg
   ```

### Removing a Tool

1. **Remove from dotbins.yaml**
   ```yaml
   # Delete or comment out the line
   # rg: BurntSushi/ripgrep
   ```

2. **Remove binary files**
   ```bash
   rm ~/.dotbins/linux/amd64/bin/rg
   rm ~/.dotbins/linux/arm64/bin/rg
   rm ~/.dotbins/macos/arm64/bin/rg
   ```

3. **Update manifest**
   ```bash
   dotbins readme  # Regenerates README and manifest
   ```

### Shell Integration

Each tool can have shell-specific configuration:

```yaml
tools:
  bat:
    repo: sharkdp/bat
    shell_code:
      bash,zsh: |
        alias bat="bat --paging=never"
        alias cat="bat --plain --paging=never"
      fish: |
        alias bat="bat --paging=never"
        alias cat="bat --plain --paging=never"
```

This code is executed when you source the shell script.

---

## Troubleshooting

### Tools Not in PATH

**Problem:** Running `fzf` says "command not found"

**Solutions:**
1. Verify shell script is sourced:
   ```bash
   echo $PATH | grep dotbins
   # Should show: /home/user/.dotbins/linux/amd64/bin
   ```

2. Re-source your shell config:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

3. Check if binary exists:
   ```bash
   ls -la ~/.dotbins/linux/amd64/bin/fzf
   ```

4. Verify platform detection:
   ```bash
   uname -s  # Should show: Linux or Darwin
   uname -m  # Should show: x86_64, aarch64, or arm64
   ```

### Sync Fails

**Problem:** `dotbins sync` fails with errors

**Solutions:**

1. **Git LFS not installed:**
   ```bash
   git lfs install
   cd ~/.dotbins
   git lfs pull
   ```

2. **Network issues:**
   ```bash
   # Check connectivity
   ping github.com
   
   # Try with verbose output
   dotbins sync --verbose
   ```

3. **Outdated dotbins version:**
   ```bash
   pip install --upgrade dotbins
   ```

4. **Corrupted manifest:**
   ```bash
   cd ~/.dotbins
   git reset --hard origin/main
   dotbins sync --force
   ```

### Binary Doesn't Work

**Problem:** Tool crashes or doesn't execute

**Solutions:**

1. **Check it's executable:**
   ```bash
   chmod +x ~/.dotbins/linux/amd64/bin/fzf
   ```

2. **Verify it's not a pointer file (LFS issue):**
   ```bash
   file ~/.dotbins/linux/amd64/bin/fzf
   # Should show: ELF executable
   # NOT: ASCII text (pointer file)
   ```
   
   If it's a pointer file:
   ```bash
   cd ~/.dotbins
   git lfs pull
   ```

3. **Check architecture:**
   ```bash
   file ~/.dotbins/linux/amd64/bin/fzf
   # Verify it matches your architecture
   ```

4. **Try redownloading:**
   ```bash
   dotbins sync --force fzf
   ```

### Wrong Platform Binaries

**Problem:** Trying to use ARM64 binaries on AMD64 or vice versa

**Solution:** Use the LFS configuration script:
```bash
cd ~/.dotbins
python3 configure-lfs-skip-smudge.py
```

This configures Git LFS to only download binaries for your platform.

### Updates Not Appearing

**Problem:** `dotbins sync` runs but tools aren't updated

**Solutions:**

1. **Check manifest.json:**
   ```bash
   cat ~/.dotbins/manifest.json | grep fzf -A 5
   ```

2. **Force update:**
   ```bash
   dotbins sync --force
   ```

3. **Check remote:**
   ```bash
   cd ~/.dotbins
   git fetch origin
   git status
   ```

4. **Reset and sync:**
   ```bash
   cd ~/.dotbins
   git reset --hard origin/main
   dotbins sync --force
   ```

---

## Advanced Usage

### Using on Multiple Machines

#### Machine 1 (Initial Setup)
```bash
# Set up as normal
git clone https://github.com/cbwinslow/.dotbins ~/.dotbins
cd ~/.dotbins
dotbins sync
```

#### Machine 2 (Sync From Remote)
```bash
# Clone the same repository
git clone https://github.com/cbwinslow/.dotbins ~/.dotbins
cd ~/.dotbins

# Configure for your platform only
python3 configure-lfs-skip-smudge.py

# Sync tools
dotbins sync --current
```

### Platform-Specific Downloads

To save bandwidth and storage, only download binaries for your platform:

```bash
cd ~/.dotbins
python3 configure-lfs-skip-smudge.py
```

This script:
1. Detects your platform (linux/amd64, linux/arm64, macos/arm64)
2. Configures Git LFS to only fetch your platform
3. Optionally cleans up other platforms
4. Saves significant disk space and bandwidth

### Custom Installation Location

```bash
# Clone to custom location
git clone https://github.com/cbwinslow/.dotbins /opt/mytools

# Update dotbins.yaml
cd /opt/mytools
# Edit dotbins.yaml and change:
# tools_dir: /opt/mytools

# Add to shell config
echo 'source /opt/mytools/shell/bash.sh' >> ~/.bashrc
```

### Offline Usage

1. **Sync while online:**
   ```bash
   dotbins sync
   ```

2. **Copy entire directory to offline machine:**
   ```bash
   # On online machine
   tar czf dotbins.tar.gz ~/.dotbins
   
   # Copy to offline machine and extract
   tar xzf dotbins.tar.gz -C ~/
   ```

3. **Configure shell on offline machine:**
   ```bash
   source ~/.dotbins/shell/bash.sh
   ```

### Pinning Versions

To prevent automatic updates:

1. **Don't run `dotbins sync`** - tools stay at current versions

2. **Use Git to rollback:**
   ```bash
   cd ~/.dotbins
   git log --oneline  # Find commit hash
   git reset --hard <commit-hash>
   git lfs pull
   ```

3. **Backup before updating:**
   ```bash
   cd ~/.dotbins
   git branch backup-$(date +%Y%m%d)
   dotbins sync
   ```

---

## Examples

### Example 1: Fresh Setup on New Linux Machine

```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install -y git git-lfs python3-pip

# Install Git LFS
git lfs install

# Install dotbins tool
pip3 install --user dotbins

# Add pip user bin to PATH if needed
export PATH="$HOME/.local/bin:$PATH"

# Clone repository
git clone https://github.com/cbwinslow/.dotbins ~/.dotbins

# Configure for current platform only (saves bandwidth)
cd ~/.dotbins
python3 configure-lfs-skip-smudge.py
# Answer 'y' to cleanup prompt

# Add to bashrc
echo 'source ~/.dotbins/shell/bash.sh' >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Sync tools (only downloads for your platform)
dotbins sync --current

# Verify
fzf --version
bat --help
rg --version
```

### Example 2: Adding a New Tool (eza)

```bash
# 1. Find the GitHub repo: eza-community/eza

# 2. Edit dotbins.yaml
cd ~/.dotbins
nano dotbins.yaml

# Add:
# tools:
#   eza:
#     repo: eza-community/eza
#     shell_code:
#       bash,zsh: |
#         alias l="eza -lah --git --icons"

# 3. Sync
dotbins sync eza

# 4. Commit changes
git add dotbins.yaml manifest.json linux/ macos/
git commit -m "Add eza file lister"
git push

# 5. Test
eza --version
l  # Using the alias
```

### Example 3: Updating a Single Tool

```bash
# Update only fzf
dotbins sync fzf

# Verify new version
fzf --version

# Commit the update
cd ~/.dotbins
git add manifest.json linux/ macos/
git commit -m "Update fzf to latest version"
git push
```

### Example 4: Syncing Between Two Machines

**Machine A (Work Computer - Linux AMD64):**
```bash
# Add a tool
dotbins sync lazygit
cd ~/.dotbins
git add -A
git commit -m "Add lazygit"
git push
```

**Machine B (Home Computer - Linux ARM64):**
```bash
# Pull changes
cd ~/.dotbins
git pull

# Sync (automatically gets ARM64 version)
dotbins sync --current

# Now lazygit is available
lg  # Alias for lazygit
```

### Example 5: Troubleshooting Missing Binary

```bash
# Tool exists but doesn't run
which fzf
# /home/user/.dotbins/linux/amd64/bin/fzf

# Check file type
file ~/.dotbins/linux/amd64/bin/fzf
# fzf: ASCII text  ← Problem! Should be ELF binary

# This means it's an LFS pointer file, not the actual binary
cat ~/.dotbins/linux/amd64/bin/fzf
# version https://git-lfs.github.com/spec/v1
# oid sha256:abc123...

# Fix by pulling LFS files
cd ~/.dotbins
git lfs pull

# Verify it's now a binary
file ~/.dotbins/linux/amd64/bin/fzf
# fzf: ELF 64-bit LSB executable  ← Fixed!

# Test
fzf --version
```

### Example 6: Custom Tool with Multiple Binaries

```bash
# Example: uv package comes with uv and uvx

# Edit dotbins.yaml
cd ~/.dotbins
nano dotbins.yaml

# Add:
# tools:
#   uv:
#     repo: astral-sh/uv
#     binary_name: [uv, uvx]
#     path_in_archive: [uv-*/uv, uv-*/uvx]

# Sync
dotbins sync uv

# Both binaries are now available
uv --version
uvx --version
```

---

## What Each Tool Does

Here's a quick reference of the tools in this repository:

| Tool | Purpose | Usage Example |
|------|---------|---------------|
| **atuin** | Shell history search and sync | `atuin search git` |
| **bat** | Cat with syntax highlighting | `bat file.py` |
| **delta** | Git diff viewer | `git diff` (auto-used) |
| **direnv** | Directory-specific env vars | `echo 'export FOO=bar' > .envrc` |
| **duf** | Disk usage (df replacement) | `duf` |
| **dust** | Disk usage tree (du replacement) | `dust` |
| **eza** | Modern ls replacement | `eza -lah` |
| **fd** | Fast find alternative | `fd pattern` |
| **fzf** | Fuzzy finder | `fzf`, `Ctrl+R` (history) |
| **git-lfs** | Git Large File Storage | `git lfs track "*.bin"` |
| **hyperfine** | Command benchmarking | `hyperfine 'command1' 'command2'` |
| **lazygit** | Terminal UI for git | `lazygit` |
| **micromamba** | Conda package manager | `micromamba install numpy` |
| **rg** (ripgrep) | Fast grep alternative | `rg pattern` |
| **starship** | Cross-shell prompt | (auto-loaded) |
| **uv** | Fast Python package manager | `uv pip install requests` |
| **yazi** | Terminal file manager | `yazi` |
| **zoxide** | Smart cd replacement | `z project` (jumps to dir) |

---

## Next Steps

After getting comfortable with basic usage:

1. **Read [ARCHITECTURE.md](ARCHITECTURE.md)** - Understand how it works internally
2. **Read [ASSESSMENT.md](ASSESSMENT.md)** - Understand limitations and future plans
3. **Customize dotbins.yaml** - Add tools you need
4. **Set up on multiple machines** - Sync your toolset everywhere
5. **Contribute improvements** - Help make this better!

---

## Getting Help

### Resources

- **This Documentation:** `/docs/` directory
- **Upstream Project:** https://github.com/basnijholt/dotbins
- **Issues:** https://github.com/cbwinslow/.dotbins/issues

### Common Questions

**Q: Do I need Python installed to use the tools?**  
A: No, only to run `dotbins sync`. The tools themselves are standalone binaries.

**Q: Can I use this without the dotbins Python tool?**  
A: Yes, but you'll need to manually download and place binaries. The shell scripts will still work.

**Q: Why are binaries so large?**  
A: They're statically linked for portability. Git LFS keeps your local clone small.

**Q: Can I add tools not on GitHub?**  
A: Not with the standard dotbins tool, but you can manually add binaries.

**Q: Is this secure?**  
A: Binaries come from official GitHub releases. See [ASSESSMENT.md](ASSESSMENT.md) for security discussion.

---

**Last Updated:** November 4, 2025
