# dotbins Scripts

Helper scripts for managing and enhancing your dotbins installation.

## Available Scripts

### Core Scripts

#### `dotbins-setup`
Automated setup script for new machines. Handles the complete installation process.

**Features:**
- Checks prerequisites (git, git-lfs, python)
- Clones the repository
- Configures Git LFS for your platform
- Sets up shell integration
- Installs dotbins CLI tool
- Syncs tools
- Verifies installation

**Usage:**
```bash
# Run on a new machine
curl -fsSL https://raw.githubusercontent.com/cbwinslow/.dotbins/main/scripts/dotbins-setup | bash

# Or download and run
wget https://raw.githubusercontent.com/cbwinslow/.dotbins/main/scripts/dotbins-setup
chmod +x dotbins-setup
./dotbins-setup
```

#### `dotbins-verify`
Health check and verification tool. Checks that everything is properly configured.

**Features:**
- Verifies directory structure
- Checks PATH configuration
- Tests Git LFS setup
- Validates tool binaries
- Tests tool functionality
- Checks for LFS pointer files
- Validates manifest and config files

**Usage:**
```bash
# Run verification
./scripts/dotbins-verify

# Or if scripts is in PATH
dotbins-verify
```

**Example Output:**
```
dotbins Verification Tool
=========================

═══════════════════════════════════════════════════
Checking dotbins directory
═══════════════════════════════════════════════════

✓ dotbins directory exists: /home/user/.dotbins
✓ dotbins is a git repository

═══════════════════════════════════════════════════
Summary
═══════════════════════════════════════════════════

Passed:  12
Failed:  0
Warnings: 1

✓ dotbins is properly configured!
```

#### `dotbins-info`
Information and search tool for dotbins tools.

**Features:**
- List all available tools
- Show detailed information about specific tools
- Search for tools by keyword
- Browse by category
- Show installed vs. missing tools
- Display tool descriptions and versions

**Usage:**
```bash
# List all tools
./scripts/dotbins-info list

# Get info about a specific tool
./scripts/dotbins-info info fzf

# Search for tools
./scripts/dotbins-info search "git"

# Show categories
./scripts/dotbins-info category

# Show tools in a category
./scripts/dotbins-info category "Git Tool"

# Show only installed tools
./scripts/dotbins-info installed

# Show missing tools
./scripts/dotbins-info missing
```

**Example Output:**
```bash
$ ./scripts/dotbins-info info fzf

fzf
═══════════════════════════════════════════════════

  Description: Command-line fuzzy finder
  Category: Search Tool
  Repository: https://github.com/junegunn/fzf
  Status: Installed (version: 0.66.1)
  Location: /home/user/.dotbins/linux/amd64/bin/fzf
  Available Version: v0.66.1
```

### AI-Powered Scripts

#### `ai-metadata.py`
Uses AI (OpenRouter) to generate and enhance tool metadata.

