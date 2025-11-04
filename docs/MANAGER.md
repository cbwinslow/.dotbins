# dotbins Manager - Full Feature Management System

## Overview

The **dotbins-manager** is a comprehensive CLI tool that transforms the .dotbins repository into a full-featured management system, addressing all concerns identified in the documentation.

## Key Features

### 1. URL-Based Downloads (No Git LFS Costs)
- Download binaries on-demand from GitHub releases
- Local caching to avoid re-downloading
- SHA256 verification for security
- **Zero Git LFS storage costs**

### 2. Version Management
- Pin tools to specific versions
- Rollback to previous versions
- Track installation history
- Backup and restore state

### 3. Security Features
- Binary verification with SHA256
- CVE checking (GitHub Advisory Database)
- Security reporting
- Integrity validation

### 4. Profile Management
- Export installed tools list
- Import profile on new machines
- Cross-machine synchronization
- Platform-aware profiles

### 5. Enhanced User Experience
- Unified CLI interface
- Comprehensive validation
- Helpful error messages
- Non-interactive mode support

## Installation

The manager is already installed in your dotbins repository:

```bash
# Make sure you're in the dotbins directory
cd ~/.dotbins

# Run the manager
./scripts/dotbins-manager --help
```

For easier access, add to your PATH:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.dotbins/scripts:$PATH"

# Then reload
source ~/.bashrc

# Now you can run it directly
dotbins-manager --help
```

## Quick Start

### Sync All Tools
```bash
# Sync all tools (downloads from URLs, not Git LFS)
dotbins-manager sync

# Sync only for current platform
dotbins-manager sync --current

# Force re-download
dotbins-manager sync --force
```

### Manage Individual Tools
```bash
# Install a tool
dotbins-manager install fzf

# Install specific version (when supported)
dotbins-manager install fzf --version 0.66.1

# Uninstall a tool
dotbins-manager uninstall fzf

# List installed tools
dotbins-manager list

# List available tools
dotbins-manager list --available
```

### Version Pinning
```bash
# Pin a tool to a version (prevents updates)
dotbins-manager pin fzf 0.66.1

# Unpin to allow updates
dotbins-manager unpin fzf

# List shows pinned tools with 📌 indicator
dotbins-manager list
```

### Verification
```bash
# Verify all tools work correctly
dotbins-manager verify

# Verify specific tool
dotbins-manager verify fzf

# Validate configuration
dotbins-manager validate
```

### Profile Management
```bash
# Export current setup
dotbins-manager export my-profile.json

# Import on another machine
dotbins-manager import my-profile.json

# Force reinstall even if already installed
dotbins-manager import my-profile.json --force
```

### Backup & Restore
```bash
# Create backup before major changes
dotbins-manager backup

# Restore from backup
dotbins-manager restore .backup_20250104_120000.json
```

### Cache Management
```bash
# Clean old cached downloads (keeps current versions)
dotbins-manager clean

# Remove all cached files
dotbins-manager clean --all
```

### Security Checks
```bash
# Verify a binary's integrity
dotbins-manager security verify --path ~/.dotbins/linux/amd64/bin/fzf --sha256 abc123...

# Check for CVEs (experimental)
dotbins-manager security check-cve --tool fzf --version 0.66.1
```

### Status Information
```bash
# Show comprehensive status
dotbins-manager status
```

## Architecture

### Directory Structure

```
~/.dotbins/                    # Your dotbins repository
├── lib/                       # Library modules (new)
│   ├── downloader.py         # URL-based download system
│   ├── manager.py            # High-level management
│   ├── security.py           # Security scanning
│   └── openrouter/           # AI integration
├── scripts/
│   ├── dotbins-manager       # Main CLI tool (new)
│   ├── dotbins-verify        # Existing verification
│   ├── dotbins-info          # Existing info tool
│   └── dotbins-setup         # Existing setup
└── [platform]/[arch]/bin/    # Binary files

~/.cache/dotbins/              # Local cache (new)
├── downloads/                # Cached archives
└── state.json                # Installation state
```

### How It Works

#### Old Approach (Git LFS)
```
GitHub (LFS Storage: 580MB)
    ↓ git lfs pull
