# Bug Report: `tmpclaude-*-cwd` files not cleaned up on Windows

## Environment

- **Claude Code Version**: 2.1.6
- **OS**: Windows 11 (Version 10.0.26200.7462)
- **Shell**: PowerShell / Git Bash

## Description

When using the `Task` tool (subagents) in Claude Code, temporary files named `tmpclaude-{random-id}-cwd` are created in the current working directory. These files are not deleted after the subagent completes on Windows.

## Steps to Reproduce

1. Open Claude Code on Windows
2. Use the `Task` tool to spawn subagents (e.g., `/orchestrate`, `/parallel`, or direct Task tool usage)
3. After completion, check the working directory

## Expected Behavior

The `tmpclaude-*-cwd` files should be automatically deleted when the subagent process completes.

## Actual Behavior

Files remain in the directory indefinitely:

```
C:\claude\automation_sub\
├── tmpclaude-0a6e-cwd
├── tmpclaude-166f-cwd
├── tmpclaude-205e-cwd
├── tmpclaude-28ba-cwd
├── tmpclaude-4187-cwd
... (24 files total)
```

Each file contains only a path string:
```
/c/claude/automation_sub
```

## Impact

- Accumulates garbage files over time
- Clutters project directories
- May cause confusion with version control (untracked files)

## Workaround

Added cleanup hook in `.claude/hooks/session_cleanup.py` with pattern `tmpclaude-*`.

## Additional Context

- Issue appears to be Windows-specific (file locking or cleanup logic not executing)
- Files are created during subagent execution, timestamp matches Task tool usage
- All files have identical size (25 bytes) containing the cwd path

---

**GitHub Issue URL**: https://github.com/anthropics/claude-code/issues
