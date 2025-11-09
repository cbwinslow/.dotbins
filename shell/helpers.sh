#!/usr/bin/env bash
# Utility helpers to make working with dotbins-managed environments easier.

if [[ -n "${DOTBINS_HELPERS_LOADED:-}" ]]; then
    return 0
fi
export DOTBINS_HELPERS_LOADED=1

_dotbins_helpers_log() {
    local level="$1"; shift
    printf '[dotbins:%s] %s\n' "$level" "$*"
}

_dotbins_helpers_require_dotbins() {
    if ! command -v dotbins >/dev/null 2>&1; then
        _dotbins_helpers_log error "dotbins is not installed or not on PATH"
        return 1
    fi
    return 0
}

_dotbins_helpers_detect_os() {
    local os
    os=$(uname -s | tr '[:upper:]' '[:lower:]')
    [[ "$os" == "darwin" ]] && os="macos"
    printf '%s' "$os"
}

_dotbins_helpers_detect_arch() {
    local arch
    arch=$(uname -m)
    case "$arch" in
        x86_64) arch="amd64" ;;
        aarch64|arm64) arch="arm64" ;;
    esac
    printf '%s' "$arch"
}

_dotbins_helpers_bin_dir() {
    printf '%s/.dotbins/%s/%s/bin' "$HOME" "$(_dotbins_helpers_detect_os)" "$(_dotbins_helpers_detect_arch)"
}

_dotbins_helpers_run() {
    _dotbins_helpers_require_dotbins || return 1
    _dotbins_helpers_log info "running: dotbins $*"
    command dotbins "$@"
}

_dotbins_helpers_config_tools() {
    local config="$HOME/.dotbins/dotbins.yaml"
    [[ -f "$config" ]] || return 0
    awk '/^  [a-zA-Z0-9_.-]+:/ { gsub(":", "", $1); if ($1 != "tools") print $1 }' "$config" | sort -u
}

# Public helpers -----------------------------------------------------------------

dotbins_sync_all() {
    _dotbins_helpers_run sync "$@"
}


dotbins_sync_current() {
    _dotbins_helpers_run sync --current "$@"
}


dotbins_install_tools() {
    if [[ $# -eq 0 ]]; then
        _dotbins_helpers_log error "provide at least one tool name"
        return 1
    fi
    _dotbins_helpers_run sync "$@"
}


dotbins_tool_path() {
    if [[ $# -ne 1 ]]; then
        _dotbins_helpers_log error "usage: dotbins_tool_path <tool>"
        return 1
    fi
    local bin_dir="$(_dotbins_helpers_bin_dir)"
    local tool="$1"
    local candidate
    for candidate in "$bin_dir/$tool" "$bin_dir/${tool%%:*}"; do
        if [[ -x "$candidate" ]]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    _dotbins_helpers_log warn "tool '$tool' not found in $bin_dir"
    return 1
}


dotbins_show_missing() {
    local bin_dir="$(_dotbins_helpers_bin_dir)"
    local missing=()
    local tool
    while IFS= read -r tool; do
        [[ -z "$tool" ]] && continue
        [[ -x "$bin_dir/$tool" ]] || missing+=("$tool")
    done < <(_dotbins_helpers_config_tools)

    if (( ${#missing[@]} == 0 )); then
        _dotbins_helpers_log info "all configured tools are present for $(basename "$bin_dir")"
        return 0
    fi

    _dotbins_helpers_log warn "missing tools for $(basename "$bin_dir")"
    printf '%s\n' "${missing[@]}"
    return 1
}

