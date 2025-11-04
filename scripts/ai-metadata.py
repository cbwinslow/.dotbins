#!/usr/bin/env python3
"""
AI-Powered Tool Metadata Generator
===================================

This script uses AI (via OpenRouter) to automatically generate and enhance
metadata for CLI tools in the dotbins repository.

Features:
- Generate descriptions for tools
- Find download URLs and latest versions
- Search for similar tools
- Check security advisories
- Generate usage examples

Usage:
    export OPENROUTER_API_KEY='your_key'
    python scripts/ai-metadata.py generate fzf
    python scripts/ai-metadata.py describe-all
    python scripts/ai-metadata.py search "fuzzy finder"
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

# Add lib directory to path
script_dir = Path(__file__).parent
lib_dir = script_dir.parent / "lib"
sys.path.insert(0, str(lib_dir))

try:
    from openrouter import OpenRouterClient, web_search_chat
except ImportError:
    print("Error: OpenRouter SDK not found.")
    print("Make sure lib/openrouter is in the correct location.")
    sys.exit(1)


class MetadataGenerator:
    """Generate and manage tool metadata using AI."""
    
    def __init__(self, dotbins_dir: Optional[str] = None):
        """Initialize metadata generator.
        
        Args:
            dotbins_dir: Path to dotbins directory (default: ~/.dotbins)
        """
        self.dotbins_dir = Path(dotbins_dir or os.path.expanduser("~/.dotbins"))
        self.manifest_path = self.dotbins_dir / "manifest.json"
        self.config_path = self.dotbins_dir / "dotbins.yaml"
        self.metadata_dir = self.dotbins_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Initialize OpenRouter client
        try:
            self.client = OpenRouterClient(
                default_model="google/gemini-flash-1.5-8b"  # Free model
            )
        except ValueError as e:
            print(f"Error: {e}")
            print("\nSet your OpenRouter API key:")
            print("  export OPENROUTER_API_KEY='your_key'")
            print("\nGet a free key from: https://openrouter.ai")
            sys.exit(1)
    
    def load_manifest(self) -> Dict[str, Any]:
        """Load manifest.json."""
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                return json.load(f)
        return {}
    
    def load_config(self) -> str:
        """Load dotbins.yaml."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return f.read()
        return ""
    
    def get_tool_repo(self, tool_name: str) -> Optional[str]:
        """Extract tool repository from config.
        
        Args:
            tool_name: Name of the tool (e.g., "fzf")
            
        Returns:
            Repository in format "user/repo" or None
        """
        config = self.load_config()
        
        # Simple YAML parsing (good enough for our use)
        for line in config.split('\n'):
            if line.strip().startswith(f"{tool_name}:"):
                # Simple format: tool: user/repo
                parts = line.split(':', 1)
                if len(parts) > 1:
                    repo = parts[1].strip().strip('"').strip("'")
                    if '/' in repo:
                        return repo
            elif line.strip().startswith("repo:") and tool_name in config:
                # Extended format: repo: user/repo
                parts = line.split(':', 1)
                if len(parts) > 1:
                    repo = parts[1].strip().strip('"').strip("'")
                    if '/' in repo:
                        return repo
        
        return None
    
    def generate_description(self, tool_name: str) -> str:
        """Generate a concise description for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            One-line description
        """
        repo = self.get_tool_repo(tool_name)
        
        prompt = f"""Generate a concise, single-line description (max 80 characters) for this CLI tool:

Tool name: {tool_name}
GitHub repo: {repo if repo else 'unknown'}

The description should:
- Explain what the tool does
- Be under 80 characters
- Be clear and actionable
- Start with a verb or noun

Example format: "Fast fuzzy finder for command line" or "Modern replacement for ls with colors"

Return only the description, nothing else."""
        
        try:
            description = self.client.chat(prompt, temperature=0.3)
            # Clean up the response
            description = description.strip().strip('"').strip("'")
            # Ensure it's one line
            description = description.split('\n')[0]
            return description[:80]  # Truncate if too long
        except Exception as e:
            print(f"Error generating description: {e}")
            return f"CLI tool: {tool_name}"
    
    def generate_usage_example(self, tool_name: str) -> str:
        """Generate usage examples for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Usage examples as markdown
        """
        repo = self.get_tool_repo(tool_name)
        
        prompt = f"""Generate 3 common usage examples for this CLI tool:

Tool: {tool_name}
Repository: {repo if repo else 'unknown'}

Format as markdown code blocks with brief descriptions:

Example:
```bash
# Description of what this does
{tool_name} [arguments]
```

Keep it practical and useful. Focus on the most common use cases."""
        
        try:
            examples = self.client.chat(prompt, temperature=0.5)
            return examples.strip()
        except Exception as e:
            print(f"Error generating examples: {e}")
            return f"# Usage\n\n```bash\n{tool_name} --help\n```"
    
    def find_similar_tools(self, description: str) -> List[str]:
        """Find similar tools based on description.
        
        Args:
            description: Tool description or search query
            
        Returns:
            List of similar tool names/suggestions
        """
        prompt = f"""Find 3-5 similar or alternative CLI tools to:

{description}

Return only the tool names, one per line, no explanations.
Focus on popular, well-maintained tools."""
        
        try:
            response = self.client.chat(prompt, temperature=0.3, web_search=True)
            # Parse tool names from response
            tools = [line.strip() for line in response.split('\n') if line.strip()]
            return tools[:5]  # Max 5 tools
        except Exception as e:
            print(f"Error finding similar tools: {e}")
            return []
    
    def check_latest_version(self, tool_name: str) -> str:
        """Check latest version of a tool using web search.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Latest version string
        """
        repo = self.get_tool_repo(tool_name)
        
        query = f"What is the latest stable version of {tool_name}"
        if repo:
            query += f" from GitHub repository {repo}"
        query += "? Return only the version number."
        
        try:
            version = self.client.chat(query, temperature=0.1, web_search=True)
            # Clean up version string
            version = version.strip().strip('v').strip()
            # Extract version pattern (x.y.z)
            import re
            match = re.search(r'\d+\.\d+\.\d+', version)
            if match:
                return match.group(0)
            return version
        except Exception as e:
            print(f"Error checking version: {e}")
            return "unknown"
    
    def generate_full_metadata(self, tool_name: str) -> Dict[str, Any]:
        """Generate complete metadata for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with all metadata
        """
        print(f"Generating metadata for {tool_name}...")
        
        repo = self.get_tool_repo(tool_name)
        
        metadata = {
            "name": tool_name,
            "repository": repo,
            "description": "",
            "category": "",
            "usage_examples": "",
            "similar_tools": [],
            "last_updated": "",
        }
        
        # Generate description
        print("  - Generating description...")
        metadata["description"] = self.generate_description(tool_name)
        
        # Generate usage examples
        print("  - Generating usage examples...")
        metadata["usage_examples"] = self.generate_usage_example(tool_name)
        
        # Find similar tools
        print("  - Finding similar tools...")
        metadata["similar_tools"] = self.find_similar_tools(metadata["description"])
        
        # Categorize
        print("  - Categorizing...")
        metadata["category"] = self.categorize_tool(tool_name, metadata["description"])
        
        from datetime import datetime
        metadata["last_updated"] = datetime.now().isoformat()
        
        return metadata
    
    def categorize_tool(self, tool_name: str, description: str) -> str:
        """Categorize a tool based on its description.
        
        Args:
            tool_name: Name of the tool
            description: Tool description
            
        Returns:
            Category name
        """
        categories = [
            "File Manager",
            "Search Tool",
            "Git Tool",
            "System Utility",
            "Shell Enhancement",
            "Package Manager",
            "Benchmarking",
            "Development Tool",
            "File Viewer",
        ]
        
        prompt = f"""Categorize this CLI tool into ONE of these categories:

{', '.join(categories)}

Tool: {tool_name}
Description: {description}

Return only the category name, nothing else."""
        
        try:
            category = self.client.chat(prompt, temperature=0.2)
            category = category.strip()
            # Validate it's one of our categories
            if category in categories:
                return category
            # Find closest match
            for cat in categories:
                if cat.lower() in category.lower():
                    return cat
            return "Other"
        except Exception as e:
            print(f"Error categorizing: {e}")
            return "Other"
    
    def save_metadata(self, tool_name: str, metadata: Dict[str, Any]):
        """Save metadata to JSON file.
        
        Args:
            tool_name: Name of the tool
            metadata: Metadata dictionary
        """
        output_file = self.metadata_dir / f"{tool_name}.json"
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"\n✓ Metadata saved to: {output_file}")
    
    def process_tool(self, tool_name: str):
        """Process a single tool: generate and save metadata.
        
        Args:
            tool_name: Name of the tool
        """
        metadata = self.generate_full_metadata(tool_name)
        self.save_metadata(tool_name, metadata)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Tool: {tool_name}")
        print(f"{'='*60}")
        print(f"Description: {metadata['description']}")
        print(f"Category: {metadata['category']}")
        print(f"Repository: {metadata['repository']}")
        if metadata['similar_tools']:
            print(f"Similar tools: {', '.join(metadata['similar_tools'])}")
        print(f"{'='*60}\n")
    
    def process_all_tools(self):
        """Process all tools from config."""
        config = self.load_config()
        
        # Extract tool names from YAML
        tools = []
        for line in config.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and ':' in line:
                parts = line.split(':', 1)
                tool_name = parts[0].strip()
                # Skip non-tool lines
                if tool_name in ['tools_dir', 'generate_lfs_scripts', 'platforms', 'tools', 'repo', 'shell_code', 'binary_name', 'path_in_archive']:
                    continue
                if tool_name and not tool_name.startswith('-'):
                    tools.append(tool_name)
        
        print(f"Found {len(tools)} tools to process")
        
        for i, tool in enumerate(tools, 1):
            print(f"\n[{i}/{len(tools)}] Processing {tool}...")
            try:
                self.process_tool(tool)
            except Exception as e:
                print(f"Error processing {tool}: {e}")
                continue


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered tool metadata generator for dotbins"
    )
    
    parser.add_argument(
        "command",
        choices=["generate", "describe-all", "search", "version"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "args",
        nargs="*",
        help="Additional arguments (tool name for generate, query for search)"
    )
    
    parser.add_argument(
        "--dotbins-dir",
        default=os.path.expanduser("~/.dotbins"),
        help="Path to dotbins directory (default: ~/.dotbins)"
    )
    
    args = parser.parse_args()
    
    generator = MetadataGenerator(args.dotbins_dir)
    
    if args.command == "generate":
        if not args.args:
            print("Error: Please specify a tool name")
            print("Usage: ai-metadata.py generate TOOLNAME")
            sys.exit(1)
        
        tool_name = args.args[0]
        generator.process_tool(tool_name)
    
    elif args.command == "describe-all":
        generator.process_all_tools()
    
    elif args.command == "search":
        if not args.args:
            print("Error: Please specify a search query")
            print("Usage: ai-metadata.py search 'fuzzy finder'")
            sys.exit(1)
        
        query = " ".join(args.args)
        print(f"Searching for tools matching: {query}")
        similar = generator.find_similar_tools(query)
        
        print("\nSuggested tools:")
        for tool in similar:
            print(f"  • {tool}")
    
    elif args.command == "version":
        if not args.args:
            print("Error: Please specify a tool name")
            print("Usage: ai-metadata.py version TOOLNAME")
            sys.exit(1)
        
        tool_name = args.args[0]
        version = generator.check_latest_version(tool_name)
        print(f"Latest version of {tool_name}: {version}")


if __name__ == "__main__":
    main()
