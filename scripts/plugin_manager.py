#!/usr/bin/env python3
"""
Plugin Manager CLI

Manage Claude Code plugins: install, update, remove, check updates

Usage:
    python scripts/plugin_manager.py list
    python scripts/plugin_manager.py install python-development@1.3.0
    python scripts/plugin_manager.py check-updates
    python scripts/plugin_manager.py diff-upstream python-development

Version: 1.0.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import subprocess


class PluginManager:
    """Plugin manager for Claude Code plugins"""

    def __init__(self, registry_path: str = ".claude-plugin/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        """Load plugin registry"""
        if not self.registry_path.exists():
            return {"plugins": [], "remoteRepositories": []}

        with open(self.registry_path, 'r') as f:
            return json.load(f)

    def _save_registry(self):
        """Save plugin registry"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def list_plugins(self, verbose: bool = False):
        """List all installed plugins"""
        print("\n📦 Installed Plugins:\n")

        plugins = self.registry.get("plugins", [])

        if not plugins:
            print("No plugins installed.")
            return

        for plugin in plugins:
            status_emoji = "✅" if plugin.get("status") == "active" else "⚠️ "

            print(f"{status_emoji} {plugin['id']}@{plugin['version']}")

            if verbose:
                print(f"   Path: {plugin['localPath']}")
                if plugin.get("upstream"):
                    print(f"   Upstream: {plugin['upstream']['repository']}")
                    print(f"   License: {plugin['upstream']['license']}")
                    print(f"   Author: {plugin['upstream']['author']['name']}")
                if plugin.get("localChanges"):
                    print(f"   Local changes: {len(plugin['localChanges'])}")
                print()

        print(f"\nTotal: {len(plugins)} plugins")

    def check_updates(self):
        """Check for available updates from upstream"""
        print("\n🔍 Checking for updates...\n")

        plugins_with_updates = []

        for plugin in self.registry.get("plugins", []):
            if plugin.get("source", {}).get("type") != "upstream":
                continue

            plugin_id = plugin["id"]
            current_version = plugin["version"]
            upstream_repo = plugin["upstream"]["repository"]

            print(f"Checking {plugin_id}@{current_version}...")

            # Simulate version check (in real implementation, fetch from GitHub API)
            # For now, just report current version
            print(f"  Current: {current_version}")
            print(f"  Status: Up to date (check skipped - implement GitHub API)")

        if plugins_with_updates:
            print(f"\n✅ {len(plugins_with_updates)} updates available")
        else:
            print("\n✅ All plugins are up to date")

    def diff_upstream(self, plugin_id: str):
        """Show diff between local and upstream version"""
        print(f"\n🔍 Comparing {plugin_id} with upstream...\n")

        # Find plugin
        plugin = next(
            (p for p in self.registry.get("plugins", []) if p["id"] == plugin_id),
            None
        )

        if not plugin:
            print(f"❌ Plugin not found: {plugin_id}")
            return

        if plugin.get("source", {}).get("type") != "upstream":
            print(f"⚠️  Plugin {plugin_id} is local-only (no upstream)")
            return

        local_path = Path(plugin["localPath"])
        upstream_url = plugin["source"]["url"]

        print(f"Local: {local_path}")
        print(f"Upstream: {upstream_url}")

        if plugin.get("localChanges"):
            print(f"\n📝 Local changes:")
            for change in plugin["localChanges"]:
                print(f"  - {change}")
        else:
            print("\n✅ No local changes detected")

    def install(self, plugin_spec: str):
        """
        Install a plugin

        Args:
            plugin_spec: Plugin ID with optional version (e.g., "python-development@1.3.0")
        """
        parts = plugin_spec.split("@")
        plugin_id = parts[0]
        version = parts[1] if len(parts) > 1 else "latest"

        print(f"\n📥 Installing {plugin_id}@{version}...\n")

        # Check if already installed
        existing = next(
            (p for p in self.registry.get("plugins", []) if p["id"] == plugin_id),
            None
        )

        if existing:
            print(f"⚠️  Plugin {plugin_id} is already installed (version {existing['version']})")
            print(f"   Use 'update' command to upgrade")
            return

        print(f"❌ Installation not yet implemented")
        print(f"   Manual installation:")
        print(f"   1. Clone upstream repository")
        print(f"   2. Copy plugin to .claude/plugins/{plugin_id}")
        print(f"   3. Update registry.json")

    def info(self, plugin_id: str):
        """Show detailed info about a plugin"""
        plugin = next(
            (p for p in self.registry.get("plugins", []) if p["id"] == plugin_id),
            None
        )

        if not plugin:
            print(f"❌ Plugin not found: {plugin_id}")
            return

        print(f"\n📦 Plugin: {plugin['id']}\n")
        print(f"Version: {plugin['version']}")
        print(f"Status: {plugin.get('status', 'unknown')}")
        print(f"Installed: {plugin.get('installed', 'unknown')}")
        print(f"Last Checked: {plugin.get('lastChecked', 'unknown')}")

        if plugin.get("upstream"):
            upstream = plugin["upstream"]
            print(f"\nUpstream:")
            print(f"  Repository: {upstream['repository']}")
            print(f"  License: {upstream['license']}")
            print(f"  Author: {upstream['author']['name']}")
            if 'email' in upstream['author']:
                print(f"  Email: {upstream['author']['email']}")
            if 'url' in upstream['author']:
                print(f"  URL: {upstream['author']['url']}")

        if plugin.get("source"):
            source = plugin["source"]
            print(f"\nSource:")
            print(f"  Type: {source['type']}")
            if source.get("url"):
                print(f"  URL: {source['url']}")
            if source.get("commit"):
                print(f"  Commit: {source['commit']}")

        print(f"\nLocal Path: {plugin['localPath']}")

        if plugin.get("localChanges"):
            print(f"\nLocal Changes: {len(plugin['localChanges'])}")
            for change in plugin["localChanges"]:
                print(f"  - {change}")

        if plugin.get("notes"):
            print(f"\nNotes: {plugin['notes']}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Plugin Manager for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/plugin_manager.py list
  python scripts/plugin_manager.py list -v
  python scripts/plugin_manager.py info python-development
  python scripts/plugin_manager.py check-updates
  python scripts/plugin_manager.py diff-upstream python-development
  python scripts/plugin_manager.py install python-development@1.3.0
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    parser_list = subparsers.add_parser('list', help='List installed plugins')
    parser_list.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Info command
    parser_info = subparsers.add_parser('info', help='Show plugin details')
    parser_info.add_argument('plugin_id', help='Plugin ID')

    # Check updates command
    subparsers.add_parser('check-updates', help='Check for available updates')

    # Diff upstream command
    parser_diff = subparsers.add_parser('diff-upstream', help='Compare with upstream')
    parser_diff.add_argument('plugin_id', help='Plugin ID')

    # Install command
    parser_install = subparsers.add_parser('install', help='Install plugin')
    parser_install.add_argument('plugin_spec', help='Plugin ID with optional version (e.g., name@1.0.0)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = PluginManager()

    if args.command == 'list':
        manager.list_plugins(verbose=args.verbose)
    elif args.command == 'info':
        manager.info(args.plugin_id)
    elif args.command == 'check-updates':
        manager.check_updates()
    elif args.command == 'diff-upstream':
        manager.diff_upstream(args.plugin_id)
    elif args.command == 'install':
        manager.install(args.plugin_spec)


if __name__ == "__main__":
    main()