Local Machine (Full binaries stored in Git)
```
**Cost:** $5-50+/month after free tier

#### New Approach (URL-Based)
```
GitHub (Repo: ~100KB)
    ↓ manifest with URLs
Local Cache (~downloads as needed)
    ↓ extract
Binary Directory
```
**Cost:** $0

## Migration Guide

### For Existing Users

The new system is **fully compatible** with the existing setup. You can use both systems side-by-side:

1. **Keep using existing binaries** - They still work
2. **Try the new manager** - Use `dotbins-manager` for new features
3. **Gradual migration** - Move to URL-based downloads over time

### Migrating to URL-Based System

To fully migrate away from Git LFS:

1. **Ensure manifest.json has URLs:**
   ```bash
   # Check that manifest has 'url' fields
   cat manifest.json | grep -A 5 '"url"'
   ```

2. **Use the new manager:**
   ```bash
   # This downloads from URLs, not LFS
   dotbins-manager sync --current
   ```

3. **Verify everything works:**
   ```bash
   dotbins-manager verify
   ```

4. **Optional: Clean up LFS binaries** (advanced)
   ```bash
   # Remove binaries from Git (keeps in LFS history)
   # Only do this if you're sure!
   git rm [platform]/*/bin/*
   git commit -m "Migrate to URL-based downloads"
   ```

## Command Reference

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `sync` | Sync tools from manifest | `dotbins-manager sync` |
| `list` | List installed tools | `dotbins-manager list` |
| `install` | Install a tool | `dotbins-manager install fzf` |
| `uninstall` | Remove a tool | `dotbins-manager uninstall fzf` |
| `status` | Show system status | `dotbins-manager status` |

### Version Management

| Command | Description | Example |
|---------|-------------|---------|
| `pin` | Pin version | `dotbins-manager pin fzf 0.66.1` |
| `unpin` | Unpin version | `dotbins-manager unpin fzf` |
| `backup` | Create backup | `dotbins-manager backup` |
| `restore` | Restore backup | `dotbins-manager restore backup.json` |

### Verification

| Command | Description | Example |
|---------|-------------|---------|
| `verify` | Verify tools work | `dotbins-manager verify` |
| `validate` | Validate config | `dotbins-manager validate` |

### Profile Management

| Command | Description | Example |
|---------|-------------|---------|
| `export` | Export profile | `dotbins-manager export profile.json` |
| `import` | Import profile | `dotbins-manager import profile.json` |

### Maintenance

| Command | Description | Example |
|---------|-------------|---------|
| `clean` | Clean cache | `dotbins-manager clean` |
| `security verify` | Verify binary | `dotbins-manager security verify --path /path/to/bin` |
| `security check-cve` | Check CVEs | `dotbins-manager security check-cve --tool fzf --version 0.66.1` |

## Configuration

### Manifest Format

The `manifest.json` file now supports URL-based downloads:

```json
{
  "version": 2,
  "fzf/linux/amd64": {
    "tag": "v0.66.1",
    "url": "https://github.com/junegunn/fzf/releases/download/v0.66.1/fzf-0.66.1-linux_amd64.tar.gz",
    "sha256": "abc123...",
    "binary_name": "fzf",
    "path_in_archive": "fzf",
    "updated_at": "2025-11-04T12:00:00Z"
  }
}
```

### State File

The local state is stored in `~/.cache/dotbins/state.json`:

```json
{
  "fzf/linux/amd64": {
    "sha256": "abc123...",
    "url": "https://...",
    "installed_at": "2025-11-04T12:00:00Z"
  }
}
```

### Version Pins

Version pins are stored in `.pins.json` (in the dotbins directory):

```json
{
  "fzf": "0.66.1",
  "bat": "0.26.0"
}
```

## Best Practices

### 1. Regular Backups
```bash
# Before major updates
dotbins-manager backup

# Then sync
dotbins-manager sync
```

### 2. Pin Critical Tools
```bash
# Pin tools you rely on
dotbins-manager pin fzf $(fzf --version | cut -d' ' -f1)
```

### 3. Verify After Updates
```bash
# After syncing
dotbins-manager verify
```

### 4. Export Your Setup
```bash
# Save your configuration
dotbins-manager export ~/.dotfiles/dotbins-profile.json
```

### 5. Clean Cache Periodically
```bash
# Clean old downloads
dotbins-manager clean
```

## Troubleshooting

### Problem: Tool won't download

**Solution:**
```bash
# Check manifest has URL
cat manifest.json | grep -A 5 "tool-name"

# Force re-download
dotbins-manager sync tool-name --force

# Check network connectivity
curl -I https://github.com
```

### Problem: SHA256 mismatch

**Solution:**
```bash
# Remove cached file and retry
rm ~/.cache/dotbins/tool-*
dotbins-manager sync tool-name --force
```

### Problem: Binary not working

**Solution:**
```bash
# Verify the binary
dotbins-manager verify tool-name

# Check if it's executable
ls -la ~/.dotbins/[platform]/[arch]/bin/tool-name

# Re-download
dotbins-manager install tool-name --force
```

### Problem: Import fails

**Solution:**
```bash
# Check profile format
cat profile.json | python -m json.tool

# Try with force
dotbins-manager import profile.json --force
```

## Advanced Usage

### Automation

For automation (CI/CD, scripts), use `--yes` flag:

```bash
#!/bin/bash
# Automated setup script

dotbins-manager sync --current
dotbins-manager verify || exit 1
```

### Custom Cache Location

Set the cache directory via environment:

```bash
export DOTBINS_CACHE="$HOME/.local/cache/dotbins"
dotbins-manager sync
```

### Multiple Profiles

Manage different profiles for different purposes:

```bash
# Development setup
dotbins-manager export ~/.dotfiles/dev-profile.json

# Production setup (minimal)
dotbins-manager export ~/.dotfiles/prod-profile.json

# Deploy
dotbins-manager import ~/.dotfiles/prod-profile.json
```

## Performance

### Cache Benefits

- **First install:** Downloads ~200MB of archives
- **Subsequent installs:** Uses cache, instant
- **Updates:** Only downloads changed tools

### Bandwidth Savings

Compared to Git LFS:
- **Initial clone:** 100KB vs 580MB (5800x smaller)
- **Updates:** Only changed binaries vs all platforms
- **Multi-machine:** Each machine downloads only its platform

## Security Considerations

### Binary Verification

All downloads are verified with SHA256:
```bash
# Automatic during sync
dotbins-manager sync

# Manual verification
dotbins-manager security verify --path /path/to/binary --sha256 abc123...
```

### CVE Checking

Check for known vulnerabilities:
```bash
dotbins-manager security check-cve --tool fzf --version 0.66.1
```

### Trust Model

- Binaries downloaded from official GitHub releases
- SHA256 checksums prevent tampering
- Optional: verify signatures when available

## Integration with Existing dotbins

The manager works alongside the original `dotbins` command:

```bash
# Original dotbins (requires pip install dotbins)
dotbins sync

# New manager (built-in, no dependencies)
dotbins-manager sync
```

Both can coexist. The new manager provides additional features while remaining compatible.

## Future Enhancements

Planned features:
- Automatic CVE monitoring
- Tool recommendation system
- Interactive TUI
- Plugin system
- Custom tool repositories

## Contributing

To add new features:

1. **Add modules** in `lib/`
2. **Update manager** in `scripts/dotbins-manager`
3. **Add tests** (when test infrastructure exists)
4. **Update docs** in this file

## Support

For issues or questions:
- Check [USAGE.md](../docs/USAGE.md) for general usage
- Check [ARCHITECTURE.md](../docs/ARCHITECTURE.md) for technical details
- Check [ASSESSMENT.md](../docs/ASSESSMENT.md) for design decisions

## License

Same as parent dotbins project (see repository root).

---

**Version:** 1.0.0  
**Last Updated:** November 4, 2025
