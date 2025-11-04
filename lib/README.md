# dotbins Library

Python library for full-featured dotbins tool management.

## Overview

This library provides the core functionality for the dotbins management system, implementing URL-based downloads, version management, security scanning, and AI integration.

## Modules

### downloader.py

URL-based binary downloader that eliminates Git LFS costs.

**Features:**
- Download binaries from GitHub releases
- Local caching in `~/.cache/dotbins`
- SHA256 verification
- Archive extraction (tar.gz, zip, etc.)
- Platform detection
- Incremental updates

**Usage:**
```python
from downloader import BinaryDownloader

downloader = BinaryDownloader()
downloader.sync_tool('fzf', 'linux', 'amd64')
```

**CLI:**
```bash
python3 lib/downloader.py sync fzf
python3 lib/downloader.py sync --current
python3 lib/downloader.py clean
```

### manager.py

High-level tool management interface.

**Features:**
- Install/uninstall tools
- Version pinning
- Backup/restore state
- Profile export/import
- Installation verification
- Configuration validation

**Usage:**
```python
from manager import ToolManager

manager = ToolManager()
manager.install_tool('fzf')
manager.pin_version('fzf', '0.66.1')
manager.export_profile('profile.json')
```

**CLI:**
```bash
python3 lib/manager.py list
python3 lib/manager.py install fzf
python3 lib/manager.py verify
```

### security.py

Security scanning and verification.

**Features:**
- CVE checking via GitHub Advisory Database
- Binary verification
- SHA256 validation
- LFS pointer detection
- Security reporting

**Usage:**
```python
from security import SecurityScanner

scanner = SecurityScanner()
valid, msg = scanner.verify_binary('/path/to/binary', expected_sha256)
cves = scanner.check_cve('fzf', '0.66.1')
```

**CLI:**
```bash
python3 lib/security.py verify --path /path/to/binary --sha256 abc123
python3 lib/security.py check-cve --tool fzf --version 0.66.1
```

### openrouter/

AI integration via OpenRouter SDK.

See [openrouter/README.md](openrouter/README.md) for details.

## Installation

The library is already included in your dotbins repository. No separate installation needed.

### Dependencies

**Core (no dependencies):**
- Python 3.8+
- Standard library only

**Optional:**
- `PyYAML` - For better YAML parsing in config validation
- `requests` - For enhanced HTTP handling (uses urllib by default)

## Architecture

```
lib/
├── __init__.py          # Package initialization
├── downloader.py        # URL-based downloads
├── manager.py           # High-level management
├── security.py          # Security features
├── openrouter/          # AI integration
│   ├── __init__.py
│   ├── openrouter.py
│   └── README.md
└── README.md           # This file
```

## Data Flow

```
User Command
    ↓
scripts/dotbins-manager (CLI)
    ↓
lib/manager.py (High-level logic)
    ↓
lib/downloader.py (Downloads)
    ↓
lib/security.py (Verification)
    ↓
Binary installed in ~/.dotbins/[platform]/[arch]/bin/
```

## Storage

### Local Cache (`~/.cache/dotbins/`)

```
~/.cache/dotbins/
├── fzf-0.66.1-linux_amd64.tar.gz    # Downloaded archives
├── bat-0.26.0-linux_amd64.tar.gz
├── ...
└── state.json                        # Installation state
```

### Repository (`~/.dotbins/`)

```
~/.dotbins/
├── manifest.json          # Tool metadata with URLs
├── .pins.json            # Version pins (optional)
├── .backup_*.json        # Backups (optional)
└── [platform]/[arch]/bin/  # Installed binaries
```

## API Reference

### BinaryDownloader

```python
class BinaryDownloader:
    def __init__(self, dotbins_dir=None, cache_dir=None)
    def load_manifest() -> Dict
    def sync_tool(tool_name, platform, arch, force=False) -> bool
    def sync_all(current_platform_only=False, force=False) -> Dict[str, bool]
    def download_file(url, dest_path, expected_sha256=None) -> bool
    def extract_binary(archive_path, binary_path, dest_path) -> bool
    def clean_cache(keep_current=True)
```

### ToolManager

```python
class ToolManager:
    def __init__(self, dotbins_dir=None)
    def list_installed() -> List[Dict]
    def list_available() -> List[Dict]
    def install_tool(tool_name, version=None, platform=None, arch=None, force=False) -> bool
    def uninstall_tool(tool_name, platform=None, arch=None) -> bool
    def pin_version(tool_name, version)
    def unpin_version(tool_name)
    def verify_installation(tool_name=None) -> Dict[str, bool]
    def validate_config() -> Tuple[bool, List[str]]
    def export_profile(output_file)
    def import_profile(input_file, force=False)
    def create_backup() -> str
    def restore_backup(backup_file)
```

