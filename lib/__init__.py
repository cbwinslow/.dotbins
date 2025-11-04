"""
dotbins Library

Full-featured tool management system for dotbins.

Modules:
- downloader: URL-based binary downloader with caching
- manager: High-level tool management interface
- security: Security scanning and verification

Note: The openrouter module is available separately in lib/openrouter/

Usage:
    from dotbins import ToolManager
    
    manager = ToolManager()
    manager.sync_all()
"""

__version__ = "1.0.0"

from .downloader import BinaryDownloader
from .manager import ToolManager
from .security import SecurityScanner

__all__ = [
    'BinaryDownloader',
    'ToolManager',
    'SecurityScanner',
]
