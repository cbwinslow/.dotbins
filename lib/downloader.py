#!/usr/bin/env python3
"""
URL-Based Binary Downloader for dotbins

This module handles downloading binaries from URLs instead of storing them in Git LFS.
It provides caching, verification, and efficient update mechanisms.

Key Features:
- Download binaries on-demand from GitHub releases
- Local caching to avoid re-downloading
- SHA256 verification for security
- Platform-specific filtering
- Incremental updates (only changed binaries)

Usage:
    from downloader import BinaryDownloader
    
    downloader = BinaryDownloader()
    downloader.sync_tool('fzf', platform='linux', arch='amd64')
"""

import hashlib
import json
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request
import urllib.error
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BinaryDownloader:
    """Download and manage CLI tool binaries from URLs."""
    
    def __init__(self, dotbins_dir: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize the downloader.
        
        Args:
            dotbins_dir: Path to .dotbins directory (default: ~/.dotbins)
            cache_dir: Path to cache directory (default: ~/.cache/dotbins)
        """
        self.dotbins_dir = Path(dotbins_dir or os.path.expanduser('~/.dotbins'))
        self.cache_dir = Path(cache_dir or os.path.expanduser('~/.cache/dotbins'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.manifest_path = self.dotbins_dir / 'manifest.json'
        self.state_path = self.cache_dir / 'state.json'
        
    def load_manifest(self) -> Dict:
        """Load the manifest.json file."""
        if not self.manifest_path.exists():
            return {}
        with open(self.manifest_path, 'r') as f:
            return json.load(f)
    
    def load_state(self) -> Dict:
        """Load the local state (what's installed)."""
        if not self.state_path.exists():
            return {}
        with open(self.state_path, 'r') as f:
            return json.load(f)
    
    def save_state(self, state: Dict):
        """Save the local state."""
        with open(self.state_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def download_file(self, url: str, dest_path: Path, expected_sha256: Optional[str] = None) -> bool:
        """
        Download a file from URL with optional SHA256 verification.
        
        Args:
            url: URL to download from
            dest_path: Where to save the file
            expected_sha256: Expected SHA256 hash (optional)
            
        Returns:
            True if download successful and verified
        """
        print(f"Downloading: {url}")
        
        try:
            # Download to temporary file first
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)
                
                # Download with progress indication
                with urllib.request.urlopen(url, timeout=30) as response:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    chunk_size = 8192
                    
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        tmp_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}%", end='', flush=True)
                    
                    if total_size > 0:
                        print()  # New line after progress
            
            # Verify SHA256 if provided
            if expected_sha256:
                actual_sha256 = self.calculate_sha256(tmp_path)
                if actual_sha256 != expected_sha256:
                    print(f"ERROR: SHA256 mismatch!")
                    print(f"  Expected: {expected_sha256}")
                    print(f"  Got:      {actual_sha256}")
                    tmp_path.unlink()
                    return False
                print("✓ SHA256 verified")
            
            # Move to destination
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(tmp_path), str(dest_path))
            return True
            
        except urllib.error.URLError as e:
            print(f"ERROR: Failed to download: {e}")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def extract_binary(self, archive_path: Path, binary_path: str, dest_path: Path) -> bool:
        """
        Extract a binary from an archive.
        
        Args:
            archive_path: Path to the archive file
            binary_path: Path within archive (supports wildcards with *)
            dest_path: Where to save the extracted binary
            
        Returns:
            True if extraction successful
        """
        print(f"Extracting binary...")
        
        try:
            # Handle tar.gz, tar.bz2, tar.xz
            if archive_path.suffix in ['.gz', '.bz2', '.xz'] or '.tar' in archive_path.name:
                return self._extract_from_tar(archive_path, binary_path, dest_path)
            
            # Handle zip
            elif archive_path.suffix == '.zip':
                return self._extract_from_zip(archive_path, binary_path, dest_path)
            
            # Handle raw binary (no archive)
            else:
                shutil.copy(archive_path, dest_path)
                dest_path.chmod(0o755)
                return True
                
        except Exception as e:
            print(f"ERROR: Failed to extract: {e}")
            return False
    
    def _extract_from_tar(self, archive_path: Path, binary_path: str, dest_path: Path) -> bool:
        """Extract from tar archive."""
        with tarfile.open(archive_path, 'r:*') as tar:
            # Find matching file
            for member in tar.getmembers():
                if self._path_matches(member.name, binary_path):
                    print(f"  Found: {member.name}")
                    
                    # Extract to temporary location
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tar.extract(member, tmpdir)
                        extracted = Path(tmpdir) / member.name
                        
                        # Move to destination
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(extracted, dest_path)
                        dest_path.chmod(0o755)
                        return True
            
            print(f"ERROR: Binary not found in archive: {binary_path}")
            return False
    
    def _extract_from_zip(self, archive_path: Path, binary_path: str, dest_path: Path) -> bool:
        """Extract from zip archive."""
        with zipfile.ZipFile(archive_path, 'r') as zf:
            # Find matching file
            for member in zf.namelist():
                if self._path_matches(member, binary_path):
                    print(f"  Found: {member}")
                    
                    # Extract to temporary location
                    with tempfile.TemporaryDirectory() as tmpdir:
                        zf.extract(member, tmpdir)
                        extracted = Path(tmpdir) / member
                        
                        # Move to destination
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(extracted, dest_path)
                        dest_path.chmod(0o755)
                        return True
            
            print(f"ERROR: Binary not found in archive: {binary_path}")
            return False
    
    def _path_matches(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern (supports * wildcard)."""
        if '*' not in pattern:
            return path.endswith(pattern)
        
        # Simple wildcard matching
        parts = pattern.split('*')
        if len(parts) == 2:
            return path.startswith(parts[0]) and path.endswith(parts[1])
        
        # For more complex patterns, just check if pattern parts are in path
        return all(part in path for part in parts if part)
    
    def sync_tool(self, tool_name: str, platform: str, arch: str, force: bool = False) -> bool:
        """
        Sync a single tool for a specific platform.
        
        Args:
            tool_name: Name of the tool (e.g., 'fzf')
            platform: Operating system (e.g., 'linux', 'macos')
            arch: Architecture (e.g., 'amd64', 'arm64')
            force: Force re-download even if up-to-date
            
        Returns:
            True if sync successful
        """
        print(f"\n=== Syncing {tool_name} ({platform}/{arch}) ===")
        
        # Load manifest
        manifest = self.load_manifest()
        key = f"{tool_name}/{platform}/{arch}"
        
        if key not in manifest:
            print(f"ERROR: No manifest entry for {key}")
            return False
        
        entry = manifest[key]
        url = entry.get('url')
        sha256 = entry.get('sha256')
        binary_name = entry.get('binary_name', tool_name)
        path_in_archive = entry.get('path_in_archive', binary_name)
        
        if not url:
            print(f"ERROR: No URL in manifest for {key}")
            return False
        
        # Check if already up-to-date
        state = self.load_state()
        if not force and key in state:
            if state[key].get('sha256') == sha256:
                print("✓ Already up-to-date")
                return True
        
        # Determine cache file name
        cache_filename = f"{tool_name}-{entry.get('tag', 'latest')}-{platform}-{arch}"
        if url.endswith('.tar.gz'):
            cache_filename += '.tar.gz'
        elif url.endswith('.tar.bz2'):
            cache_filename += '.tar.bz2'
        elif url.endswith('.tar.xz'):
            cache_filename += '.tar.xz'
        elif url.endswith('.zip'):
            cache_filename += '.zip'
        
        cache_file = self.cache_dir / cache_filename
        
        # Download if not cached or force
        if force or not cache_file.exists():
            if not self.download_file(url, cache_file, sha256):
                return False
        else:
            print(f"✓ Using cached file: {cache_file.name}")
            # Verify cached file
            if sha256:
                actual = self.calculate_sha256(cache_file)
                if actual != sha256:
                    print("WARNING: Cached file SHA256 mismatch, re-downloading...")
                    if not self.download_file(url, cache_file, sha256):
                        return False
        
        # Extract to binary location
        bin_dir = self.dotbins_dir / platform / arch / 'bin'
        bin_dir.mkdir(parents=True, exist_ok=True)
        bin_path = bin_dir / binary_name
        
        if not self.extract_binary(cache_file, path_in_archive, bin_path):
            return False
        
        print(f"✓ Installed to: {bin_path}")
        
        # Update state
        state[key] = {
            'sha256': sha256,
            'url': url,
            'installed_at': self._current_timestamp()
        }
        self.save_state(state)
        
        return True
    
    def sync_all(self, current_platform_only: bool = False, force: bool = False) -> Dict[str, bool]:
        """
        Sync all tools from manifest.
        
        Args:
            current_platform_only: Only sync for current platform
            force: Force re-download all
            
        Returns:
            Dictionary mapping tool keys to success status
        """
        manifest = self.load_manifest()
        results = {}
        
        # Detect current platform if needed
        if current_platform_only:
            platform, arch = self._detect_platform()
            print(f"Syncing for current platform: {platform}/{arch}")
        
        for key in manifest:
            parts = key.split('/')
            if len(parts) != 3:
                continue
            
            tool_name, platform, arch = parts
            
            # Skip if not current platform
            if current_platform_only:
                curr_platform, curr_arch = self._detect_platform()
                if platform != curr_platform or arch != curr_arch:
                    continue
            
            success = self.sync_tool(tool_name, platform, arch, force)
            results[key] = success
        
        return results
    
    def _detect_platform(self) -> Tuple[str, str]:
        """Detect current platform and architecture."""
        import platform
        
        os_name = platform.system().lower()
        if os_name == 'darwin':
            os_name = 'macos'
        
        machine = platform.machine().lower()
        if machine == 'x86_64':
            arch = 'amd64'
        elif machine in ['aarch64', 'arm64']:
            arch = 'arm64'
        else:
            arch = machine
        
        return os_name, arch
    
    def _current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    def clean_cache(self, keep_current: bool = True):
        """
        Clean up cached downloads.
        
        Args:
            keep_current: Keep files for currently installed versions
        """
        if not self.cache_dir.exists():
            return
        
        state = self.load_state()
        current_urls = {entry.get('url') for entry in state.values()}
        
        for cache_file in self.cache_dir.iterdir():
            if cache_file.is_file() and cache_file.suffix in ['.gz', '.bz2', '.xz', '.zip']:
                # Check if this is for a current installation
                # This is simplified - in practice, would need better tracking
                if not keep_current or not any(url and cache_file.name in url for url in current_urls):
                    print(f"Removing: {cache_file.name}")
                    cache_file.unlink()


def main():
    """Command-line interface for the downloader."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download and manage dotbins binaries from URLs'
    )
    parser.add_argument('command', choices=['sync', 'clean', 'status'],
                        help='Command to execute')
    parser.add_argument('tool', nargs='?', help='Specific tool to sync')
    parser.add_argument('--current', action='store_true',
                        help='Only sync current platform')
    parser.add_argument('--force', action='store_true',
                        help='Force re-download')
    
    args = parser.parse_args()
    
    downloader = BinaryDownloader()
    
    if args.command == 'sync':
        if args.tool:
            platform, arch = downloader._detect_platform()
            success = downloader.sync_tool(args.tool, platform, arch, args.force)
            sys.exit(0 if success else 1)
        else:
            results = downloader.sync_all(args.current, args.force)
            failures = [k for k, v in results.items() if not v]
            if failures:
                print(f"\nFailed: {', '.join(failures)}")
                sys.exit(1)
            else:
                print("\n✓ All tools synced successfully")
                sys.exit(0)
    
    elif args.command == 'clean':
        downloader.clean_cache()
        print("✓ Cache cleaned")
    
    elif args.command == 'status':
        state = downloader.load_state()
        if not state:
            print("No tools installed")
        else:
            print(f"Installed tools: {len(state)}")
            for key, info in state.items():
                print(f"  {key} - installed {info.get('installed_at', 'unknown')}")


if __name__ == '__main__':
    main()
