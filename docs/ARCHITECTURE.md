# .dotbins Architecture Documentation

**Technical deep-dive into how .dotbins works**

---

## Table of Contents

1. [Overview](#overview)
2. [Component Architecture](#component-architecture)
3. [File Structure](#file-structure)
4. [Shell Integration](#shell-integration)
5. [Git LFS Integration](#git-lfs-integration)
6. [Platform Detection](#platform-detection)
7. [Tool Management](#tool-management)
8. [Data Flow](#data-flow)
9. [Storage Architecture](#storage-architecture)
10. [Future Architecture](#future-architecture)

---

## Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User's Shell                        │
│  (bash/zsh/fish/nushell with dotbins integration)       │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ source ~/.dotbins/shell/bash.sh
                  ↓
┌─────────────────────────────────────────────────────────┐
│               Shell Integration Scripts                  │
│  • Detect platform (OS + architecture)                  │
│  • Add binaries to PATH                                 │
│  • Load tool-specific configurations                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ $PATH includes ~/.dotbins/{os}/{arch}/bin
                  ↓
┌─────────────────────────────────────────────────────────┐
│                  Binary Directory                        │
│  linux/amd64/bin/  linux/arm64/bin/  macos/arm64/bin/  │
│  ├── fzf          ├── fzf            ├── fzf           │
│  ├── bat          ├── bat            ├── bat           │
│  └── ...          └── ...            └── ...           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Managed by dotbins tool
                  ↓
┌─────────────────────────────────────────────────────────┐
│              dotbins CLI Tool (Python)                   │
│  • Read dotbins.yaml configuration                      │
│  • Fetch latest versions from GitHub API               │
│  • Download binaries from GitHub Releases              │
│  • Update manifest.json with metadata                  │
│  • Generate README documentation                       │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Stores in Git repository
                  ↓
┌─────────────────────────────────────────────────────────┐
│              Git Repository + LFS                        │
│  • Configuration (dotbins.yaml)                         │
│  • Binary files (via Git LFS)                          │
│  • Version metadata (manifest.json)                    │
│  • Shell scripts                                        │
└─────────────────────────────────────────────────────────┘
```

### Component Relationships

```
┌──────────────┐     reads      ┌──────────────┐
│dotbins.yaml  │────────────────▶│ dotbins CLI  │
└──────────────┘                 └──────┬───────┘
                                        │
                                        │ writes
                                        ↓
┌──────────────┐     updates    ┌──────────────┐
│manifest.json │◀────────────────│ GitHub API   │
└──────────────┘                 └──────────────┘
       │                                │
       │ references                     │ downloads from
       ↓                                ↓
┌──────────────┐                 ┌──────────────┐
│   Binaries   │◀────────────────│GitHub Release│
└──────────────┘    fetches      └──────────────┘
       │
       │ stored in
       ↓
┌──────────────┐
│   Git LFS    │
└──────────────┘
```

---

## Component Architecture

### 1. Shell Integration Scripts

**Location:** `shell/bash.sh`, `shell/zsh.sh`, `shell/fish.fish`, etc.

**Purpose:** 
- Add platform-specific binaries to PATH
- Load tool-specific configurations
- Set up aliases and shell integrations

**Key Functions:**
```bash
# Platform detection
_os=$(uname -s | tr '[:upper:]' '[:lower:]')
[[ "$_os" == "darwin" ]] && _os="macos"

_arch=$(uname -m)
[[ "$_arch" == "x86_64" ]] && _arch="amd64"
[[ "$_arch" == "aarch64" || "$_arch" == "arm64" ]] && _arch="arm64"

# PATH modification
export PATH="$HOME/.dotbins/$_os/$_arch/bin:$PATH"

# Tool-specific configurations
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
fi
```

**Execution Flow:**
1. User sources script in their shell config
2. Script runs on every shell startup
3. Detects current platform
4. Modifies PATH to include appropriate binary directory
5. Executes tool-specific setup commands

### 2. Configuration System (dotbins.yaml)

**Location:** `dotbins.yaml`

**Structure:**
```yaml
# Global settings
tools_dir: ~/.dotbins
generate_lfs_scripts: true

# Platform definitions
platforms:
  linux:
    - amd64
    - arm64
  macos:
    - arm64

# Tool definitions
tools:
  # Simple form
  tool_name: github_user/repo
  
  # Extended form
  tool_name:
    repo: github_user/repo
    binary_name: [name1, name2]  # Multiple binaries
    path_in_archive: [path1, path2]  # Paths in archive
    shell_code:
      bash,zsh: |
        # Shell-specific code
```

**Processing:**
1. Parsed by dotbins CLI tool
2. Used to determine which tools to download
3. Shell code injected into integration scripts
4. Defines supported platforms/architectures

### 3. Version Manifest (manifest.json)

**Location:** `manifest.json`

**Structure:**
```json
{
  "version": 2,
  "tool_name/platform/arch": {
    "tag": "v1.0.0",
    "updated_at": "2025-11-04T12:00:00",
    "sha256": "abc123...",
    "url": "https://github.com/..."
  }
}
```

**Purpose:**
- Track installed versions
- Store download URLs
- Verify binary integrity (SHA256)
- Record update timestamps

**Usage:**
- Read by dotbins to check current versions
- Updated on every sync operation
- Used to generate README documentation

### 4. Git LFS Configuration

**Location:** `.gitattributes`

**Content:**
```gitattributes
# Track all files in platform directories as LFS
linux/*/bin/* filter=lfs diff=lfs merge=lfs -text
macos/*/bin/* filter=lfs diff=lfs merge=lfs -text
windows/*/bin/* filter=lfs diff=lfs merge=lfs -text

# Track common binary extensions
*.exe filter=lfs diff=lfs merge=lfs -text
*.dll filter=lfs diff=lfs merge=lfs -text
*.so filter=lfs diff=lfs merge=lfs -text
```

**How It Works:**
1. Git recognizes files matching these patterns
2. Instead of storing content, stores a pointer
3. Actual content stored in LFS storage
4. `git lfs pull` downloads actual content
5. Keeps repository clone small

### 5. LFS Helper Script

**Location:** `configure-lfs-skip-smudge.py`

**Purpose:** 
- Configure Git LFS to download only current platform
- Save bandwidth and disk space
- Clean up unnecessary platform binaries

**Algorithm:**
```python
def main():
    # 1. Detect current platform
    target = detect_platform()  # e.g., "linux/amd64"
    
    # 2. Configure LFS fetchinclude for current platform
    git config lfs.fetchinclude "{target}/**"
    
    # 3. Configure LFS fetchexclude for other platforms
    for other_platform in OTHER_PLATFORMS:
        git config --add lfs.fetchexclude "{other_platform}/**"
    
    # 4. Optionally clean up already-downloaded binaries
    if prompt_cleanup():
        remove_other_platforms()
        git lfs prune
```

**Benefits:**
- Reduces disk usage by ~66% (only one platform vs. three)
- Reduces bandwidth on updates
- Faster clones and pulls

---

## File Structure

### Directory Layout

```
.dotbins/
├── .git/                         # Git repository data
│   └── lfs/                     # Git LFS cache
├── .gitattributes               # LFS tracking configuration
├── README.md                    # Auto-generated documentation
├── dotbins.yaml                 # Main configuration file
├── manifest.json                # Version and metadata tracking
├── configure-lfs-skip-smudge.py # LFS platform helper script
│
├── docs/                        # Documentation
│   ├── USAGE.md                # User guide
│   ├── ARCHITECTURE.md         # This file
│   └── ASSESSMENT.md           # Repository assessment
│
├── shell/                       # Shell integration
│   ├── bash.sh                 # Bash configuration
│   ├── zsh.sh                  # Zsh configuration
│   ├── fish.fish               # Fish shell configuration
│   ├── nushell.nu              # Nushell configuration
│   └── powershell.ps1          # PowerShell configuration
│
├── linux/                       # Linux binaries
│   ├── amd64/                  # x86_64 architecture
│   │   └── bin/                # Binary files
│   │       ├── atuin
│   │       ├── bat
│   │       ├── delta
│   │       ├── direnv
│   │       ├── duf
│   │       ├── dust
│   │       ├── eza
│   │       ├── fd
│   │       ├── fzf
│   │       ├── git-lfs
│   │       ├── hyperfine
│   │       ├── lazygit
│   │       ├── micromamba
│   │       ├── rg
│   │       ├── starship
│   │       ├── uv
│   │       ├── uvx
│   │       ├── yazi
│   │       └── zoxide
│   └── arm64/                  # ARM64 architecture
│       └── bin/                # Binary files (same list)
│
└── macos/                       # macOS binaries
    └── arm64/                  # Apple Silicon
        └── bin/                # Binary files
```

### File Purposes

| File/Directory | Purpose | Generated | Version Controlled |
|----------------|---------|-----------|-------------------|
| `dotbins.yaml` | Configuration | Manual | Yes |
| `manifest.json` | Version tracking | Auto | Yes |
| `README.md` | Documentation | Auto | Yes |
| `.gitattributes` | LFS config | Auto | Yes |
| `shell/*.sh` | Integration | Auto | Yes |
| `*/bin/*` | Binaries | Downloaded | Yes (via LFS) |
| `.git/lfs/` | LFS cache | Git LFS | No |
| `docs/` | Documentation | Manual | Yes |

---

## Shell Integration

### How Shell Scripts Work

#### 1. Platform Detection

**Code (bash.sh):**
```bash
_os=$(uname -s | tr '[:upper:]' '[:lower:]')
[[ "$_os" == "darwin" ]] && _os="macos"

_arch=$(uname -m)
[[ "$_arch" == "x86_64" ]] && _arch="amd64"
[[ "$_arch" == "aarch64" || "$_arch" == "arm64" ]] && _arch="arm64"
```

**Platform Mapping:**
| `uname -s` | Normalized | Directory |
|------------|-----------|-----------|
| Linux | linux | linux/ |
| Darwin | macos | macos/ |

| `uname -m` | Normalized | Directory |
|------------|-----------|-----------|
| x86_64 | amd64 | */amd64/ |
| aarch64 | arm64 | */arm64/ |
| arm64 | arm64 | */arm64/ |

#### 2. PATH Modification

```bash
export PATH="$HOME/.dotbins/$_os/$_arch/bin:$PATH"
```

**Result:**
- Prepends dotbins binaries to PATH
- Takes precedence over system binaries
- Example: `~/.dotbins/linux/amd64/bin:/usr/local/bin:/usr/bin`

#### 3. Tool Configuration Loading

```bash
# Configuration for starship
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
fi
```

**Pattern:**
1. Check if tool is available (`command -v`)
2. If yes, run tool-specific setup
3. Setup code comes from `dotbins.yaml`

#### 4. Shell-Specific Variations

**Bash vs Zsh:**
- Nearly identical
- Difference: `fzf --bash` vs `source <(fzf --zsh)`

**Fish:**
- Different syntax but same logic
- Uses `set -x` for exports
- Different conditional syntax

**Nushell:**
- Completely different syntax
- Uses Nushell's configuration system
- Same functionality

---

## Git LFS Integration

### How Git LFS Works

#### Traditional Git

```
┌──────────────┐
│  Git Repo    │
│              │
│  ┌────────┐  │
│  │ Binary │  │  ← Entire file stored in Git
│  │  10MB  │  │
│  └────────┘  │
└──────────────┘
```

**Problem:** Repository grows with every binary version

#### Git LFS

```
┌──────────────┐                    ┌──────────────┐
│  Git Repo    │                    │  LFS Server  │
│              │                    │              │
│  ┌────────┐  │   Points to      │  ┌────────┐  │
│  │Pointer │──┼───────────────────▶│ Binary │  │
│  │ 100B   │  │                    │  10MB  │  │
│  └────────┘  │                    │  └────────┘  │
└──────────────┘                    └──────────────┘
```

**Benefits:**
- Git repo stays small
- Binaries stored separately
- Download on-demand

### LFS Pointer File Format

```
version https://git-lfs.github.com/spec/v1
oid sha256:abc123def456...
size 10485760
```

**What Happens:**
1. `git add binary` → Git LFS intercepts
2. Uploads binary to LFS server
3. Stores pointer in Git
4. `git clone` → Downloads only pointers
5. `git lfs pull` → Downloads actual binaries

### Platform-Specific LFS

**Problem:** Don't want to download all platforms

**Solution:** LFS fetch filters

```bash
git config lfs.fetchinclude "linux/amd64/**"
git config lfs.fetchexclude "linux/arm64/**"
git config lfs.fetchexclude "macos/arm64/**"
```

**Result:**
- Only downloads linux/amd64 binaries
- Saves ~66% of download size
- Other platforms stay as pointers

---

## Platform Detection

### Detection Algorithm

```
Start
  ↓
┌─────────────────┐
│  uname -s       │ → Linux, Darwin, etc.
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Normalize OS   │ → linux, macos, windows
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  uname -m       │ → x86_64, aarch64, arm64
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Normalize Arch │ → amd64, arm64
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Combine to Path │ → linux/amd64
└────────┬────────┘
         │
         ↓
      Result
```

### Supported Platforms

| Platform | Architecture | Directory | Typical Systems |
|----------|-------------|-----------|-----------------|
| linux | amd64 | linux/amd64 | Most Linux servers, desktops |
| linux | arm64 | linux/arm64 | Raspberry Pi, ARM servers |
| macos | arm64 | macos/arm64 | M1/M2/M3 Macs |

**Not Currently Supported:**
- Windows (any architecture)
- macOS Intel (macos/amd64)
- Other architectures (RISC-V, MIPS, etc.)

---

## Tool Management

### Sync Operation Flow

```
User runs: dotbins sync
         ↓
┌──────────────────────────────────────┐
│ 1. Read dotbins.yaml                │
│    - Get tool list                  │
│    - Get platform list              │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 2. For each tool:                   │
│    - Check GitHub API for latest    │
│    - Compare with manifest.json     │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 3. For each platform:               │
│    - Find matching release asset    │
│    - Download archive               │
│    - Extract binary                 │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 4. Verify:                          │
│    - Check SHA256                   │
│    - Make executable                │
│    - Store in {os}/{arch}/bin/     │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 5. Update manifest.json             │
│    - Version                        │
│    - URL                            │
│    - SHA256                         │
│    - Timestamp                      │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 6. Regenerate shell scripts         │
│    - Inject shell_code from config  │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 7. Generate README.md               │
│    - Tool table                     │
│    - Statistics                     │
└──────────────────────────────────────┘
```

### Asset Matching Algorithm

**Problem:** GitHub releases have different naming conventions

**Examples:**
- `fzf-0.66.1-linux_amd64.tar.gz`
- `bat-v0.26.0-x86_64-unknown-linux-musl.tar.gz`
- `ripgrep-15.1.0-x86_64-unknown-linux-musl.tar.gz`

**dotbins Matching Strategy:**
1. Try exact match for platform string
2. Try common variations (x86_64, amd64, linux-amd64, etc.)
3. Use heuristics to find best match
4. Prefer musl over glibc (more portable)

---

## Data Flow

### Initial Setup Flow

```
User                    Local Machine            GitHub
 │                           │                      │
 ├─ git clone ──────────────▶│                      │
 │                           ├─ Clone repo ────────▶│
 │                           │◀─ Get pointers ──────┤
 │                           │                      │
 ├─ git lfs pull ───────────▶│                      │
 │                           ├─ Get binaries ───────▶│
 │                           │◀─ Download ──────────┤
 │                           │                      │
 ├─ source shell/bash.sh ───▶│                      │
 │                           ├─ Modify PATH         │
 │                           │                      │
 ├─ fzf ────────────────────▶│                      │
 │                           ├─ Execute binary      │
 │◀─ Output ─────────────────┤                      │
```

### Update Flow

```
User                    Local Machine            GitHub
 │                           │                      │
 ├─ dotbins sync ───────────▶│                      │
 │                           ├─ Read dotbins.yaml   │
 │                           │                      │
 │                           ├─ Check versions ────▶│
 │                           │◀─ Latest versions ───┤
 │                           │                      │
 │                           ├─ Download new ───────▶│
 │                           │◀─ Get binaries ──────┤
 │                           │                      │
 │                           ├─ Update manifest     │
 │                           ├─ Generate README     │
 │                           │                      │
 ├─ git add/commit/push ────▶│                      │
 │                           ├─ Push changes ───────▶│
 │◀─ Done ────────────────────┤                      │
```

---

## Storage Architecture

### Current Architecture (Git LFS)

```
┌─────────────────────────────────────────────────┐
│              GitHub Repository                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  Regular Git Storage (~1MB):                    │
│  ├── dotbins.yaml                              │
│  ├── manifest.json                             │
│  ├── shell/*.sh                                │
│  └── */bin/* (LFS pointers only)               │
│                                                 │
│  Git LFS Storage (~580MB):                      │
│  ├── linux/amd64/bin/* (actual binaries)       │
│  ├── linux/arm64/bin/* (actual binaries)       │
│  └── macos/arm64/bin/* (actual binaries)       │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Storage Costs:**
- Free tier: 1GB storage + 1GB/month bandwidth
- After: $5/month per 50GB
- **Current usage: 580MB (58% of free tier)**

**Problems:**
1. Will exceed free tier with more tools
2. Bandwidth costs when multiple users sync
3. Full binary downloads on every update
4. Can't scale to team usage

---

## Future Architecture

### Proposed URL-Based Architecture

```
┌─────────────────────────────────────────────────┐
│              GitHub Repository                   │
│              (Regular Git Only)                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  Storage (~100KB):                              │
│  ├── dotbins.yaml                              │
│  ├── manifest.json (with URLs)                 │
│  ├── metadata/ (tool descriptions)             │
│  ├── shell/*.sh                                │
│  └── scripts/                                  │
│      ├── install.sh                            │
│      ├── update.sh                             │
│      └── helpers/                              │
│                                                 │
└─────────────────────────────────────────────────┘
                    │
                    │ Downloads from
                    ↓
┌─────────────────────────────────────────────────┐
│              GitHub Releases                     │
│              (Original Projects)                 │
├─────────────────────────────────────────────────┤
│  junegunn/fzf/releases/download/v0.66.1/...    │
│  sharkdp/bat/releases/download/v0.26.0/...     │
│  ... (each tool's original release)             │
└─────────────────────────────────────────────────┘
                    │
                    │ Cached locally
                    ↓
┌─────────────────────────────────────────────────┐
│           User's Local Machine                   │
├─────────────────────────────────────────────────┤
│  ~/.local/dotbins/                              │
│  ├── cache/                                     │
│  │   ├── fzf-0.66.1-linux_amd64.tar.gz         │
│  │   └── bat-0.26.0-linux_amd64.tar.gz         │
│  ├── bin/                                       │
│  │   ├── fzf (extracted)                        │
│  │   └── bat (extracted)                        │
│  └── state.json (what's installed)              │
└─────────────────────────────────────────────────┘
```

**Benefits:**
1. **Zero LFS costs** - No binaries in Git
2. **Smaller repository** - ~100KB vs 580MB
3. **Faster clones** - Download metadata only
4. **On-demand downloads** - Get what you need
5. **Local caching** - Don't redownload unchanged tools
6. **Scalable** - Works for any number of users/tools

**Implementation Plan:**
1. Create download scripts
2. Modify manifest to store URLs instead of binaries
3. Build local cache management
4. Add verification (SHA256)
5. Migrate existing users
6. Remove binaries from Git history

---

## Conclusion

The current architecture is functional but has scaling limitations due to Git LFS costs. The proposed URL-based architecture solves this while maintaining all benefits of version control and cross-machine sync.

**Current State:**
- ✅ Works well for personal use
- ✅ Multi-platform support
- ✅ Version tracking
- ❌ LFS costs will accumulate
- ❌ Large repository size

**Future State:**
- ✅ No storage costs
- ✅ Smaller repository
- ✅ Faster operations
- ✅ Better scalability
- ✅ Same functionality

---

**Last Updated:** November 4, 2025
