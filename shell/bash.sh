#!/usr/bin/env bash
# dotbins - Add platform-specific binaries to PATH
# This script detects the current OS and architecture, then adds the appropriate
# binary directory to PATH. It should be sourced in your ~/.bashrc or ~/.bash_profile

# Detect operating system (Linux, Darwin/macOS, etc.)
# Convert to lowercase for consistency
_os=$(uname -s | tr '[:upper:]' '[:lower:]')
# Normalize macOS (Darwin) to "macos" for directory naming
[[ "$_os" == "darwin" ]] && _os="macos"

# Detect CPU architecture (x86_64, aarch64, arm64, etc.)
_arch=$(uname -m)
# Normalize x86_64 to "amd64" for consistency with Go/Docker naming
[[ "$_arch" == "x86_64" ]] && _arch="amd64"
# Normalize ARM64 variants (aarch64 on Linux, arm64 on macOS) to "arm64"
[[ "$_arch" == "aarch64" || "$_arch" == "arm64" ]] && _arch="arm64"

# Add platform-specific binary directory to the front of PATH
# This ensures dotbins tools take precedence over system tools
export PATH="$HOME/.dotbins/$_os/$_arch/bin:$PATH"

helpers_file="$HOME/.dotbins/shell/helpers.sh"
if [[ -f "$helpers_file" ]]; then
    # shellcheck disable=SC1090
    source "$helpers_file"
fi

# Tool-specific configurations
# These configurations are automatically generated from dotbins.yaml
# Each section checks if the tool is available before configuring it

# Configuration for bat (cat with syntax highlighting)
# Only configure if bat is available in PATH
if command -v bat >/dev/null 2>&1; then
    # Disable paging for bat output (more convenient for short files)
    alias bat="bat --paging=never"
    # Replace cat with bat for syntax-highlighted output
    alias cat="bat --plain --paging=never"
fi

# Configuration for direnv (directory-specific environment variables)
# Enables automatic loading of .envrc files in directories
if command -v direnv >/dev/null 2>&1; then
    eval "$(direnv hook bash)"
fi

# Configuration for eza (modern ls replacement)
# Provides a convenient alias with common options
if command -v eza >/dev/null 2>&1; then
    # l = long format, all files, human-readable sizes, git status, icons
    alias l="eza -lah --git --icons"
fi

# Configuration for fzf (fuzzy finder)
# Sets up key bindings (Ctrl+R for history, Ctrl+T for files, Alt+C for cd)
if command -v fzf >/dev/null 2>&1; then
    eval "$(fzf --bash)"
fi

# Configuration for lazygit (terminal UI for git)
# Provides a short alias for quick access
if command -v lazygit >/dev/null 2>&1; then
    alias lg="lazygit"
fi

# Configuration for micromamba (fast conda alternative)
# Provides a short alias for quick access
if command -v micromamba >/dev/null 2>&1; then
    alias mm="micromamba"
fi

# Configuration for starship (cross-shell prompt)
# Initializes the starship prompt for bash
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
fi

# Configuration for zoxide (smart cd replacement)
# Sets up 'z' command for jumping to frequently used directories
if command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init bash)"
fi

# Configuration for atuin (magical shell history)
# Enables improved shell history with sync capabilities
# --disable-up-arrow preserves the default up arrow behavior
if command -v atuin >/dev/null 2>&1; then
    eval "$(atuin init bash --disable-up-arrow)"
fi