**Requirements:**
- Python 3.8+
- OpenRouter API key (free at https://openrouter.ai)
- Set `OPENROUTER_API_KEY` environment variable

**Features:**
- Generate tool descriptions automatically
- Create usage examples
- Find similar tools
- Categorize tools
- Check latest versions with web search
- Generate complete metadata files

**Usage:**
```bash
# Set API key first
export OPENROUTER_API_KEY='your_key_here'

# Generate metadata for a tool
./scripts/ai-metadata.py generate fzf

# Generate metadata for all tools
./scripts/ai-metadata.py describe-all

# Search for similar tools
./scripts/ai-metadata.py search "fuzzy finder"

# Check latest version
./scripts/ai-metadata.py version fzf
```

**Generated Metadata:**
Metadata is saved to `metadata/*.json`:
```json
{
  "name": "fzf",
  "repository": "junegunn/fzf",
  "description": "Command-line fuzzy finder for files and commands",
  "category": "Search Tool",
  "usage_examples": "...",
  "similar_tools": ["skim", "fzy", "peco"],
  "last_updated": "2025-11-04T12:00:00"
}
```

## Directory Structure

```
scripts/
├── README.md              # This file
├── dotbins-setup         # Automated setup script
├── dotbins-verify        # Verification and health check
├── dotbins-info          # Tool information and search
├── ai-metadata.py        # AI-powered metadata generator
└── helpers/              # Helper modules (future)
```

## Integration with Shell

To make scripts easily accessible, you can add them to your PATH:

### Option 1: Add to PATH

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.dotbins/scripts:$PATH"
```

Then use without path prefix:
```bash
dotbins-verify
dotbins-info list
```

### Option 2: Create Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias dotbins-verify="$HOME/.dotbins/scripts/dotbins-verify"
alias dotbins-info="$HOME/.dotbins/scripts/dotbins-info"
alias dotbins-ai="$HOME/.dotbins/scripts/ai-metadata.py"
```

### Option 3: Symlink to ~/.local/bin

```bash
mkdir -p ~/.local/bin
ln -s ~/.dotbins/scripts/dotbins-verify ~/.local/bin/
ln -s ~/.dotbins/scripts/dotbins-info ~/.local/bin/
ln -s ~/.dotbins/scripts/ai-metadata.py ~/.local/bin/dotbins-ai

# Make sure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"
```

## Common Workflows

### New Machine Setup

```bash
# 1. Run setup script
curl -fsSL https://raw.githubusercontent.com/cbwinslow/.dotbins/main/scripts/dotbins-setup | bash

# 2. Reload shell
source ~/.bashrc  # or ~/.zshrc

# 3. Verify everything works
dotbins-verify

# 4. Check what's installed
dotbins-info installed
```

### Troubleshooting

```bash
# 1. Run verification to find issues
./scripts/dotbins-verify

# 2. Check specific tool
./scripts/dotbins-info info fzf

# 3. If tool not working, check it's a binary and not LFS pointer
file ~/.dotbins/linux/amd64/bin/fzf

# 4. If it's an LFS pointer, pull files
cd ~/.dotbins
git lfs pull
```

### Adding Tool Metadata

```bash
# Generate metadata for new tool
export OPENROUTER_API_KEY='your_key'
./scripts/ai-metadata.py generate newtool

# Or generate for all tools
./scripts/ai-metadata.py describe-all
```

### Finding Tools

```bash
# Search by keyword
./scripts/dotbins-info search "file manager"

# Browse by category
./scripts/dotbins-info category "Git Tool"

# See what's missing
./scripts/dotbins-info missing
```

## Development

### Adding a New Script

1. Create script in `scripts/` directory
2. Make it executable: `chmod +x scripts/new-script`
3. Add shebang: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`
4. Document it in this README
5. Follow the existing code style (comments, error handling)

### Script Guidelines

- Use proper error handling (`set -euo pipefail` for bash)
- Provide helpful error messages
- Support `--help` flag
- Use colors for better UX (but allow NO_COLOR)
- Make scripts idempotent (safe to run multiple times)
- Test on multiple platforms (Linux, macOS)

### Testing Scripts

```bash
# Test verify script
./scripts/dotbins-verify

# Test info script
./scripts/dotbins-info list
./scripts/dotbins-info info fzf

# Test AI script (needs API key)
export OPENROUTER_API_KEY='test_key'
./scripts/ai-metadata.py search "test"
```

## Dependencies

### Bash Scripts
- **Required:** bash 4.0+
- **Optional:** jq (for JSON parsing)
- **Optional:** git-lfs (for LFS operations)

### Python Scripts
- **Required:** Python 3.8+
- **Required:** OpenRouter API key (for AI features)
- **No external packages** - uses stdlib only

## Future Enhancements

Planned features for upcoming versions:

- [ ] `dotbins-sync`: Enhanced sync with verification
- [ ] `dotbins-diff`: Compare installed vs. available versions
- [ ] `dotbins-export`: Export installed tools list
- [ ] `dotbins-import`: Import and sync from exported list
- [ ] `dotbins-backup`: Backup/restore configuration
- [ ] `dotbins-doctor`: Advanced diagnostics
- [ ] `dotbins-update`: Update dotbins itself
- [ ] Interactive TUI for tool management
- [ ] Web dashboard for tool statistics

## Contributing

Contributions welcome! Please:
1. Follow existing code style
2. Add documentation
3. Test on multiple platforms
4. Update this README

## License

MIT License - See main repository LICENSE file

## Resources

- [Main Documentation](../docs/USAGE.md)
- [Architecture Guide](../docs/ARCHITECTURE.md)
- [Assessment & Recommendations](../docs/ASSESSMENT.md)
- [OpenRouter SDK](../lib/openrouter/README.md)
