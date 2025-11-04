#!/usr/bin/env python3
"""
Tool Manager for dotbins

Provides high-level management features:
- Version pinning
- Rollback capability
- Sync verification
- Configuration validation
- Update notifications

Usage:
    from manager import ToolManager
    
    manager = ToolManager()
    manager.install_tool('fzf', version='0.66.1')
    manager.list_installed()
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from .downloader import BinaryDownloader
except ImportError:
    from downloader import BinaryDownloader


class ToolManager:
    """High-level tool management for dotbins."""
    
    def __init__(self, dotbins_dir: Optional[str] = None):
        """
        Initialize the tool manager.
        
        Args:
            dotbins_dir: Path to .dotbins directory (default: ~/.dotbins)
        """
        self.dotbins_dir = Path(dotbins_dir or os.path.expanduser('~/.dotbins'))
        self.downloader = BinaryDownloader(dotbins_dir=str(self.dotbins_dir))
        
        self.config_path = self.dotbins_dir / 'dotbins.yaml'
        self.manifest_path = self.dotbins_dir / 'manifest.json'
        self.pins_path = self.dotbins_dir / '.pins.json'
        
    def list_installed(self) -> List[Dict]:
        """
        List all installed tools.
        
        Returns:
            List of tool information dictionaries
        """
        state = self.downloader.load_state()
        manifest = self.downloader.load_manifest()
        
        tools = []
        for key, info in state.items():
            parts = key.split('/')
            if len(parts) == 3:
                tool_name, platform, arch = parts
                manifest_info = manifest.get(key, {})
                
                tools.append({
                    'name': tool_name,
                    'platform': platform,
                    'arch': arch,
                    'version': manifest_info.get('tag', 'unknown'),
                    'installed_at': info.get('installed_at', 'unknown'),
                    'pinned': self.is_pinned(tool_name)
                })
        
        return tools
    
    def list_available(self) -> List[Dict]:
        """
        List all available tools in manifest.
        
        Returns:
            List of available tool information
        """
        manifest = self.downloader.load_manifest()
        state = self.downloader.load_state()
        
        tools = []
        seen = set()
        
        for key in manifest:
            parts = key.split('/')
            if len(parts) == 3:
                tool_name, platform, arch = parts
                
                # Group by tool name
                if tool_name not in seen:
                    seen.add(tool_name)
                    
                    # Check if installed on any platform
                    installed = any(k.startswith(f"{tool_name}/") for k in state)
                    
                    tools.append({
                        'name': tool_name,
                        'installed': installed,
                        'platforms': self._get_tool_platforms(tool_name, manifest)
                    })
        
        return tools
    
    def _get_tool_platforms(self, tool_name: str, manifest: Dict) -> List[str]:
        """Get list of platforms for a tool."""
        platforms = []
        for key in manifest:
            if key.startswith(f"{tool_name}/"):
                parts = key.split('/')
                if len(parts) == 3:
                    platform_arch = f"{parts[1]}/{parts[2]}"
                    if platform_arch not in platforms:
                        platforms.append(platform_arch)
        return platforms
    
    def install_tool(self, tool_name: str, version: Optional[str] = None, 
                     platform: Optional[str] = None, arch: Optional[str] = None,
                     force: bool = False) -> bool:
        """
        Install a specific tool.
        
        Args:
            tool_name: Name of the tool
            version: Specific version to install (optional, uses latest)
            platform: Target platform (optional, uses current)
            arch: Target architecture (optional, uses current)
            force: Force reinstall
            
        Returns:
            True if successful
        """
        # Detect platform if not specified
        if not platform or not arch:
            platform, arch = self.downloader._detect_platform()
        
        # Check if version pinning requested
        if version:
            print(f"Version pinning not yet implemented for {version}")
            print("Using latest available version")
        
        # Sync the tool
        return self.downloader.sync_tool(tool_name, platform, arch, force)
    
    def uninstall_tool(self, tool_name: str, platform: Optional[str] = None, 
                       arch: Optional[str] = None) -> bool:
        """
        Uninstall a tool.
        
        Args:
            tool_name: Name of the tool
            platform: Target platform (optional, uses current)
            arch: Target architecture (optional, uses current)
            
        Returns:
            True if successful
        """
        if not platform or not arch:
            platform, arch = self.downloader._detect_platform()
        
        # Remove binary
        bin_path = self.dotbins_dir / platform / arch / 'bin' / tool_name
        if bin_path.exists():
            bin_path.unlink()
            print(f"✓ Removed {bin_path}")
        
        # Update state
        state = self.downloader.load_state()
        key = f"{tool_name}/{platform}/{arch}"
        if key in state:
            del state[key]
            self.downloader.save_state(state)
        
        return True
    
    def pin_version(self, tool_name: str, version: str):
        """
        Pin a tool to a specific version.
        
        Args:
            tool_name: Name of the tool
            version: Version to pin
        """
        pins = self._load_pins()
        pins[tool_name] = version
        self._save_pins(pins)
        print(f"✓ Pinned {tool_name} to version {version}")
    
    def unpin_version(self, tool_name: str):
        """
        Unpin a tool version.
        
        Args:
            tool_name: Name of the tool
        """
        pins = self._load_pins()
        if tool_name in pins:
            del pins[tool_name]
            self._save_pins(pins)
            print(f"✓ Unpinned {tool_name}")
        else:
            print(f"Tool {tool_name} is not pinned")
    
    def is_pinned(self, tool_name: str) -> bool:
        """Check if a tool version is pinned."""
        pins = self._load_pins()
        return tool_name in pins
    
    def get_pinned_version(self, tool_name: str) -> Optional[str]:
        """Get the pinned version for a tool."""
        pins = self._load_pins()
        return pins.get(tool_name)
    
    def _load_pins(self) -> Dict:
        """Load version pins."""
        if not self.pins_path.exists():
            return {}
        with open(self.pins_path, 'r') as f:
            return json.load(f)
    
    def _save_pins(self, pins: Dict):
        """Save version pins."""
        with open(self.pins_path, 'w') as f:
            json.dump(pins, f, indent=2)
    
    def verify_installation(self, tool_name: Optional[str] = None) -> Dict[str, bool]:
        """
        Verify that installed tools are working.
        
        Args:
            tool_name: Specific tool to verify (optional, verifies all)
            
        Returns:
            Dictionary mapping tool names to verification status
        """
        platform, arch = self.downloader._detect_platform()
        bin_dir = self.dotbins_dir / platform / arch / 'bin'
        
        if not bin_dir.exists():
            print(f"ERROR: Binary directory does not exist: {bin_dir}")
            return {}
        
        results = {}
        
        # Get tools to verify
        if tool_name:
            tools_to_verify = [tool_name]
        else:
            tools_to_verify = [f.name for f in bin_dir.iterdir() if f.is_file()]
        
        for tool in tools_to_verify:
            bin_path = bin_dir / tool
            
            if not bin_path.exists():
                print(f"✗ {tool}: Not found")
                results[tool] = False
                continue
            
            # Check if executable
            if not os.access(bin_path, os.X_OK):
                print(f"✗ {tool}: Not executable")
                results[tool] = False
                continue
            
            # Try to run with --version
            try:
                result = subprocess.run(
                    [str(bin_path), '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"✓ {tool}: Working")
                    results[tool] = True
                else:
                    print(f"✗ {tool}: Failed (exit code {result.returncode})")
                    results[tool] = False
            except subprocess.TimeoutExpired:
                print(f"✗ {tool}: Timeout")
                results[tool] = False
            except Exception as e:
                print(f"✗ {tool}: Error - {e}")
                results[tool] = False
        
        return results
    
    def check_updates(self) -> List[Dict]:
        """
        Check which tools have updates available.
        
        Note: This currently requires the dotbins Python tool to be installed
        and will be enhanced in the future to check GitHub releases directly.
        
        Returns:
            List of tools with updates available
        """
        print("Checking for updates...")
        print("Note: Full update checking requires dotbins tool integration")
        
        # For now, just report current versions
        installed = self.list_installed()
        return []
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        Validate the dotbins.yaml configuration.
        
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        if not self.config_path.exists():
            issues.append(f"Configuration file not found: {self.config_path}")
            return False, issues
        
        try:
            # Try to load as YAML (requires PyYAML)
            try:
                import yaml
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
            except ImportError:
                print("Note: Install PyYAML for better config validation")
                # Basic validation without YAML parser
                with open(self.config_path, 'r') as f:
                    content = f.read()
                    if 'tools:' not in content:
                        issues.append("No 'tools:' section found")
                return len(issues) == 0, issues
            
            # Validate structure
            if 'tools' not in config:
                issues.append("Missing 'tools' section")
            
            if 'platforms' not in config:
                issues.append("Missing 'platforms' section")
            
            # Validate tools
            if 'tools' in config and isinstance(config['tools'], dict):
                for tool_name, tool_config in config['tools'].items():
                    if isinstance(tool_config, str):
                        # Simple form: just repo
                        if '/' not in tool_config:
                            issues.append(f"Tool '{tool_name}': Invalid repo format '{tool_config}'")
                    elif isinstance(tool_config, dict):
                        # Extended form
                        if 'repo' not in tool_config:
                            issues.append(f"Tool '{tool_name}': Missing 'repo' field")
                    else:
                        issues.append(f"Tool '{tool_name}': Invalid configuration type")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Error reading config: {e}")
            return False, issues
    
    def export_profile(self, output_file: str):
        """
        Export list of installed tools to a file.
        
        Args:
            output_file: Path to output file
        """
        installed = self.list_installed()
        
        # Get current platform
        platform, arch = self.downloader._detect_platform()
        
        profile = {
            'platform': platform,
            'arch': arch,
            'exported_at': datetime.utcnow().isoformat() + 'Z',
            'tools': [
                {
                    'name': tool['name'],
                    'version': tool['version'],
                    'pinned': tool['pinned']
                }
                for tool in installed
                if tool['platform'] == platform and tool['arch'] == arch
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(profile, f, indent=2)
        
        print(f"✓ Exported profile to {output_file}")
        print(f"  Platform: {platform}/{arch}")
        print(f"  Tools: {len(profile['tools'])}")
    
    def import_profile(self, input_file: str, force: bool = False):
        """
        Import and install tools from a profile.
        
        Args:
            input_file: Path to profile file
            force: Force reinstall even if already installed
        """
        with open(input_file, 'r') as f:
            profile = json.load(f)
        
        print(f"Importing profile from {input_file}")
        print(f"  Platform: {profile.get('platform')}/{profile.get('arch')}")
        print(f"  Exported: {profile.get('exported_at')}")
        print(f"  Tools: {len(profile.get('tools', []))}")
        
        # Get current platform
        platform, arch = self.downloader._detect_platform()
        
        # Warn if platforms don't match
        if profile.get('platform') != platform or profile.get('arch') != arch:
            print(f"\nWARNING: Profile is for {profile.get('platform')}/{profile.get('arch')}")
            print(f"         Current system is {platform}/{arch}")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Import cancelled")
                return
        
        # Install tools
        for tool in profile.get('tools', []):
            tool_name = tool['name']
            version = tool.get('version')
            pinned = tool.get('pinned', False)
            
            print(f"\nInstalling {tool_name}...")
            success = self.install_tool(tool_name, version, force=force)
            
            if success and pinned and version:
                self.pin_version(tool_name, version)
        
        print("\n✓ Profile import complete")
    
    def create_backup(self) -> str:
        """
        Create a backup of current installation state.
        
        Returns:
            Path to backup file
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_file = self.dotbins_dir / f'.backup_{timestamp}.json'
        
        backup_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'state': self.downloader.load_state(),
            'pins': self._load_pins()
        }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✓ Backup created: {backup_file}")
        return str(backup_file)
    
    def restore_backup(self, backup_file: str):
        """
        Restore from a backup file.
        
        Args:
            backup_file: Path to backup file
        """
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        print(f"Restoring from backup: {backup_file}")
        print(f"  Backup date: {backup_data.get('timestamp')}")
        
        # Restore state
        if 'state' in backup_data:
            self.downloader.save_state(backup_data['state'])
            print("✓ Restored installation state")
        
        # Restore pins
        if 'pins' in backup_data:
            self._save_pins(backup_data['pins'])
            print("✓ Restored version pins")
        
        print("\n✓ Backup restored")
        print("Note: Binaries are not restored, run sync to download them")


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Tool manager for dotbins'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List commands
    subparsers.add_parser('list', help='List installed tools')
    subparsers.add_parser('available', help='List available tools')
    
    # Install/uninstall
    install_parser = subparsers.add_parser('install', help='Install a tool')
    install_parser.add_argument('tool', help='Tool name')
    install_parser.add_argument('--version', help='Specific version')
    install_parser.add_argument('--force', action='store_true', help='Force reinstall')
    
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a tool')
    uninstall_parser.add_argument('tool', help='Tool name')
    
    # Pin/unpin
    pin_parser = subparsers.add_parser('pin', help='Pin tool version')
    pin_parser.add_argument('tool', help='Tool name')
    pin_parser.add_argument('version', help='Version to pin')
    
    unpin_parser = subparsers.add_parser('unpin', help='Unpin tool version')
    unpin_parser.add_argument('tool', help='Tool name')
    
    # Verify
    verify_parser = subparsers.add_parser('verify', help='Verify installation')
    verify_parser.add_argument('tool', nargs='?', help='Specific tool to verify')
    
    # Config
    subparsers.add_parser('validate', help='Validate configuration')
    
    # Export/import
    export_parser = subparsers.add_parser('export', help='Export profile')
    export_parser.add_argument('file', help='Output file')
    
    import_parser = subparsers.add_parser('import', help='Import profile')
    import_parser.add_argument('file', help='Input file')
    import_parser.add_argument('--force', action='store_true', help='Force reinstall')
    
    # Backup/restore
    subparsers.add_parser('backup', help='Create backup')
    restore_parser = subparsers.add_parser('restore', help='Restore backup')
    restore_parser.add_argument('file', help='Backup file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = ToolManager()
    
    # Execute command
    if args.command == 'list':
        tools = manager.list_installed()
        if not tools:
            print("No tools installed")
        else:
            print(f"Installed tools ({len(tools)}):")
            for tool in tools:
                pinned = " [PINNED]" if tool['pinned'] else ""
                print(f"  {tool['name']} - {tool['version']} ({tool['platform']}/{tool['arch']}){pinned}")
    
    elif args.command == 'available':
        tools = manager.list_available()
        print(f"Available tools ({len(tools)}):")
        for tool in tools:
            status = "✓" if tool['installed'] else " "
            platforms = ", ".join(tool['platforms'])
            print(f"  [{status}] {tool['name']} - {platforms}")
    
    elif args.command == 'install':
        success = manager.install_tool(args.tool, args.version, force=args.force)
        sys.exit(0 if success else 1)
    
    elif args.command == 'uninstall':
        manager.uninstall_tool(args.tool)
    
    elif args.command == 'pin':
        manager.pin_version(args.tool, args.version)
    
    elif args.command == 'unpin':
        manager.unpin_version(args.tool)
    
    elif args.command == 'verify':
        results = manager.verify_installation(args.tool)
        failures = [k for k, v in results.items() if not v]
        if failures:
            print(f"\nFailed tools: {', '.join(failures)}")
            sys.exit(1)
    
    elif args.command == 'validate':
        valid, issues = manager.validate_config()
        if valid:
            print("✓ Configuration is valid")
        else:
            print("✗ Configuration has issues:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
    
    elif args.command == 'export':
        manager.export_profile(args.file)
    
    elif args.command == 'import':
        manager.import_profile(args.file, args.force)
    
    elif args.command == 'backup':
        manager.create_backup()
    
    elif args.command == 'restore':
        manager.restore_backup(args.file)


if __name__ == '__main__':
    main()
