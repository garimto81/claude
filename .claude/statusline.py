# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Claude Code Status Line Script
Reads JSON status info from stdin and outputs a formatted status line.
"""
import json
import sys
import os
from pathlib import Path


def get_git_branch():
    """Get current git branch name"""
    try:
        git_dir = Path('.git')
        if git_dir.exists():
            head_file = git_dir / 'HEAD'
            if head_file.exists():
                content = head_file.read_text(encoding='utf-8').strip()
                if content.startswith('ref: refs/heads/'):
                    return content.replace('ref: refs/heads/', '')
        return "no-git"
    except Exception:
        return "unknown"


def main():
    """Main function - read JSON from stdin and print status line"""
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print("Claude Code")
            return

        data = json.loads(raw_input)

        # Try multiple possible JSON structures
        # Structure 1: {model: {display_name: ...}}
        # Structure 2: {modelName: ...}
        # Structure 3: direct fields

        model = "Claude"
        if isinstance(data.get('model'), dict):
            model = data['model'].get('display_name', 'Claude')
        elif 'modelName' in data:
            model = data['modelName']
        elif 'model' in data and isinstance(data['model'], str):
            model = data['model']

        # Working directory
        dir_name = "root"
        if isinstance(data.get('workspace'), dict):
            current_dir = data['workspace'].get('current_dir', '.')
            dir_name = os.path.basename(current_dir) or 'root'
        elif 'cwd' in data:
            dir_name = os.path.basename(data['cwd']) or 'root'
        elif 'workingDirectory' in data:
            dir_name = os.path.basename(data['workingDirectory']) or 'root'

        # Git branch
        git_branch = get_git_branch()

        # Cost info
        cost_info = ""
        cost_data = data.get('cost') or data.get('totalCost') or data.get('sessionCost')
        if cost_data:
            if isinstance(cost_data, dict):
                cost_usd = cost_data.get('total_cost') or cost_data.get('totalCost', 0)
            elif isinstance(cost_data, (int, float)):
                cost_usd = cost_data
            else:
                cost_usd = 0
            if cost_usd > 0:
                cost_info = f" | ${cost_usd:.4f}"

        # Final status line
        print(f"[{model}] {dir_name} ({git_branch}){cost_info}")

    except Exception as e:
        # Fallback
        print("Claude Code")


if __name__ == '__main__':
    main()