### SecurityScanner

```python
class SecurityScanner:
    def __init__(self)
    def check_cve(package_name, version, ecosystem="github-actions") -> List[Dict]
    def verify_binary(binary_path, expected_sha256=None) -> Tuple[bool, str]
    def scan_binary_properties(binary_path) -> Dict
    def generate_security_report(tools) -> Dict
```

## Examples

### Download and Install a Tool

```python
from lib import BinaryDownloader

downloader = BinaryDownloader()
success = downloader.sync_tool('fzf', 'linux', 'amd64')

if success:
    print("Tool installed successfully")
```

### Manage Tool Versions

```python
from lib import ToolManager

manager = ToolManager()

# Install tool
manager.install_tool('fzf')

# Pin to specific version
manager.pin_version('fzf', '0.66.1')

# List installed
tools = manager.list_installed()
for tool in tools:
    print(f"{tool['name']} - {tool['version']}")
```

### Verify Security

```python
from lib import SecurityScanner
from pathlib import Path

scanner = SecurityScanner()

# Verify binary
binary = Path.home() / '.dotbins/linux/amd64/bin/fzf'
valid, message = scanner.verify_binary(binary)

if not valid:
    print(f"Security issue: {message}")

# Check for CVEs
cves = scanner.check_cve('fzf', '0.66.1')
if cves:
    print(f"Found {len(cves)} CVEs")
```

### Export/Import Profile

```python
from lib import ToolManager

manager = ToolManager()

# On machine A
manager.export_profile('/tmp/my-setup.json')

# On machine B
manager.import_profile('/tmp/my-setup.json')
```

## Testing

```bash
# Test imports
python3 -c "from lib import ToolManager, BinaryDownloader, SecurityScanner; print('OK')"

# Test downloader
python3 lib/downloader.py status

# Test manager
python3 lib/manager.py list

# Test security
python3 lib/security.py --help
```

## Development

### Adding New Features

1. Add functionality to appropriate module
2. Update module docstring
3. Add CLI interface if needed
4. Update this README
5. Update main docs/MANAGER.md

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all public functions
- Include usage examples in docstrings

### Error Handling

- Catch specific exceptions
- Provide helpful error messages
- Return boolean success indicators
- Use tuple returns for (success, message) patterns

## Performance

### Download Optimization

- **First install:** Downloads archives as needed
- **Cache hits:** Instant from local cache
- **Updates:** Only downloads changed tools
- **Verification:** SHA256 computed once

### Memory Usage

- Streams large downloads (no full buffer)
- Extracts archives to temp directories
- Minimal memory footprint

## Security

### Download Security

1. **HTTPS only** - All downloads use HTTPS
2. **SHA256 verification** - Every binary verified
3. **Official sources** - GitHub releases only
4. **No code execution** - Binaries not run during install

### Binary Verification

```python
# Every download is verified
downloader.download_file(url, dest, expected_sha256)
# SHA256 mismatch = download fails

# Manual verification available
scanner.verify_binary(path, sha256)
```

## Troubleshooting

### Import Errors

```bash
# Check Python version
python3 --version  # Need 3.8+

# Verify files exist
ls -la lib/*.py

# Test imports
python3 -c "import sys; sys.path.insert(0, 'lib'); from manager import ToolManager"
```

### Download Failures

- Check network connectivity
- Verify manifest.json has valid URLs
- Check cache directory exists and is writable
- Try with `--force` flag

### Cache Issues

```bash
# Check cache location
ls -la ~/.cache/dotbins/

# Clean cache
python3 lib/downloader.py clean

# Remove cache entirely
rm -rf ~/.cache/dotbins/
```

## Migration from Git LFS

To migrate from Git LFS storage to URL-based:

1. **Ensure manifest has URLs:**
   ```bash
   cat manifest.json | grep '"url"'
   ```

2. **Use new downloader:**
   ```bash
   python3 lib/downloader.py sync --current
   ```

3. **Verify:**
   ```bash
   python3 lib/manager.py verify
   ```

4. **Optional - Remove LFS binaries:**
   ```bash
   # Only do this if you're confident!
   git rm [platform]/*/bin/*
   ```

## Future Enhancements

Planned features:
- Parallel downloads
- Progress bars
- Resume capability
- Custom repository support
- Binary diffing for updates
- Compression options

## Contributing

Contributions welcome! Please:
1. Follow existing code style
2. Add tests (when test infrastructure exists)
3. Update documentation
4. Test on multiple platforms

## License

Same as parent dotbins project.

---

**Version:** 1.0.0  
**Last Updated:** November 4, 2025
