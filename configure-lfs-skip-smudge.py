#!/usr/bin/env python3
"""Configure Git LFS to keep only the current platform's binaries.

This helper does two things:

1. Enables `lfs.fetchinclude` for the detected platform/arch and sets
   `lfs.fetchexclude` for the other supported targets so future pulls stay lean.
2. Optionally performs a one-off cleanup that removes previously downloaded
   binaries for the excluded platforms and prunes the local LFS cache.

It is safe to rerun; settings are idempotent and cleanup is optional.

Usage:
    python3 configure-lfs-skip-smudge.py

This script will:
- Detect your current platform (e.g., linux/amd64)
- Configure Git LFS to only fetch binaries for your platform
- Optionally clean up binaries for other platforms to save disk space
- Show useful Git LFS commands for your reference

Example:
    $ python3 configure-lfs-skip-smudge.py
    Detected platform: linux/amd64
    
    Configuration updated
      lfs.fetchinclude = linux/amd64/**
      lfs.fetchexclude = linux/arm64/**, macos/arm64/**
    
    Run cleanup to drop already-downloaded binaries for other platforms? [y/N] y
    Cleanup finished. This clone now only stores binaries for this platform.
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


# Supported platform/architecture combinations
# Format: "{os}/{architecture}"
SUPPORTED_TARGETS = (
    "linux/amd64",   # Most Linux servers and desktops (x86_64)
    "linux/arm64",   # ARM Linux (Raspberry Pi, ARM servers)
    "macos/arm64",   # Apple Silicon Macs (M1/M2/M3)
)


class CommandError(RuntimeError):
    """Raised when a shell command fails."""

    pass


def run(
    cmd: list[str], *, env: dict[str, str] | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Run a command, pretty printing the invocation.
    
    Args:
        cmd: Command and arguments as a list (e.g., ['git', 'status'])
        env: Optional environment variables to set
        check: If True, raise CommandError on non-zero exit code
        
    Returns:
        CompletedProcess object with returncode, stdout, stderr
        
    Raises:
        CommandError: If check=True and command fails
        
    Example:
        run(['git', 'status'])
        run(['git', 'config', 'lfs.fetchinclude', 'linux/**'], check=True)
    """
    print(f"→ {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env, check=False)
    if check and result.returncode != 0:
        raise CommandError(f"command failed: {' '.join(cmd)}")
    return result


def ensure_tool(name: str) -> None:
    """Ensure a required tool is available on PATH.
    
    Args:
        name: Name of the tool to check (e.g., 'git', 'git-lfs')
        
    Raises:
        SystemExit: If tool is not found on PATH
        
    Example:
        ensure_tool('git')
        ensure_tool('git-lfs')
    """
    if shutil.which(name) is None:
        raise SystemExit(f"{name} is required but not on PATH")


def repo_root() -> Path:
    """Get the root directory of the Git repository.
    
    Returns:
        Path object pointing to the repository root
        
    Raises:
        SystemExit: If not run from inside a Git repository
        
    Example:
        root = repo_root()  # Returns Path('/home/user/.dotbins')
    """
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("Run this script from inside the repository")
    return Path(result.stdout.strip())


def git_config_get_all(key: str) -> list[str]:
    """Get all values for a Git configuration key.
    
    Git allows multiple values for the same key (e.g., multiple fetchexclude patterns).
    This function returns all of them.
    
    Args:
        key: Git config key (e.g., 'lfs.fetchexclude')
        
    Returns:
        List of values for the key, or empty list if key doesn't exist
        
    Example:
        excludes = git_config_get_all('lfs.fetchexclude')
        # Returns: ['linux/arm64/**', 'macos/arm64/**']
    """
    result = subprocess.run(
        ["git", "config", "--local", "--get-all", key],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def unset_value(key: str, value: str) -> None:
    """Remove a specific value from a Git configuration key.
    
    Args:
        key: Git config key (e.g., 'lfs.fetchexclude')
        value: Specific value to remove
        
    Example:
        unset_value('lfs.fetchexclude', 'linux/arm64/**')
    """
    # Escape special regex characters in the value
    regex = re.escape(value)
    run(["git", "config", "--local", "--unset-all", key, regex], check=False)


def detect_target() -> str:
    """Detect the current platform and architecture.
    
    Returns:
        Platform string in format "os/arch" (e.g., "linux/amd64")
        
    Raises:
        SystemExit: If the OS or architecture is not supported
        
    Supported platforms:
        - linux/amd64 (x86_64 Linux)
        - linux/arm64 (ARM64 Linux)
        - macos/arm64 (Apple Silicon)
        
    Example:
        target = detect_target()  # Returns "linux/amd64" on x86_64 Linux
    """
    # Get OS name (Linux, Darwin, Windows, etc.)
    system = platform.system().lower()
    # Get CPU architecture (x86_64, aarch64, arm64, etc.)
    machine = platform.machine().lower()

    # Normalize OS names
    if system == "darwin":
        system = "macos"  # macOS reports as "Darwin"
    elif system != "linux":
        raise SystemExit(f"Unsupported OS: {system}")

    # Normalize architecture names
    if machine in {"x86_64", "amd64"}:
        arch = "amd64"
    elif machine in {"aarch64", "arm64"}:
        arch = "arm64"
    else:
        raise SystemExit(f"Unsupported architecture: {machine}")

    # Combine into platform string
    target = f"{system}/{arch}"
    
    # Verify it's a supported combination
    if target not in SUPPORTED_TARGETS:
        raise SystemExit(f"Unsupported target: {target}")
    
    return target


def configure_lfs(target: str) -> tuple[str, list[str]]:
    """Configure Git LFS to fetch only the specified platform's binaries.
    
    This function:
    1. Enables Git LFS with skip-smudge (don't auto-download all LFS files)
    2. Sets fetchinclude to download only the target platform
    3. Sets fetchexclude to skip other platforms
    
    Args:
        target: Platform string (e.g., "linux/amd64")
        
    Returns:
        Tuple of (include_pattern, exclude_directories)
        
    Example:
        include, excludes = configure_lfs("linux/amd64")
        # Returns: ("linux/amd64/**", ["linux/arm64", "macos/arm64"])
    """
    # Pattern to include: all files under the target platform
    include_pattern = f"{target}/**"
    
    # Directories to exclude: all other supported platforms
    exclude_dirs = [t for t in SUPPORTED_TARGETS if t != target]

    # Enable Git LFS with skip-smudge mode
    # This prevents automatic download of all LFS files on clone
    run(["git", "lfs", "install", "--local", "--skip-smudge"], check=True)

    # Set the include pattern (replaces any existing value)
    run(
        [
            "git",
            "config",
            "--local",
            "--replace-all",
            "lfs.fetchinclude",
            include_pattern,
        ]
    )

    # Clean up old exclude patterns that match our supported platforms
    existing_excludes = git_config_get_all("lfs.fetchexclude")
    for value in existing_excludes:
        if any(value.startswith(prefix) for prefix in SUPPORTED_TARGETS):
            unset_value("lfs.fetchexclude", value)

    # Add new exclude patterns for other platforms
    for directory in exclude_dirs:
        pattern = f"{directory}/**"
        run(
            ["git", "config", "--local", "--add", "lfs.fetchexclude", pattern],
            check=True,
        )

    return include_pattern, exclude_dirs


def prompt_cleanup() -> bool:
    """Prompt the user to confirm cleanup of other platforms' binaries.
    
    Returns:
        True if user confirms cleanup, False otherwise
        
    Example:
        if prompt_cleanup():
            # User said yes, proceed with cleanup
    """
    try:
        answer = (
            input(
                "Run cleanup to drop already-downloaded binaries for other platforms? [y/N] "
            )
            .strip()
            .lower()
        )
    except EOFError:
        # Handle piped input or Ctrl+D
        return False
    return answer in {"y", "yes"}


def cleanup(exclude_dirs: list[str]) -> None:
    """Remove binaries for other platforms and prune LFS cache.
    
    This function:
    1. Resets the working tree with GIT_LFS_SKIP_SMUDGE=1 (keeps pointer files)
    2. Removes directories for other platforms
    3. Restores pointer files for removed directories
    4. Prunes the local LFS cache to free disk space
    
    Args:
        exclude_dirs: List of platform directories to remove (e.g., ["linux/arm64", "macos/arm64"])
        
    Example:
        cleanup(["linux/arm64", "macos/arm64"])
    """
    # Set environment variable to skip LFS smudge filter
    # This means git reset will restore pointer files, not actual binaries
    env = os.environ.copy()
    env["GIT_LFS_SKIP_SMUDGE"] = "1"

    print("Resetting working tree with smudge disabled...")
    run(["git", "reset", "--hard", "HEAD"], env=env)

    # Remove the directories for other platforms
    cleaned: list[str] = []
    for directory in exclude_dirs:
        path = Path(directory)
        if path.exists():
            print(f"Removing {directory} ...")
            shutil.rmtree(path)
        cleaned.append(directory)

    # Restore pointer files for the removed directories
    # This ensures Git still tracks them, just as pointer files
    if cleaned:
        print("Restoring pointer files...")
        run(["git", "checkout", "--", *cleaned], env=env)

    # Prune the local LFS cache to free up disk space
    # --force: Don't prompt for confirmation
    # --recent=0: Prune everything not currently checked out
    print("Pruning local Git LFS cache...")
    run(["git", "lfs", "prune", "--force", "--recent=0"])


def main() -> None:
    """Main entry point for the LFS configuration script.
    
    This function:
    1. Verifies required tools are installed (git, git-lfs)
    2. Detects the current platform
    3. Configures Git LFS for platform-specific fetching
    4. Optionally cleans up binaries for other platforms
    5. Displays helpful information and commands
    
    Raises:
        SystemExit: If required tools are missing or platform is unsupported
        CommandError: If Git commands fail
    """
    # Verify required tools are available
    ensure_tool("git")
    ensure_tool("git-lfs")

    # Navigate to repository root
    root = repo_root()
    os.chdir(root)

    # Detect current platform (e.g., "linux/amd64")
    target = detect_target()
    print(f"Detected platform: {target}\n")

    # Configure Git LFS to only fetch this platform's binaries
    include_pattern, excludes = configure_lfs(target)

    # Display the configuration that was applied
    print("Configuration updated")
    print(f"  lfs.fetchinclude = {include_pattern}")
    print(f"  lfs.fetchexclude = {', '.join(f'{e}/**' for e in excludes)}\n")

    # Prompt user to clean up already-downloaded binaries
    if prompt_cleanup():
        cleanup(excludes)
        print(
            "Cleanup finished. This clone now only stores binaries for this platform.\n"
        )
    else:
        # Show manual cleanup commands if user declined
        print("Skipped cleanup. You can run it later with:")
        print("  GIT_LFS_SKIP_SMUDGE=1 git reset --hard HEAD")
        for directory in excludes:
            print(f"  rm -rf {directory}")
        print("  git lfs prune --force --recent=0\n")

    # Display useful Git LFS commands
    print("Useful commands:")
    print(f'  git lfs pull --include="{include_pattern}"')
    print(f'  git lfs checkout --include="{include_pattern}"')
    print("  git lfs ls-files")
    print()
    
    # Show how to undo these settings
    print("To undo these settings:")
    print("  git config --local --unset-all lfs.fetchinclude")
    print("  git config --local --unset-all lfs.fetchexclude")


if __name__ == "__main__":
    try:
        main()
    except CommandError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
