#!/usr/bin/env python3
"""
Security Scanner for dotbins

Provides security features:
- CVE checking via GitHub Advisory Database
- Binary verification
- Security reporting

Usage:
    from security import SecurityScanner
    
    scanner = SecurityScanner()
    scanner.scan_tool('fzf', '0.66.1')
"""

import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SecurityScanner:
    """Security scanning for CLI tools."""
    
    def __init__(self):
        """Initialize the security scanner."""
        self.github_advisory_api = "https://api.github.com/advisories"
    
    def check_cve(self, package_name: str, version: str, ecosystem: str = "github-actions") -> List[Dict]:
        """
        Check for CVEs affecting a package version.
        
        Args:
            package_name: Name of the package
            version: Version to check
            ecosystem: Package ecosystem (e.g., 'npm', 'pip', 'github-actions')
            
        Returns:
            List of CVE information dictionaries
        """
        print(f"Checking for CVEs: {package_name} {version}")
        
        # Note: GitHub Advisory Database API has rate limits
        # For production use, implement caching and rate limiting
        
        try:
            # Search for advisories
            url = f"{self.github_advisory_api}?ecosystem={ecosystem}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'dotbins-security-scanner')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                # Filter for our package (simplified)
                # In practice, would need more sophisticated matching
                relevant_cves = []
                for advisory in data:
                    if package_name.lower() in advisory.get('summary', '').lower():
                        relevant_cves.append({
                            'id': advisory.get('ghsa_id'),
                            'severity': advisory.get('severity'),
                            'summary': advisory.get('summary'),
                            'url': advisory.get('html_url')
                        })
                
                return relevant_cves
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("Note: No advisories found")
                return []
            print(f"Warning: Failed to check CVEs: {e}")
            return []
        except Exception as e:
            print(f"Warning: CVE check error: {e}")
            return []
    
    def verify_binary(self, binary_path: Path, expected_sha256: Optional[str] = None) -> Tuple[bool, str]:
        """
        Verify a binary file.
        
        Args:
            binary_path: Path to binary
            expected_sha256: Expected SHA256 hash (optional)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not binary_path.exists():
            return False, "Binary file not found"
        
        # Check if it's actually a binary (not an LFS pointer)
        with open(binary_path, 'rb') as f:
            header = f.read(1024)
            if b'version https://git-lfs.github.com/spec/v1' in header:
                return False, "File is a Git LFS pointer, not actual binary"
        
        # Check if executable
        if not binary_path.stat().st_mode & 0o111:
            return False, "File is not executable"
        
        # Verify SHA256 if provided
        if expected_sha256:
            import hashlib
            sha256 = hashlib.sha256()
            with open(binary_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            
            actual = sha256.hexdigest()
            if actual != expected_sha256:
                return False, f"SHA256 mismatch: expected {expected_sha256}, got {actual}"
        
        return True, "Binary verified"
    
    def scan_binary_properties(self, binary_path: Path) -> Dict:
        """
        Scan binary properties using file command.
        
        Args:
            binary_path: Path to binary
            
        Returns:
            Dictionary of binary properties
        """
        properties = {
            'path': str(binary_path),
            'exists': binary_path.exists(),
            'size': binary_path.stat().st_size if binary_path.exists() else 0,
            'executable': binary_path.stat().st_mode & 0o111 != 0 if binary_path.exists() else False
        }
        
        try:
            # Get file type
            result = subprocess.run(
                ['file', str(binary_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                properties['file_type'] = result.stdout.strip()
        except Exception as e:
            properties['file_type'] = f"Error: {e}"
        
        return properties
    
    def generate_security_report(self, tools: List[Dict]) -> Dict:
        """
        Generate a security report for a list of tools.
        
        Args:
            tools: List of tool information dictionaries
            
        Returns:
            Security report dictionary
        """
        report = {
            'scanned_at': self._current_timestamp(),
            'tools_scanned': len(tools),
            'issues_found': 0,
            'tools': []
        }
        
        for tool in tools:
            tool_report = {
                'name': tool['name'],
                'version': tool.get('version', 'unknown'),
                'issues': []
            }
            
            # Verify binary if path provided
            if 'path' in tool:
                valid, message = self.verify_binary(
                    Path(tool['path']),
                    tool.get('sha256')
                )
                if not valid:
                    tool_report['issues'].append({
                        'type': 'verification',
                        'severity': 'high',
                        'message': message
                    })
            
            # Check for CVEs (placeholder - would need better implementation)
            # CVE checking for CLI tools is complex as they're not in standard
            # package ecosystems. Would need to:
            # 1. Map tool name to GitHub repo
            # 2. Check GitHub Security Advisories for that repo
            # 3. Check if current version is affected
            
            if tool_report['issues']:
                report['issues_found'] += len(tool_report['issues'])
            
            report['tools'].append(tool_report)
        
        return report
    
    def _current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


def main():
    """Command-line interface."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='Security scanner for dotbins tools'
    )
    parser.add_argument('command', choices=['scan', 'verify', 'check-cve'],
                        help='Command to execute')
    parser.add_argument('--tool', help='Tool name')
    parser.add_argument('--version', help='Tool version')
    parser.add_argument('--path', help='Path to binary')
    parser.add_argument('--sha256', help='Expected SHA256 hash')
    
    args = parser.parse_args()
    
    scanner = SecurityScanner()
    
    if args.command == 'verify':
        if not args.path:
            print("Error: --path required for verify command")
            sys.exit(1)
        
        valid, message = scanner.verify_binary(
            Path(args.path),
            args.sha256
        )
        
        if valid:
            print(f"✓ {message}")
            sys.exit(0)
        else:
            print(f"✗ {message}")
            sys.exit(1)
    
    elif args.command == 'check-cve':
        if not args.tool or not args.version:
            print("Error: --tool and --version required for check-cve command")
            sys.exit(1)
        
        cves = scanner.check_cve(args.tool, args.version)
        
        if cves:
            print(f"\nFound {len(cves)} potential CVEs:")
            for cve in cves:
                print(f"\n  {cve['id']} - {cve['severity']}")
                print(f"  {cve['summary']}")
                print(f"  {cve['url']}")
        else:
            print("\n✓ No known CVEs found")
    
    elif args.command == 'scan':
        print("Security scanning not fully implemented yet")
        print("Use 'verify' or 'check-cve' commands instead")


if __name__ == '__main__':
    main()
